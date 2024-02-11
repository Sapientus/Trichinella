from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves an user with specified email.

    :param email: The email to retrieve an user for.
    :type email: Str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user from the form.

    :param body: The data to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The new user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**dict(body), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates a refresh token for an user.

    :param user: The user to update for.
    :type user: User
    :param token: The new refresh token.
    :type token: Str
    :param db: The database session.
    :type db: Session
    :return: Nothing.
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Changes an user as confirmed in DB.

    :param email: The email to find an user.
    :type email: Str
    :param db: The database session.
    :type db: Session
    :return: Nothing.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates avatar of an user with certain email.

    :param email: The email to find an user.
    :type email: Str
    :param db: The database session.
    :type db: Session
    :return: The user with new avatar.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
