"""Task definitions for ExpertLongBench.

Two things live here that are *not* in the dataset and had to be transcribed from the
paper's Appendix B:

1. the **description** of each rubric item -- the mapper prompt is built from these, and
   the dataset only carries item *names*;
2. the **task prompt** given to the model under test (Appendix B, "Model prompt" table).

Everything else (item names, ordering, the reference content) comes from the data.

T03MaterialSEG and T01LegalMDS are transcribed (T01 on 2026-09-07 for Arm 6). Adding a
task means transcribing its Appendix B rubric verbatim -- do not paraphrase, and do not
let a model write these.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RubricItem:
    """One checklist item.

    ``key`` must match the corresponding key in ``human_reference_checklist`` exactly.
    """

    key: str
    name: str
    description: str
    group: str | None = None


@dataclass(frozen=True)
class Task:
    task_id: str
    domain: str
    #: Verbatim from the paper's per-task "Model prompt" table. Given to the model under test.
    model_prompt: str
    items: tuple[RubricItem, ...] = field(default_factory=tuple)
    #: Paper's reported F1 range on this task for frontier models, for orientation only.
    paper_reference_f1: str = ""
    #: How the loop's instruction names the source material committed as RECIPE.md
    #: ("The synthesis recipe is in ..."). T03's wording is kept as the default so that
    #: every earlier arm's prompt bytes are unchanged; a task whose input is not a
    #: recipe names it here (Arm 6, T01: "case documents").
    source_noun: str = "synthesis recipe"
    #: The deliverable's noun in the same sentence ("Write your explanation to ...").
    deliverable_noun: str = "explanation"

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(item.key for item in self.items)

    def item_definitions(self) -> str:
        """The item definition block used in the mapper prompt."""
        lines = []
        for index, item in enumerate(self.items, start=1):
            label = f"{item.group} / {item.name}" if item.group else item.name
            lines.append(f"{index}. {label}: {item.description}")
        return "\n".join(lines)


T03_MATERIAL_SEG = Task(
    task_id="T03MaterialSEG",
    domain="materials science",
    # Verbatim, paper Table 12 (S-B.3.4).
    model_prompt=(
        "You are a materials science researcher. Given a synthesis recipe that includes the "
        "target material, selected precursors, and synthesis steps, your task is to justify the "
        "key decisions made in the recipe. This includes explaining the rationale behind the "
        "choice of precursors, reaction conditions, and processing steps, using relevant "
        "principles such as structural compatibility, chemical reactivity, and desired phase "
        "formation. Output the explanation rationales as a list of bullet points, where each "
        "bullet point contains complete sentences."
    ),
    paper_reference_f1="15.2 (GPT-4o) to 19.5 (Gemini-2.0-Flash), Table 2 column T3",
    # Verbatim, paper S-B.3.5.
    items=(
        RubricItem(
            key="Selection of Precursors [level] Structural Considerations",
            name="Structural Considerations",
            group="Selection of Precursors",
            description=(
                "Justify precursor selection by explaining how the precursor's structural motifs "
                "(e.g., coordination environments, lattice arrangement) influence the target phase "
                "formation."
            ),
        ),
        RubricItem(
            key="Selection of Precursors [level] Handling Precursor Reactivity",
            name="Handling Precursor Reactivity",
            group="Selection of Precursors",
            description=(
                "Justify precursor selection by explaining the impact of precursor reactivity on "
                "phase evolution."
            ),
        ),
        RubricItem(
            key="Selection of Precursors [level] Physical and Chemical Properties of Precursors",
            name="Physical and Chemical Properties of Precursors",
            group="Selection of Precursors",
            description=(
                "Justify precursor selection by addressing how precursor properties (e.g., particle "
                "size, morphology) influences reaction kinetics and product morphology."
            ),
        ),
        RubricItem(
            key="Synthesis Conditions [level] Temperature and Heating Method",
            name="Temperature and Heating Method",
            group="Synthesis Conditions",
            description=(
                "Justify the choice of synthesis temperature and heating method (e.g., based on "
                "thermodynamic considerations, reaction kinetics, heat transfer efficiency, or side "
                "reactions)."
            ),
        ),
        RubricItem(
            key="Synthesis Conditions [level] Atmosphere",
            name="Atmosphere",
            group="Synthesis Conditions",
            description=(
                "Justify the choice of synthesis atmosphere environment (e.g., based on "
                "thermodynamic considerations, reaction kinetics, or side reactions)."
            ),
        ),
        RubricItem(
            key="Synthesis Conditions [level] Duration",
            name="Duration",
            group="Synthesis Conditions",
            description=(
                "Justify the choice of synthesis duration (e.g., based on reaction kinetics, phase "
                "transformation rates, or side reactions)."
            ),
        ),
    ),
)



# T01LegalMDS — transcribed 2026-09-07 from arXiv:2506.01241v3, Appendix B.1.5 (the 26
# checklist items, "Evaluation Rubric") and Table 5 ("T1LegalMDS - Model prompt"), by
# extracting the PDF's text (pypdf 6.17) and copying it; the edits are rejoining words the
# PDF broke across lines ("tempo-\nrary" -> "temporary"), restoring the spaces the
# extraction dropped after item numbers ("1.Filing Date"), and normalising the PDF's
# typographic apostrophes to ASCII ("case\u2019s" -> "case's"; quotation marks are kept as
# \u201c \u201d). Item keys match
# `human_reference_checklist` in the release, whose names differ from the paper's
# wording for four items (the release's names are used as keys; the paper's text as
# the description). Nothing here was written by a model.
T01_LEGAL_MDS = Task(
    task_id="T01LegalMDS",
    domain="law",
    # Verbatim, paper Table 5 (B.1).
    model_prompt=(
        "Generate a clear and legally precise summary of a multiple-document legal case. Focus "
        "on capturing key facts, procedural history, and significant rulings in a way that is easy to "
        "understand. Provide enough detail to convey the case's development and outcome without "
        "being excessively long or overly detailed. These are the case documents:"
    ),
    source_noun="case documents",
    deliverable_noun="summary",
    items=(
        RubricItem(key="Filing Date", name="Filing Date", description="Filing Date"),
        RubricItem(key="Class Action or Individual Plaintiffs", name="Class Action or Individual Plaintiffs? (if applicable)",
                   description=("If there are class action plaintiffs the summary should say it's a class action; if "
                                "there are individual plaintiffs it can just describe the plaintiffs. For example, use "
                                "specific terms like \u201cThe city\u201d or \u201cThe parents\u201d rather than general "
                                "terms like \u201cThe defendant\u201d or \u201cThe plaintiffs.\u201d")),
        RubricItem(key="Cause of Action", name="Cause of Action",
                   description="e.g., a statute (e.g., 42 USC 1983) or a case (e.g., Ex Parte Young)"),
        RubricItem(key="Statutory or Constitutional Basis for the Case", name="Statutory or Constitutional Basis for the Case",
                   description=("A case can either be based on a statute or a provision of the Constitution\u2014i.e., a "
                                "case will either claim that someone violated a statute, or violated the Constitution. "
                                "For cases that have a constitutional basis, the summary should refer to the clause of "
                                "the Constitution that was allegedly violated, as well as the amendment if applicable. "
                                "For example it would say \u201cthe plaintiffs alleged violations of the Fourteenth "
                                "Amendment's Equal Protection Clause,\u201d or \u201cthe plaintiffs alleged violations "
                                "of the Commerce Clause.\u201d")),
        RubricItem(key="Remedy Sought", name="Remedy Sought", description="e.g., declaratory judgment"),
        RubricItem(key="Who are the Parties", name="Who are the parties (description, not name)?",
                   description="Who are the parties (description, not name)?"),
        RubricItem(key="Type of Counsel", name="Type of Counsel",
                   description="type of counsel contains private, legal services, ACLU, etc."),
        RubricItem(key="Consolidated Cases Noted", name="Consolidated Cases Noted (if applicable)",
                   description="Consolidated Cases Noted (if applicable)"),
        RubricItem(key="Related Cases Listed by Their Case Code Number", name="Related Cases listed by their case code number (if applicable)",
                   description="Related Cases listed by their case code number (if applicable)"),
        RubricItem(key="Note Important Filings", name="Note important filings (if applicable)",
                   description=("Note important filings including motions for temporary restraining orders or "
                                "preliminary injunctions, motions to dismiss, motions for summary judgment, etc.")),
        RubricItem(key="All Reported Opinions Cited with Shortened Bluebook Citation",
                   name="All reported opinions cited with shortened Bluebook citation (if applicable)",
                   description=("For example, the summary could write \u201c2020 WL 4218003\u201d after the paragraph in "
                                "which it discusses that opinion. The summary does not need to include the case name, "
                                "court, or date unless helpful\u2014such as when the summary cites an opinion from a "
                                "different case.")),
        RubricItem(key="First and Last name of Judge", name="First and Last Name of Judge",
                   description="Form: Judge John Smith. Find judge's first names at http://www.fjc.gov/public/home.nsf/hisj"),
        RubricItem(key="Significant Terms of Decrees", name="Significant Terms of Decrees (if applicable)",
                   description=("Significant terms means the substance of the decree or settlement. In a decree, the "
                                "judge orders the defendants to do something; in a settlement, the defendants agree to "
                                "do something. The significant terms would be what the defendants are ordered/agree to do.")),
        RubricItem(key="Dates of All Decrees", name="Dates of All Decrees (if applicable)",
                   description="Dates of All Decrees (if applicable)"),
        RubricItem(key="How Long Decrees will Last", name="How long decrees will last (if applicable)",
                   description="How long decrees will last (if applicable)"),
        RubricItem(key="Significant Terms of Settlement", name="Significant Terms of Settlement (if applicable)",
                   description="Significant Terms of Settlement (if applicable)"),
        RubricItem(key="Date of Settlement", name="Date of settlement (if applicable)",
                   description="Date of settlement (if applicable)"),
        RubricItem(key="How Long Settlement will Last", name="How long settlement will last (if applicable)",
                   description="How long settlement will last (if applicable)"),
        RubricItem(key="Whether the Settlement is Court-enforced or Not", name="Whether the settlement is court-enforced or not (if applicable)",
                   description="Whether the settlement is court-enforced or not (if applicable)"),
        RubricItem(key="Name of the Monitor", name="Was there a monitor? Note the name of the monitor (if applicable)",
                   description="Was there a monitor? Note the name of the monitor (if applicable)"),
        RubricItem(key="Monitor Reports", name="Monitor's Reports (if applicable)",
                   description=("A monitor's report explains whether a defendant is complying with a court order, so "
                                "people want to know which terms of the order are being complied with. For example, "
                                "from this case: In February 2016, the monitor filed her first semi-annual report. The "
                                "report stated that the payment to the plaintiffs and plaintiffs counsel was made; the "
                                "requirement of hiring ADA Coordinators was nearly compliant; videophone installation "
                                "is apparently compliant; free access to videophone, provision of qualified "
                                "interpreters for unscheduled medical emergencies, and provision of qualified "
                                "interpreters for disciplinary hearings were unclear; informational materials were "
                                "partially compliant; the routine and situational reporting were difficult or "
                                "partially noncompliant; and training was noncompliant.")),
        RubricItem(key="Appeal", name="Appeal (if applicable)", description="Appeal (if applicable)"),
        RubricItem(key="Trials", name="Trials (if applicable)", description="Trials (if applicable)"),
        RubricItem(key="Court Rulings", name="Court rulings on any of the important filings (if applicable)",
                   description=("This category corresponds with the \u201cimportant filings\u201d category\u2014so "
                                "whenever an important filing is mentioned, people also want to know what the ruling "
                                "on that filing was (if there is one)\u2014e.g., whether the judge granted or denied a "
                                "motion to dismiss. Generally these filings would be: Motions to dismiss, Motions for "
                                "summary judgment, Motions for a preliminary injunction or temporary restraining "
                                "order, Motions for class certification, Motions for attorneys' fees, Amended "
                                "complaints\u2013these won't have rulings, so they should be in the \u201cimportant "
                                "filings\u201d category but not the \u201crulings on to important filings\u201d category, "
                                "statements of interest\u2013similar to above, there won't be rulings on these.")),
        RubricItem(key="Factual Basis of Case", name="Factual basis of case",
                   description=("Refers to the facts or evidence upon which the case is built. These facts are "
                                "essential in the legal process and are used to support legal claims or decisions. It "
                                "typically includes: 1. Details of the relevant events\u2014For example, what happened, "
                                "when it happened, where it happened, and who was involved. 2. Evidence \u2013 Physical "
                                "evidence, documentary records, witness testimonies, etc., that support these facts. "
                                "3. Background information\u2014Context or explanatory facts that provide additional "
                                "understanding. In legal proceedings, the factual basis is crucial for determining the "
                                "outcome of a case, as the judge or jury makes decisions based on the facts and the "
                                "applicable legal principles.")),
        RubricItem(key="Disputes Over Settlement Enforcement", name="Disputes over settlement enforcement (if applicable)",
                   description="Disputes over settlement enforcement (if applicable)"),
    ),
)


TASKS: dict[str, Task] = {T03_MATERIAL_SEG.task_id: T03_MATERIAL_SEG,
                          T01_LEGAL_MDS.task_id: T01_LEGAL_MDS}


def get_task(task_id: str) -> Task:
    if task_id not in TASKS:
        raise KeyError(
            f"{task_id} has no transcribed rubric yet. Available: {sorted(TASKS)}. "
            "Add it by transcribing its Appendix B 'Evaluation Rubric' and 'Model prompt' "
            "tables verbatim into tasks.py."
        )
    return TASKS[task_id]
