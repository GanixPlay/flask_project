from flask_restful import reqparse, Api, abort, Resource
from data import db_session
from data.results import Results
from data.quizes import Quiz
from flask import jsonify


def abort_if_results_not_found(id):
    sess = db_session.create_session()
    results = sess.query(Quiz).get(id)
    if not results:
        abort(404, message=f'Quiz {id} not found')


class ResultResource(Resource):
    def get(self, quiz_id):
        abort_if_results_not_found(quiz_id)
        sess = db_session.create_session()
        results = sess.query(Results).filter(Results.quiz_id == quiz_id).all()
        return jsonify({'results': [{'name': x.user_name, 'score': x.score} for x in results]})
