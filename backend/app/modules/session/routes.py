"""Session endpoint (contract §4.7)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.session.schemas import SessionInfo
from app.modules.session.service import SessionService
from app.modules.session.utils import get_session_id

router = APIRouter(tags=["session"])
service = SessionService()


@router.get("/session", response_model=SessionInfo)
async def get_session(
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
) -> SessionInfo:
    """Report lightweight session info; the cookie is issued by the middleware."""
    return await service.get_session_info(session_id, db)
