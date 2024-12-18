#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from user import Base, User
import logging

logging.disable(logging.WARNING)


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Add a user to the database.
        """
        session = self._session
        try:
            new_user = User()
            new_user.email = email
            new_user.hashed_password = hashed_password
            session.add(new_user)
            session.commit()
        except Exception:
            session.rollback()
            new_user = None
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """
        Retrives a user from the datbase.
        """
        session = self._session
        for attr, value in kwargs.items():
            if not hasattr(User, attr):
                raise InvalidRequestError()
        try:
            user = session.query(User).filter_by(**kwargs).one()
        except NoResultFound:
            raise NoResultFound()
        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user.
        """
        session = self._session
        try:
            user = self.find_user_by(id=user_id)
        except NoResultFound:
            pass
        for attr, value in kwargs.items():
            if not hasattr(User, attr):
                raise ValueError
            setattr(user, attr, value)
        session.commit()
