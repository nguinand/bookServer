from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.book_access_crud import convert_access_info, create_access_info
from app.db.db_conn import db_manager
from app.models.access_info import AccessInfoModel, CreateAccessInfoRequest

router = APIRouter()


@router.post(
    "/create_access_info/",
    response_model=AccessInfoModel,
    status_code=status.HTTP_200_OK,
)
async def access_info_create(
    access_info_request: CreateAccessInfoRequest,
    session: Session = Depends(db_manager.get_db),
) -> AccessInfoModel:
    access_info_data = create_access_info(
        access_info=access_info_request.access_info,
        book_id=access_info_request.book_id,
        session=session,
    )
    return convert_access_info(access_info_data)
