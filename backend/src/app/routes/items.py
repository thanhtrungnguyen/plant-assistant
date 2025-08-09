from uuid import UUID
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import Item, User
from app.schemas import ItemRead, ItemCreate
from app.users import current_active_user

router = APIRouter(tags=["item"])


@router.get("/", response_model=list[ItemRead])
async def read_item(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> list[ItemRead]:
    result = await db.execute(select(Item).filter(Item.user_id == user.id))
    items = result.scalars().all()
    return [ItemRead.model_validate(item) for item in items]


@router.post("/", response_model=ItemRead)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> ItemRead:
    db_item = Item(**item.model_dump(), user_id=user.id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return ItemRead.model_validate(db_item)


@router.delete("/{item_id}")
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> Dict[str, Any]:
    result = await db.execute(
        select(Item).filter(Item.id == item_id, Item.user_id == user.id)
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")

    await db.delete(item)
    await db.commit()

    return {"message": "Item successfully deleted"}
