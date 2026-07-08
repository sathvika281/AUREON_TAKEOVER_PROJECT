from typing import Any

from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.conversation import Conversation, Turn
from aureon.services.supabase.client import get_supabase_client


class ConversationRepository:
    """Thin data-access wrapper around the session-scoped ``conversations``
    and ``turns`` tables. Agents and domain services call these
    domain-meaningful methods rather than ``client.table(...)`` directly,
    so tests can mock this class instead of the whole Supabase SDK, and the
    storage backend can change without touching callers.
    """

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        def _fetch() -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
            # maybe_single().execute() returns None outright (not a response
            # object with .data = None) when zero rows match, in this
            # supabase-py version.
            conv_row = (
                self._client.table("conversations")
                .select("*")
                .eq("id", conversation_id)
                .maybe_single()
                .execute()
            )
            if conv_row is None or not conv_row.data:
                return None
            turns_rows = (
                self._client.table("turns")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at")
                .execute()
            )
            return conv_row.data, turns_rows.data

        result = await run_in_threadpool(_fetch)
        if result is None:
            return None
        conv_row, turns_rows = result
        return Conversation(
            conversation_id=conv_row["id"],
            student_id=conv_row["student_id"],
            turns=[Turn(**row) for row in turns_rows],
            created_at=conv_row["created_at"],
            updated_at=conv_row["updated_at"],
        )

    async def create_conversation(self, conversation: Conversation) -> None:
        def _insert() -> None:
            self._client.table("conversations").insert(
                {
                    "id": conversation.conversation_id,
                    "student_id": conversation.student_id,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                }
            ).execute()

        await run_in_threadpool(_insert)

    async def append_turn(self, conversation_id: str, turn: Turn) -> None:
        def _insert() -> None:
            self._client.table("turns").insert(
                {
                    "conversation_id": conversation_id,
                    "role": turn.role,
                    "content": turn.content,
                    "agent_name": turn.agent_name,
                    "created_at": turn.created_at.isoformat(),
                }
            ).execute()

        await run_in_threadpool(_insert)
