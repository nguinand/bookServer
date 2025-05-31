from sqlalchemy.orm import Session

from app.db.db_models.admin_logs import AdminLogs


def get_admin_logs_by_id(id: int, session: Session) -> AdminLogs:
    return session.query(AdminLogs).filter_by(id=id).first()
