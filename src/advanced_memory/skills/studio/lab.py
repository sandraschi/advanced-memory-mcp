"""Trigger lab: score skill descriptions against graded scenario suites.

Scoring math is pure (testable without an LLM); judging goes through LLMClient.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from advanced_memory.services.llm_client import LLMClient
from advanced_memory.skills.studio import repository, skillsource

JUDGE_SYSTEM = (
    "You route user requests to skills. Answer with exactly one word: FIRE or SKIP."
)


def judge_prompt(description: str, toc: list[str], scenario: str) -> str:
    toc_txt = ", ".join(toc) if toc else "(no sections listed)"
    return (
        f"Skill description: {description or '(no description)'}\n"
        f"Skill sections: {toc_txt}\n\n"
        f"User request: {scenario}\n\n"
        "Would you load this skill for that request? FIRE or SKIP?"
    )


def parse_verdict(text: str) -> bool:
    """True = FIRE. Defaults to False on anything ambiguous."""
    t = (text or "").strip().upper()
    if t.startswith("FIRE"):
        return True
    if t.startswith("SKIP"):
        return False
    if "FIRE" in t and "SKIP" not in t:
        return True
    return False


def score_verdicts(verdicts: list[dict[str, Any]]) -> dict[str, float]:
    """Precision/recall over verdicts: {fired: bool, should_fire: bool}."""
    tp = sum(1 for v in verdicts if v.get("fired") and v.get("should_fire"))
    fp = sum(1 for v in verdicts if v.get("fired") and not v.get("should_fire"))
    fn = sum(1 for v in verdicts if not v.get("fired") and v.get("should_fire"))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {"precision": precision, "recall": recall}


async def run_lab(skill_id: str, model: str | None = None) -> dict[str, Any]:
    """Judge every scenario for a skill; persist the run; return scores."""
    try:
        skill = skillsource.load_skill(skill_id)
    except FileNotFoundError as exc:
        return {"success": False, "error": str(exc)}
    scenarios = await repository.scenario_list(skill_id)
    if not scenarios:
        return {"success": False, "error": f"No scenarios for skill '{skill_id}'. Create some first."}
    client = LLMClient(model=model) if model else LLMClient()
    used_model = getattr(client, "model", None) or getattr(client, "default_model", "") or "default"
    verdicts: list[dict[str, Any]] = []
    for sc in scenarios:
        prompt = judge_prompt(str(skill.get("description", "")), list(skill.get("toc", [])), str(sc["prompt"]))
        try:
            raw = await client.generate(prompt, system_prompt=JUDGE_SYSTEM, max_tokens=10, temperature=0.0)
        except Exception as exc:
            logger.warning(f"studio lab judge failed: {exc}")
            raw = "SKIP"
        fired = parse_verdict(raw)
        verdicts.append({
            "scenario_id": sc["id"],
            "prompt": sc["prompt"],
            "should_fire": bool(sc["should_fire"]),
            "fired": fired,
        })
    scores = score_verdicts(verdicts)
    record = await repository.run_record(
        skill_id=skill_id, model=str(used_model),
        precision=scores["precision"], recall=scores["recall"], verdicts=verdicts,
    )
    return {
        "success": True,
        "skill_id": skill_id,
        "model": str(used_model),
        "precision": scores["precision"],
        "recall": scores["recall"],
        "run_id": record["id"],
        "verdicts": verdicts,
    }
