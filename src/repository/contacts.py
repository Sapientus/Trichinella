from typing import List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import *
from datetime import datetime, timedelta


# Show all contacts
async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
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
    seven_days_birth = datetime.now().date() + timedelta(days=7)
    contacts = (
        db.query(Contact)
        .filter(and_(Contact.birthday == seven_days_birth, Contact.user_id == user.id))
        .all()
    )
    return contacts


async def get_search_contacts(search_word, user: User, db: Session) -> Contact | None:
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
