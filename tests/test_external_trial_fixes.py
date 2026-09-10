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


def test_the_repair_path_still_drops_a_deprecated_temperature():
    exc = ProviderDenial("provider returned HTTP 400",
                         detail={"detail": "temperature is deprecated for this model"})
    retry = openai_compat._repaired_payload({"model": "m", "temperature": 0}, exc)
    assert retry == {"model": "m"}


# 2 ------------------------------------------------------------------------------------

class _Console(io.StringIO):
    """A stdout with a code page that cannot encode ✓ (GBK, as on the trial's console)."""
    encoding = "gbk"


def test_the_ok_mark_falls_back_to_ascii_where_stdout_cannot_encode_it(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdout", _Console())
    assert tui.glyph("✓", "+") == "+"
    tui.ok("written")                       # must not raise UnicodeEncodeError
    assert "+ written" in sys.stdout.getvalue()


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
