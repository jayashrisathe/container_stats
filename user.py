"""This file is used create database, user table"""
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URI = 'sqlite:///user_crud_operations.db'
Base = declarative_base()


class User(Base):
    """User Model to create table and columns"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(50))
    email = Column(String(50), nullable=False)
    age = Column(String(50))

    def __init__(self, name, phone, email, age):
        self.name = name
        self.phone = phone
        self.email = email
        self.age = age


def get_db_seesion():
    """
    @description - Used to create database.
    @returns - returns session which is used in user_operations file
    """
    engine = create_engine(DB_URI)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(DB_URI))
    session = scoped_session(session_maker)
    return session
