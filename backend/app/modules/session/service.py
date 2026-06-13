"""Session service (M5 / §4.7) — lightweight info about a visitor's session.

There is no `sessions` table (it is deliberately omitted, see report §4.4), so
session facts are derived from the visitor's runs: when they first ran something
and how many runs they have.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.runs.models import Run
from app.modules.session.schemas import SessionInfo


class SessionService:
    async def get_session_info(self, session_id: str, db: AsyncSession) -> SessionInfo:
        """Return when this session first ran something, and its run count.

        With no runs yet, the session has effectively just started, so we report
        the current time.
        """
        stmt = select(
            func.count(Run.run_id),
            func.min(Run.created_at),
        ).where(Run.session_id == session_id)

        run_count, first_run_at = (await db.execute(stmt)).one()

        started = first_run_at or datetime.now(timezone.utc)
        return SessionInfo(session_started=started, run_count=run_count)
