"""SkillStudio v1 unit tests: pure scoring math + skill file parsing (no DB, no LLM)."""

from advanced_memory.skills.studio.lab import judge_prompt, parse_verdict, score_verdicts
from advanced_memory.skills.studio.skillsource import parse_frontmatter, skill_headers


def test_score_perfect():
    verdicts = [
        {"fired": True, "should_fire": True},
        {"fired": False, "should_fire": False},
    ]
    scores = score_verdicts(verdicts)
    assert scores == {"precision": 1.0, "recall": 1.0}


def test_score_mixed():
    verdicts = [
        {"fired": True, "should_fire": True},
        {"fired": True, "should_fire": False},
        {"fired": False, "should_fire": True},
        {"fired": False, "should_fire": False},
    ]
    scores = score_verdicts(verdicts)
    assert scores == {"precision": 0.5, "recall": 0.5}


def test_score_empty_is_zero_not_crash():
    assert score_verdicts([]) == {"precision": 0.0, "recall": 0.0}


def test_parse_verdict():
    assert parse_verdict("FIRE") is True
    assert parse_verdict("  fire because relevant") is True
    assert parse_verdict("SKIP") is False
    assert parse_verdict("") is False
    assert parse_verdict("MAYBE") is False


def test_judge_prompt_contains_material():
    p = judge_prompt("Does X", ["A", "B"], "Do X now?")
    assert "Does X" in p and "A, B" in p and "Do X now?" in p


def test_frontmatter_parse():
    text = "---\nname: demo\ndescription: Does things\n---\n\n## A\n\nbody"
    fields, body = parse_frontmatter(text)
    assert fields["name"] == "demo"
    assert fields["description"] == "Does things"
    assert "## A" in body


def test_frontmatter_missing_is_empty():
    fields, body = parse_frontmatter("# No frontmatter\n")
    assert fields == {}
    assert "No frontmatter" in body


def test_toc_extraction():
    assert skill_headers("## A\ntext\n## B\n") == ["A", "B"]
    assert skill_headers("no headers") == []
