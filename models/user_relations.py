#user_relations.py

from sqlalchemy import Column, ForeignKey, String, Table
from models import db

Friends = Table(
    'friends',
    db.metadata,
    Column('user_dni', String(36), ForeignKey('user.dni'), primary_key=True),
    Column('friend_dni', String(36), ForeignKey('user.dni'), primary_key=True)
)

Blocked = Table(
    'blocked_users',
    db.metadata,
    Column('user_dni', String(36), ForeignKey('user.dni'), primary_key=True),
    Column('blocked_dni', String(36), ForeignKey('user.dni'), primary_key=True)
)

Favourites = Table(
    'favourite_users',
    db.metadata,
    Column('user_dni', String(36), ForeignKey('user.dni'), primary_key=True),
    Column('favourite_dni', String(36), ForeignKey('user.dni'), primary_key=True)
)