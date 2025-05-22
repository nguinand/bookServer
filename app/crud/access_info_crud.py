from pytest import Session
from app.models.access_info import AccessInfoModel


class AccessInfoCrud:
    def create_Access_info(
        self, Access_info_model: AccessInfoModel, session: Session
    ) -> AccessInfoModel: ...

    def get_Access_info_by_id(self, id: int, session: Session) -> AccessInfoModel: ...

    def update_Access_info(
        self, Access_info_replacement: AccessInfoModel, session: Session
    ) -> None | AccessInfoModel: ...

    def delete_Access_info(self, Access_info_id: int, session: Session) -> bool: ...
