from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.schemas.scm_connection import ScmConnection
from src.services.exceptions.source_control_exception import (
    DuplicateScmConnectionError,
    ScmConnectionNotFoundError,
)


class ScmConnectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def acreate(
        self,
        project_id: int,
        provider: str,
        owner: str,
        repo_name: str,
        app_id: str,
        installation_id: str,
        encrypted_pem: str,
    ) -> ScmConnection:
        try:
            stmt = insert(ScmConnection).values(
                project_id=project_id,
                provider=provider,
                owner=owner,
                repo_name=repo_name,
                app_id=app_id,
                installation_id=installation_id,
                encrypted_pem=encrypted_pem,
            ).returning(ScmConnection)

            result = await self.session.execute(stmt)
            return result.scalar_one()
        except IntegrityError as exc:
            raise DuplicateScmConnectionError() from exc

    async def aget_active_by_project_id(self, project_id: int) -> ScmConnection:
        stmt = select(ScmConnection).where(
            ScmConnection.project_id == project_id,
            ScmConnection.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        scm_connection = result.scalar_one_or_none()

        if scm_connection is None:
            raise ScmConnectionNotFoundError(project_id=project_id)

        return scm_connection
