from sqlalchemy.orm import Session
from app.db.sql_queries.admin_logs_queries import get_admin_logs_by_id
from app.models.admin_log import AdminLogsModel
from app.db.db_models import AdminLogs


class AdminLogsCrud:
    def create_admin_logs(
        self, admin_log_model: AdminLogsModel, session: Session
    ) -> AdminLogs:
        admin_log_data = AdminLogs(**admin_log_model.model_dump(by_alias=True))
        session.add(admin_log_data)
        session.commit()
        session.refresh(admin_log_data)
        return admin_log_data

    def get_admin_logs_by_id(
        self, admin_log_id: int, session: Session
    ) -> AdminLogsModel:
        return get_admin_logs_by_id(admin_log_id, session)

    def update_admin_logs(
        self, admin_log_replacement: AdminLogsModel, session: Session
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

        session.commit()
        return admin_log_record

    def delete_admin_logs(self, admin_log_id: int, session: Session) -> bool:
        admin_log = get_admin_logs_by_id(admin_log_id, session)
        if not admin_log:
            return False

        session.delete(admin_log)
        session.commit()
        return True

    def convert_admin_logs(self, admin_logs_model: AdminLogsModel) -> AdminLogsModel:
        return AdminLogsModel.model_validate(admin_logs_model)
