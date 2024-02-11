from typing import List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import *
from datetime import datetime, timedelta


# Show all contacts
async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list contacts.
    :rtype: List[Note]
    """
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype:  | None
    """
    return (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(
        firstname=body.firstname,
        lastname=body.lastname,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        user=user,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdate, user: User, db: Session
) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactUpdate
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        contact.firstname = (body.firstname,)
        contact.lastname = (body.lastname,)
        contact.email = (body.email,)
        contact.phone = (body.phone,)
        contact.birthday = (body.birthday,)
        contact.done = body.done
        db.commit()
    return contact


async def get_birthdays(user: User, db: Session) -> Contact | None:
    """
    Retrieves a list of contacts whose birthday will be in next 7 days.

    :param user: The user to authenticate.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The list of contacts, or None if they don't match.
    :rtype: Contact | None
    """
    seven_days_birth = datetime.now().date() + timedelta(days=7)
    contacts = (
        db.query(Contact)
        .filter(and_(Contact.birthday == seven_days_birth, Contact.user_id == user.id))
        .all()
    )
    return contacts


async def get_search_contacts(search_word, user: User, db: Session) -> Contact | None:
    """
    Retrieves a contact with the specified searcword.

    :param search_word: The word to search.
    :type search_word: Str
    :param user: The user to authenticate.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with certain word, or None if they don't match.
    :rtype: Contact | None
    """
    contact = (
        db.query(Contact)
        .filter(
            and_(
                Contact.user_id == user.id,
                or_(
                    Contact.firstname == search_word,
                    Contact.lastname == search_word,
                    Contact.email == search_word,
                ),
            )
        )
        .first()
    )
    return contact
