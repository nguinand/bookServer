from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.db.db_models import AdminLogs
from app.models.admin_log import AdminLogsModel


def create_admin_logs(admin_log_model: AdminLogsModel, session: Session) -> AdminLogs:
    admin_log_data = AdminLogs(**admin_log_model.model_dump(by_alias=True))
    session.add(admin_log_data)
    db_manager.commit_or_raise(session)
    session.refresh(admin_log_data)
    return admin_log_data


def get_admin_logs_by_id(admin_log_id: int, session: Session) -> AdminLogs | None:
    return session.get(AdminLogs, admin_log_id)


def get_admin_logs(
    start_time: datetime,
    end_time: datetime,
    limit: int,
    offset: int,
    session: Session,
) -> tuple[list[AdminLogs], int]:
    filters = (
        AdminLogs.created_at >= start_time,
        AdminLogs.created_at <= end_time,
    )
    logs_stmt = (
        select(AdminLogs)
        .where(*filters)
        .order_by(AdminLogs.created_at.desc(), AdminLogs.id.desc())
        .limit(limit)
        .offset(offset)
    )
    total_stmt = select(func.count()).select_from(AdminLogs).where(*filters)

    admin_logs = list(session.scalars(logs_stmt).all())
    total = session.scalar(total_stmt)
    return admin_logs, total or 0


def update_admin_logs(
    admin_log_replacement: AdminLogsModel, session: Session
) -> None | AdminLogs:
    if admin_log_replacement.id is None:
        raise ValueError(
            f"Cannot replace user without an ID. {admin_log_replacement.id} - {admin_log_replacement.event_description}"
        )

    admin_log_record = get_admin_logs_by_id(admin_log_replacement.id, session)

    if not admin_log_record:
        return None

    admin_log_record.event_description = admin_log_replacement.event_description
    admin_log_record.event_type = admin_log_replacement.event_type

    db_manager.commit_or_raise(session)
    return admin_log_record


def delete_admin_logs(admin_log_id: int, session: Session) -> bool:
    admin_log = get_admin_logs_by_id(admin_log_id, session)
    if not admin_log:
        return False

    session.delete(admin_log)
    db_manager.commit_or_raise(session)
    return True


def convert_admin_logs(admin_logs_model: AdminLogs) -> AdminLogsModel:
    return AdminLogsModel.model_validate(admin_logs_model)
