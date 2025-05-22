from pytest import Session
from app.models.volume_info import VolumeInfoModel


# DEL
class VolumeInfoCrud:
    def create_volume_info(
        self, volume_info_model: VolumeInfoModel, session: Session
    ) -> VolumeInfoModel: ...

    def get_volume_info_by_id(self, id: int, session: Session) -> VolumeInfoModel: ...

    def update_volume_info(
        self, volume_info_replacement: VolumeInfoModel, session: Session
    ) -> None | VolumeInfoModel: ...

    def delete_volume_info(self, volume_info_id: int, session: Session) -> bool: ...
