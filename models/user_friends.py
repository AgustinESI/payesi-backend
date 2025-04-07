#user_friends.py

from sqlalchemy import Column, ForeignKey, String, Table
from models import db

Friends = Table(
    'user_friends',
    db.Model.metadata,
    Column('user_dni', String(36), ForeignKey('user.dni'), primary_key=True),
    Column('friend_dni', String(36), ForeignKey('user.dni'), primary_key=True)
)
