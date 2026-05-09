from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.book_access_crud import convert_access_info, update_access_info
from app.db.db_conn import db_manager
from app.models.access_info import AccessInfoModel, UpdateAccessInfoRequest

router = APIRouter()


@router.put(
    "/update_access_info/",
    response_model=AccessInfoModel,
    status_code=status.HTTP_200_OK,
)
async def access_info_update(
    access_info_request: UpdateAccessInfoRequest,
    session: Session = Depends(db_manager.get_db),
) -> AccessInfoModel:
    access_info_result = update_access_info(
        access_info_id=access_info_request.access_info_id,
        access_info_replacement=access_info_request.access_info,
        session=session,
    )

    if access_info_result:
        return convert_access_info(access_info_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Access info not found.",
    )
