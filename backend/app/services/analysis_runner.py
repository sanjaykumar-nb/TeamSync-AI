"""Run the multi-agent analysis and persist the result.

Both callers go through here: the Run Analysis button, and the GitHub webhook
when a push or pull request has actually moved work on the board. Keeping one
implementation matters more than it sounds — the persistence tail (which
columns the dashboard reads, what happens to a failed run) is exactly the kind
of thing that drifts when two endpoints each keep their own copy.

Synchronous on purpose. The deterministic path is single- to low-double-digit
milliseconds, which is what makes triggering on every push reasonable at all.
With a language-model key configured the narration layer adds a network call on
top of that, so a webhook caller can see a slower response; GitHub allows ten
seconds, and the grounding work itself is unaffected either way.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AIServiceError
from app.models.project import Project
from app.models.risk import AgentRun
from app.services.ai_client import ai_client
from app.services.snapshot_builder import build_project_snapshot

# How a severity level shows up as the number the dashboard and workspace read.
RISK_SCORE_BY_LEVEL = {"low": 0.2, "medium": 0.45, "high": 0.7, "critical": 0.9}

DEFAULT_SCOPE = ["planning", "progress", "workload"]


async def run_analysis(
    db: AsyncSession,
    project: Project,
    *,
    trigger_type: str = "manual",
    triggered_by: UUID | None = None,
    scope: list[str] | None = None,
) -> AgentRun:
    """Analyse ``project`` and return the persisted AgentRun.

    A failed run is recorded, not raised: the row carries status ``failed`` and
    the error, so a caller can report it without the caller having to know what
    went wrong inside the AI service. ``triggered_by`` is None when nobody with
    an account caused the run, which is the case for every webhook.
    """
    snapshot = await build_project_snapshot(db, project)

    run = AgentRun(
        project_id=project.id,
        triggered_by=triggered_by,
        trigger_type=trigger_type,
        status="running",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    started = datetime.utcnow()
    try:
        result = await ai_client.analyze_project(
            project_id=project.id,
            scope=scope or DEFAULT_SCOPE,
            trigger_type=trigger_type,
            snapshot=snapshot,
        )
    except AIServiceError as e:
        run.status = "failed"
        run.error_message = str(e.detail)
        await db.commit()
        await db.refresh(run)
        return run

    analysis = result.get("result") or {}
    run.status = "completed"
    run.coordinator_output = analysis
    run.specialist_outputs = analysis.get("specialist_outputs")
    run.final_recommendations = {"items": analysis.get("merged_recommendations", [])}
    run.completed_at = datetime.utcnow()
    run.execution_time_ms = int((run.completed_at - started).total_seconds() * 1000)

    # The dashboard and workspace read these columns; without this they keep
    # showing defaults that contradict the analysis that just ran.
    risk = RISK_SCORE_BY_LEVEL.get(analysis.get("overall_risk_level"))
    if risk is not None:
        project.risk_score = risk
        project.health_score = round(1 - risk, 2)

    await db.commit()
    await db.refresh(run)
    return run
