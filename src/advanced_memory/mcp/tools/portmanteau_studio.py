"""Portmanteau tool for SkillStudio v1: trigger lab + Q&A distiller.

PORTMANTEAU PATTERN RATIONALE: All studio operations (scenarios, lab runs,
telemetry reads, distill jobs) share the lab/distill/telemetry backends and
belong to one tool surface. Lives in the isolated skills/studio subtree so it
moves cleanly to anthropic-skills-mcp later (see docs/SKILL_STUDIO_SPEC.md).
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import BaseModel, Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response
from advanced_memory.skills.studio import distill, lab, repository
from advanced_memory.skills.studio import telemetry as _telemetry


class StudioScenarioCreate(BaseModel):
    operation: Literal["scenario_create"] = Field(..., description="Add a graded trigger scenario")
    skill_id: str = Field(..., description="Skill identifier (name, path, or catalog id)")
    prompt: str = Field(..., description="User request to judge")
    should_fire: bool = Field(True, description="Whether the skill should fire for this prompt")
    notes: str | None = Field(None, description="Why this scenario matters")


class StudioScenarioList(BaseModel):
    operation: Literal["scenario_list"] = Field(..., description="List scenarios, optionally per skill")
    skill_id: str | None = Field(None, description="Filter by skill identifier")


class StudioScenarioDelete(BaseModel):
    operation: Literal["scenario_delete"] = Field(..., description="Delete a scenario")
    scenario_id: int = Field(..., description="Scenario id")


class StudioLabRun(BaseModel):
    operation: Literal["lab_run"] = Field(..., description="Judge all scenarios for a skill")
    skill_id: str = Field(..., description="Skill identifier")
    model: str | None = Field(None, description="Judge model override (default ambient)")


class StudioLabHistory(BaseModel):
    operation: Literal["lab_history"] = Field(..., description="Past runs with scores")
    skill_id: str = Field(..., description="Skill identifier")
    limit: int = Field(10, description="Max runs")


class StudioTelemetry(BaseModel):
    operation: Literal["telemetry"] = Field(..., description="Door telemetry events")
    skill_id: str | None = Field(None, description="Filter by skill identifier")
    since: str | None = Field(None, description="ISO timestamp lower bound")
    limit: int = Field(200, description="Max events")


class StudioTelemetryCounts(BaseModel):
    operation: Literal["telemetry_counts"] = Field(..., description="Event counts per type")
    skill_id: str | None = Field(None, description="Filter by skill identifier")


class StudioDistillPreview(BaseModel):
    operation: Literal["distill_preview"] = Field(..., description="Draft a section without writing")
    skill_id: str = Field(..., description="Target skill identifier")
    source: str = Field(..., description="discussion:<n>, issue:<n>, or note:<path>")


class StudioDistillApply(BaseModel):
    operation: Literal["distill_apply"] = Field(..., description="Approved write of a distill job")
    job_id: int = Field(..., description="Distill job id")
    draft_md: str | None = Field(None, description="Edited draft (default stored draft)")


class StudioDistillJobs(BaseModel):
    operation: Literal["distill_jobs"] = Field(..., description="List distill jobs")
    state: str | None = Field(None, description="pending|approved|applied|rejected")


StudioOperation = Annotated[
    StudioScenarioCreate
    | StudioScenarioList
    | StudioScenarioDelete
    | StudioLabRun
    | StudioLabHistory
    | StudioTelemetry
    | StudioTelemetryCounts
    | StudioDistillPreview
    | StudioDistillApply
    | StudioDistillJobs,
    Field(discriminator="operation"),
]


@mcp.tool(name="adn_skillstudio")
async def adn_skillstudio(op: StudioOperation) -> dict:
    """SkillStudio v1: trigger lab (score skill descriptions) and Q&A distiller.

    Use lab_run to grade a skill's trigger against its scenario suite, then
    rewrite the description from failing scenarios and re-run. Use
    distill_preview/distill_apply to turn answered discussions, issues, or
    notes into skill sections behind approval. Telemetry shows Door usage.
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_skillstudio operation={operation}")

    try:
        if operation == "scenario_create":
            row = await repository.scenario_create(op.skill_id, op.prompt, op.should_fire, op.notes)
            return build_success_response("scenario_create", f"Scenario {row['id']} created.", scenario=row)
        if operation == "scenario_list":
            rows = await repository.scenario_list(op.skill_id)
            return build_success_response("scenario_list", f"{len(rows)} scenarios.", scenarios=rows)
        if operation == "scenario_delete":
            ok = await repository.scenario_delete(op.scenario_id)
            if not ok:
                return build_error_response(f"Scenario {op.scenario_id} not found.", error_code="NOT_FOUND")
            return build_success_response("scenario_delete", f"Scenario {op.scenario_id} deleted.")
        if operation == "lab_run":
            res = await lab.run_lab(op.skill_id, op.model)
            if not res.get("success"):
                return build_error_response(str(res.get("error")), error_code="LAB_FAILED")
            return build_success_response(
                "lab_run",
                f"{op.skill_id}: precision {res['precision']:.2f}, recall {res['recall']:.2f} ({res['model']}).",
                **{k: v for k, v in res.items() if k != "success"},
            )
        if operation == "lab_history":
            rows = await repository.run_history(op.skill_id, op.limit)
            return build_success_response("lab_history", f"{len(rows)} runs.", runs=rows)
        if operation == "telemetry":
            if not _telemetry.enabled():
                return build_success_response("telemetry", "Telemetry disabled (ADN_SKILLS_TELEMETRY=0).", events=[])
            rows = await repository.event_list(op.skill_id, op.since, op.limit)
            counts = await repository.event_counts(op.skill_id)
            return build_success_response("telemetry", f"{len(rows)} events.", events=rows, counts=counts)
        if operation == "telemetry_counts":
            counts = await repository.event_counts(op.skill_id)
            return build_success_response("telemetry_counts", "Event counts.", counts=counts)
        if operation == "distill_preview":
            res = await distill.distill_preview(op.skill_id, op.source)
            if not res.get("success"):
                return build_error_response(str(res.get("error")), error_code="DISTILL_FAILED")
            return build_success_response("distill_preview", f"Draft ready (job {res['job_id']}).", **res)
        if operation == "distill_apply":
            res = await distill.distill_apply(op.job_id, op.draft_md)
            if not res.get("success"):
                return build_error_response(str(res.get("error")), error_code="DISTILL_FAILED")
            return build_success_response("distill_apply", f"Job {op.job_id} applied (backup kept).", **res)
        if operation == "distill_jobs":
            rows = await repository.job_list(op.state)
            return build_success_response("distill_jobs", f"{len(rows)} jobs.", jobs=rows)
        return build_error_response(f"Unknown operation: {operation}", error_code="UNKNOWN_OP")
    except Exception as exc:
        logger.error(f"adn_skillstudio_error: {exc}", exc_info=True)
        return build_error_response(str(exc), error_code="STUDIO_ERROR")
