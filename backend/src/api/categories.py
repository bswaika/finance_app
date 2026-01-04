from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from peewee import DoesNotExist
from pydantic import BaseModel

from ..models.category import Category
from ..models.user import User
from ..services.auth_service import get_current_active_user


router = APIRouter()


class CategoryBase(BaseModel):
    name: str
    category_type: str  # income, expense, both
    parent_category_id: UUID | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    category_type: str | None = None
    parent_category_id: UUID | None = None


class CategoryRead(CategoryBase):
    id: UUID
    is_system: bool


@router.get("/", response_model=List[CategoryRead])
async def list_categories(current_user: User = Depends(get_current_active_user)) -> List[CategoryRead]:
    # System categories: user is NULL and is_system = True
    system_cats = Category.select().where(Category.user.is_null(True), Category.is_system == True)  # type: ignore  # noqa: E712
    user_cats = Category.select().where(Category.user == current_user)

    def cat_to_read(c: Category) -> CategoryRead:
        return CategoryRead(
            id=c.id,
            name=c.name,
            category_type=c.category_type,
            parent_category_id=c.parent_category_id,
            is_system=c.is_system,
        )

    return [cat_to_read(c) for c in system_cats] + [cat_to_read(c) for c in user_cats]


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    cat_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
) -> CategoryRead:
    parent = None
    if cat_in.parent_category_id is not None:
        try:
            parent = Category.get(Category.id == cat_in.parent_category_id)
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent_category_id")

    cat = Category.create(
        user=current_user,
        name=cat_in.name,
        category_type=cat_in.category_type,
        parent_category=parent,
        is_system=False,
    )
    return CategoryRead(
        id=cat.id,
        name=cat.name,
        category_type=cat.category_type,
        parent_category_id=cat.parent_category_id,
        is_system=cat.is_system,
    )


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    cat_in: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
) -> CategoryRead:
    try:
        cat = Category.get(Category.id == category_id, Category.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    update_data = cat_in.dict(exclude_unset=True)

    if "parent_category_id" in update_data:
        if update_data["parent_category_id"] is None:
            cat.parent_category = None
        else:
            try:
                parent = Category.get(Category.id == update_data["parent_category_id"])
            except DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid parent_category_id",
                )
            cat.parent_category = parent
        update_data.pop("parent_category_id")

    for field, value in update_data.items():
        setattr(cat, field, value)
    cat.save()

    return CategoryRead(
        id=cat.id,
        name=cat.name,
        category_type=cat.category_type,
        parent_category_id=cat.parent_category_id,
        is_system=cat.is_system,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        cat = Category.get(Category.id == category_id, Category.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    cat.delete_instance()
    return None


