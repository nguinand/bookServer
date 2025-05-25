from sqlalchemy.orm import Session
from app.models.admin_log import AdminLogsModel
from app.db.db_models import AdminLogs


class AdminLogsCrud:
    def create_admin_logs(
        self, admin_log_model: AdminLogsModel, session: Session
    ) -> AdminLogsModel:
        admin_log_data = AdminLogs(**admin_log_model.model_dump(by_alias=True))
        session.add(admin_log_data)
        session.commit()
        session.refresh(admin_log_data)
        return AdminLogsModel.model_validate(admin_log_data)

    def get_admin_logs(self, admin_log_id: int, session: Session) -> AdminLogsModel:
        admin_log_record = session.query(AdminLogs).filter_by(id=admin_log_id).first()
        return AdminLogsModel.model_validate(admin_log_record)

    def update_admin_logs(
        self, admin_log_replacement: AdminLogsModel, session: Session
    ) -> None | AdminLogsModel:
        if admin_log_replacement.id is None:
            raise ValueError(
                f"Cannot replace user without an ID. {admin_log_replacement.id} - {admin_log_replacement.event_description}"
            )

        admin_log_record = (
            session.query(AdminLogs).filter_by(id=admin_log_replacement.id).first()
        )

        if not admin_log_record:
            return None

        admin_log_record.event_description = admin_log_replacement.event_description
        admin_log_record.event_type = admin_log_replacement.event_type

        session.commit()
        return AdminLogsModel.model_validate(admin_log_record)

    def delete_admin_logs(self, admin_log_id: int, session: Session) -> bool:
        admin_log = session.query(AdminLogs).filter_by(id=admin_log_id).first()
        if not admin_log:
            return False

        session.delete(admin_log)
        session.commit()
        return True

    def convert_admin_logs(
        self, admin_logs_data: AdminLogs
    ) -> AdminLogsModel:
        ...