from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.book_access_crud import (
    convert_access_info,
    get_access_info_by_book_id,
    get_access_info_by_id,
)
from app.db.db_conn import db_manager
from app.models.access_info import AccessInfoModel

router = APIRouter()


@router.get(
    "/get_access_info_by_id/{access_info_id}",
    response_model=AccessInfoModel,
    status_code=status.HTTP_200_OK,
)
async def access_info_by_id(
    access_info_id: int,
    session: Session = Depends(db_manager.get_db),
) -> AccessInfoModel:
    access_info_result = get_access_info_by_id(
        access_info_id=access_info_id,
        session=session,
    )
    if access_info_result:
        return convert_access_info(access_info_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Access info not found.",
    )


@router.get(
    "/get_access_info_by_book_id/{book_id}",
    response_model=AccessInfoModel,
    status_code=status.HTTP_200_OK,
)
async def access_info_by_book_id(
    book_id: int,
    session: Session = Depends(db_manager.get_db),
) -> AccessInfoModel:
    access_info_result = get_access_info_by_book_id(
        book_id=book_id,
        session=session,
    )
    if access_info_result:
        return convert_access_info(access_info_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Access info not found.",
    )
