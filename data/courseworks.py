import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Coursework(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'courseworks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    coursework = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    coursework_sheets = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
    students = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    deadline = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    direction = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directions.id"))
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user = orm.relation('User')

    def __repr__(self):
        return f'<Coursework> {self.coursework}'
