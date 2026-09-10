"""Three defects an external trial found in v4.17 (fix/external-trial-defects).

1. Moonshot rejected every call: the compat registry sent temperature 0 to every vendor but
   MiniMax, and the repair path did not recognise "only 1 is allowed".
2. `crossaudit init` died on a Windows console with a non-UTF-8 code page at its first ✓.
3. Moonshot's China endpoint was in the catalogue and unreachable from setup.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from crossaudit.cli import tui, wizard
from crossaudit.errors import ConfigDenial, ProviderDenial
from crossaudit.providers import get_provider, openai_compat
from crossaudit.providers.specs import SPECS


# 1 ------------------------------------------------------------------------------------

def test_moonshot_sends_the_one_temperature_its_origin_accepts(monkeypatch):
    spec = SPECS["moonshot"]
    monkeypatch.setenv(spec.key_env, "provider-test-key")
    seen = {}

    def request(url, payload, headers, *, timeout):
        seen["payload"] = payload
        return {"id": "r", "choices": [{"message": {"content": "OK"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 1}}, "rid"

    monkeypatch.setattr("crossaudit.providers.openai_compat.request_json", request)
    get_provider(spec.provider)(model=spec.default_model, system="s", prompt="p",
                                key_env=spec.key_env, max_tokens=9)
    assert seen["payload"]["temperature"] == 1.0


def test_the_repair_path_reads_only_N_is_allowed_and_sends_that_N():
    exc = ProviderDenial("provider returned HTTP 400",
                         detail={"detail": "invalid temperature: only 1 is allowed"})
    retry = openai_compat._repaired_payload({"model": "m", "temperature": 0}, exc)
    assert retry == {"model": "m", "temperature": 1.0}


def test_an_only_N_mandate_about_another_field_does_not_touch_the_temperature():
    """Review round 1: the mandate must be the temperature's own, not any 'only N is
    allowed' in the body — here it is about `n`, and the temperature is left alone."""
    exc = ProviderDenial("provider returned HTTP 400",
                         detail={"detail": "temperature must be between 0 and 2; n: only 1 is allowed"})
    assert openai_compat._repaired_payload({"model": "m", "temperature": 0, "n": 2}, exc) is None


@pytest.mark.parametrize("body", [
    "temperature must be between 0 and 2, n: only 1 is allowed",
    "temperature must be between 0 and 2 (n: only 1 is allowed)",
    "temperature must be between 0 and 2;            n: only 1 is allowed",
    "n: only 1 is allowed; temperature must be between 0 and 2",
])
def test_a_mandate_about_another_field_in_any_punctuation_leaves_the_temperature(body):
    """Review round 2: proximity is not ownership. Only punctuation and space may stand
    between the word temperature and its mandate."""
    exc = ProviderDenial("provider returned HTTP 400", detail={"detail": body})
    assert openai_compat._repaired_payload({"model": "m", "temperature": 0, "n": 2}, exc) is None


def test_the_repair_path_still_drops_a_deprecated_temperature():
    exc = ProviderDenial("provider returned HTTP 400",
                         detail={"detail": "temperature is deprecated for this model"})
    retry = openai_compat._repaired_payload({"model": "m", "temperature": 0}, exc)
    assert retry == {"model": "m"}


# 2 ------------------------------------------------------------------------------------

def _gbk_console() -> io.TextIOWrapper:
    """A real encoding stream: writing a character GBK lacks raises, as on the trial's console."""
    return io.TextIOWrapper(io.BytesIO(), encoding="gbk", errors="strict", write_through=True)


def _written(stream: io.TextIOWrapper) -> str:
    stream.flush()
    return stream.buffer.getvalue().decode("gbk")


def test_the_ok_mark_falls_back_to_ascii_where_stdout_cannot_encode_it(monkeypatch):
    out = _gbk_console()
    monkeypatch.setattr(sys, "stdout", out)
    assert tui.glyph("✓", "+") == "+"
    tui.ok("written")                       # must not raise UnicodeEncodeError
    assert "+ written" in _written(out)


