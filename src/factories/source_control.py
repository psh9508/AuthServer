from src.services.source_control_service import SourceControlService


def get_source_control_service() -> SourceControlService:
    return SourceControlService()
