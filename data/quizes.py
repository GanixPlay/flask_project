import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Quiz(SqlAlchemyBase):
    __tablename__ = 'quizes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.Text)
    image = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    is_public = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    quiz = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')