def test_the_whole_setup_flow_survives_a_gbk_console(monkeypatch):
    """Review round 1: ok() was fixed but the text prompt's ❯ still raised. Every glyph the
    wizard prints — banner box, arrows, prompt marks, section rules — must fall back."""
    out = _gbk_console()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt="": (print(prompt, end=""), "typed")[1])
    tui.banner("CrossAudit", "setup")
    tui.step(1, 4, "the auditor")
    tui.note("a note")
    tui.warn("a warning")
    assert tui.text("Base URL", placeholder="https://host/v1") == "typed"
    assert tui.outcome_line(0, tui.Option("a", "A", "hint"))
    text = _written(out)
    # GBK has the box-drawing characters, so the banner stays Unicode; ❯ is not in GBK
    # and became ">". What matters is that nothing raised and every prompt was printed.
    assert "> " in text and "the auditor" in text and "Base URL" in text


def test_the_menu_row_and_the_banner_subtitle_survive_a_gbk_console(monkeypatch):
    """Review round 2: the interactive menu's ❯ and the banner's subtitle rule were still
    unguarded. The row renderer is called as select() calls it; the banner with a subtitle."""
    out = _gbk_console()
    monkeypatch.setattr(sys, "stdout", out)
    row = tui.option_row(0, tui.Option("a", "Alpha", "the first"), current=True)
    print(row)
    tui.banner("CrossAudit", "a subtitle that draws the side rule")
    text = _written(out)
    assert "> 1) " in text and "Alpha" in text and "a subtitle" in text


def test_the_ok_mark_stays_unicode_where_stdout_can_encode_it(monkeypatch):
    class Utf8(io.StringIO):
        encoding = "utf-8"
    monkeypatch.setattr(sys, "stdout", Utf8())
    assert tui.glyph("✓", "+") == "✓"


# 3 ------------------------------------------------------------------------------------

def test_a_named_region_becomes_the_auditor_base_url_and_the_default_writes_none():
    assert wizard.choose_region("moonshot", "china") == "https://api.moonshot.cn/v1"
    assert wizard.choose_region("moonshot", "global") == ""        # the first endpoint: as before
    assert wizard.choose_region("openai", None) == ""              # one endpoint: nothing asked


def test_an_unknown_region_is_refused_with_the_choices_named():
    with pytest.raises(ConfigDenial) as denial:
        wizard.choose_region("moonshot", "mars")
    assert "china" in str(denial.value) and "global" in str(denial.value)


def test_init_accepts_the_region_flag(tmp_path, monkeypatch):
    """The flag reaches the wizard and the written config carries the regional origin."""
    monkeypatch.delenv("CROSSAUDIT_AUDITOR_KEY", raising=False)
    target = tmp_path / "proj"
    wizard.run(target, mode="local", auditor_vendor="moonshot", auditor_model="kimi-k2.6",
               auditor_region="china", generator_vendor="human", profile="science")
    cfg = (target / "crossaudit.yml").read_text(encoding="utf-8")
    assert "base_url: https://api.moonshot.cn/v1" in cfg


def test_the_cli_forwards_the_region_flag_to_the_wizard(tmp_path, monkeypatch):
    """Review round 1: the earlier test called wizard.run directly, so dropping the CLI
    forwarding would not have reddened anything."""
    import argparse
    import crossaudit.cli.main as main_mod
    seen = {}

    def fake_run(target, **kw):
        seen.update(kw)
        return {"config": str(tmp_path / "crossaudit.yml")}

    monkeypatch.setattr(main_mod.wizard, "run", fake_run)
    monkeypatch.setattr(main_mod, "_open_console", lambda root: {})
    args = argparse.Namespace(path=str(tmp_path), github=False, force=False, no_console=True,
                              json=False, auditor_vendor="moonshot", auditor_model="kimi-k2.6",
                              auditor_region="china", generator_vendor="human")
    assert main_mod.cmd_init(args) == 0
    assert seen["auditor_region"] == "china"
