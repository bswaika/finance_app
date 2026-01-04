from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from peewee import DoesNotExist

from ..models.custom_report import CustomReport
from ..models.user import User
from ..schemas.custom_report import (
    CustomReportCreate,
    CustomReportRead,
    CustomReportUpdate,
)
from ..services.auth_service import get_current_active_user


router = APIRouter()


@router.get("/", response_model=List[CustomReportRead])
async def list_custom_reports(
    current_user: User = Depends(get_current_active_user),
) -> List[CustomReportRead]:
    qs = CustomReport.select().where(CustomReport.user == current_user)
    return [_to_read(r) for r in qs]


@router.post("/", response_model=CustomReportRead, status_code=status.HTTP_201_CREATED)
async def create_custom_report(
    report_in: CustomReportCreate,
    current_user: User = Depends(get_current_active_user),
) -> CustomReportRead:
    report = CustomReport.create(
        user=current_user,
        name=report_in.name,
        description=report_in.description,
        sql_query=report_in.sql_query,
    )
    return _to_read(report)


@router.get("/{report_id}", response_model=CustomReportRead)
async def get_custom_report(
    report_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> CustomReportRead:
    try:
        report = CustomReport.get(
            CustomReport.id == report_id,
            CustomReport.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom report not found")

    return _to_read(report)


@router.put("/{report_id}", response_model=CustomReportRead)
async def update_custom_report(
    report_id: UUID,
    report_in: CustomReportUpdate,
    current_user: User = Depends(get_current_active_user),
) -> CustomReportRead:
    try:
        report = CustomReport.get(
            CustomReport.id == report_id,
            CustomReport.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom report not found")

    update_data = report_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    report.save()

    return _to_read(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_report(
    report_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        report = CustomReport.get(
            CustomReport.id == report_id,
            CustomReport.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom report not found")

    report.delete_instance()
    return None


def _to_read(report: CustomReport) -> CustomReportRead:
    return CustomReportRead(
        id=report.id,
        name=report.name,
        description=report.description,
        sql_query=report.sql_query,
    )


