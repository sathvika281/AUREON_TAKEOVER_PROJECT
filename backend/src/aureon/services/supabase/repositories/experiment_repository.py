from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.experiment import Experiment
from aureon.services.supabase.client import get_supabase_client


class ExperimentRepository:
    """Data-access wrapper around ``experiments`` — the Career Experiments
    catalog. Same normalized-rows shape as TrendRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_experiments(self) -> list[Experiment]:
        def _fetch() -> list[dict]:
            result = self._client.table("experiments").select("*").eq("is_active", True).execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Experiment.model_validate(row) for row in rows]

    async def get_experiment(self, experiment_id: str) -> Experiment | None:
        def _fetch() -> dict | None:
            row = self._client.table("experiments").select("*").eq("id", experiment_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Experiment.model_validate(data) if data else None
