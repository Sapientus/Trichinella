from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from src.database.models import User
from src.database.db import get_db
from src.schemas import *
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_contact(
    body: ContactModel,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.update_contact(contact_id, body, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_birthdays(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    birth_contacts = await repository_contacts.get_birthdays(current_user, db)
    return birth_contacts


@router.get("/searching/", response_model=ContactResponse)
async def get_search_contacts(
    search_word: str = Query,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    search_contacts = await repository_contacts.get_search_contacts(
        search_word, current_user, db
    )
    return search_contacts
