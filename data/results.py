import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Results(SqlAlchemyBase):
    __tablename__ = 'results'
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    user_name = sqlalchemy.Column(sqlalchemy.String)
    quiz_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('quizes.id'))
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
