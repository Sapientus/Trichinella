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
    """
    Returns a list of contacts for the current user.
    The limit and offset parameters are used to paginate the results.

    :param skip:
    :type skip:
    :param limit: Limitation of contacts' amount.
    :type limit: Int
    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: Contact | None
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    This one shows you a certain contact, the only one.

    :param contact_id: The needed id of stupid contact
    :type contact_id: Int
    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The contact we were looking for.
    :rtype: Contact | None
    """
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
    """
    Ah, finally we create a contact here, that's not so difficult.

    :param body: The data our user fills in.
    :type body: ContactModel
    :param limit: Limitation of contacts' amount.
    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A new contact we created.
    :rtype: Contact | None
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    This one marks our poor contact as "done".

    :param body: The data of our contact.
    :type body: ContactUpdate
    :param contact_id: Our contact's id which we want to update.
    :type contact_id: Int
    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: Updated contact.
    :rtype: Contact | None
    """
    contact = await repository_contacts.update_contact(
        contact_id, body, current_user, db
    )
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
    """
    This one kilss our contact in the most violant way. Kidding :)
    It just deletes our contact by its id.

    :param contact_id: Our contact's id which we want to delete.
    :type contact_id: Int
    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: Deleted contact.
    :rtype: Contact | None
    """
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
    """
    Shows the list of contacts whose birthday will be after 7 days.

    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: Updated contact.
    :rtype: Contact | None
    """
    birth_contacts = await repository_contacts.get_birthdays(current_user, db)
    return birth_contacts


@router.get("/searching/", response_model=ContactResponse)
async def get_search_contacts(
    search_word: str = Query,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a contact with the specified searchword.

    :param search_word: The word to search.
    :type search_word: Str
    :param current_user: The user to authenticate.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with certain word, or None if they don't match.
    :rtype: Contact | None
    """
    search_contacts = await repository_contacts.get_search_contacts(
        search_word, current_user, db
    )
    return search_contacts
