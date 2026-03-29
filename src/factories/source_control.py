from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.services.source_control_service import SourceControlService


def get_source_control_service(
    session: AsyncSession = Depends(get_session),
) -> SourceControlService:
    return SourceControlService(session)
