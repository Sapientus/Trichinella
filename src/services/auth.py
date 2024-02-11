from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Takes a plain-text password and the hashed version of that password and returns True if they match, False otherwise.

        :param self: Represent the instance of the class
        :param plain_password: Check if the password entered by the user is correct
        :type plain_password: str
        :param hashed_password: Check if the password is hashed
        :type hashed_password: Str
        :return: A boolean value
        :rtype: Boolean
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Takes a password as input and returns the hash of that password.

        :param self: Represents the instance of the class
        :param password: Pass the password to be hashed into the function
        :param password: Str
        :return: A string of the hashed password
        :rtype: Str
        """
        return self.pwd_context.hash(password)

    def create_email_token(self, data: dict):
        """
        Takes a dictionary of data and returns a JWT token.
        The token is encoded with the SECRET_KEY and ALGORITHM defined in the class.
        The iat (issued at) claim is set to datetime.utcnow() and exp (expiration time)
        is set to one day from now.

        :param self: Represents the instance of the class
        :param data: Pass a dictionary to the function
        :type data: dict
        :return: A token
        :rtype: Str
        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Takes a token as an argument and returns the email associated with that token.
        If the token is invalid, it raises an HTTPException.

        :param self: Represents the instance of the class
        :param token: Pass the token to the function
        :type token: Str
        :return: The email
        :rtype: EmailStr
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Creates a new access token for the user.

        :param self: Represents the instance of the class
        :param data: Pass the data to be encoded in the jwt token
        :type data: dict
        :param expires_delta: Set the expiration time of the token
        :type expires_delta: Optional[float]
        :return: An encoded access token
        :rtype: Str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Creates a refresh token for the user.

        :param self: Represents the instance of the class
        :param data: Pass the user data to be encoded in the token
        :type data: dict
        :param expires_delta: Set the expiration time for the refresh token
        :type expires_delta: Optional[float]
        :return: An encoded refresh token
        :rtype: Str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        How simple it wouldn't sound but it decodes the refresh token.
        Will raise an HTTPException if the token is invalid or has expired.
        If the token is valid, it will return a string with the email address of the user who owns that refresh_token.

        :param self: Represents the instance of a class
        :param refresh_token: Pass the refresh token to the function
        :type refresh_token: Str
        :return: The email of the user
        :rtype: EmailStr
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        This is a dependency that takes an access token as input and returns the user object associated with it.

        :param self: Represents the instance of a class
        :param token: Pass the token to the function
        :type token: Str
        :param db: Get the database session from the dependency
        :type db: Session
        :return: The user object
        :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user


auth_service = Auth()
