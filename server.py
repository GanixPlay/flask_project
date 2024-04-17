import flask_login
from flask import Flask, url_for, request, render_template, redirect, abort, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required
import base64
import random

from data import db_session
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.quiz import NewQuizForm
from forms.question import QuestionForm
from data.users import User
from data.quizes import Quiz
from data.results import Results
from qrcoder import get_qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(401)
def not_authorized(error):
    return render_template('401.html'), 401


@app.template_filter('shuffle')
def filter_shuffle(lst):
    try:
        result = list(lst)
        random.shuffle(result)
        return result
    except:
        return lst


@login_manager.user_loader
def load_user(user_id):
    sess = db_session.create_session()
    return sess.query(User).get(user_id)


@app.route('/')
def index():
    qr = get_qrcode('https://lace-necessary-tv.glitch.me/quiz/5')
    return render_template('index.html', title='KvantQuiz', qr=qr)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.again_password.data:
            return render_template('register.html', form=form, message='Пароли не совпадают', title='Регистрация')
        sess = db_session.create_session()
        users = sess.query(User).filter(User.email == form.email.data).first()
        if users:
            return render_template('register.html', form=form, message='Такой пользователь уже есть',
                                   title='Регистрация')
        user = User(
            name=form.name.data,
            email=form.email.data,
            avatar=base64.b64encode(form.avatar.data.read()).decode("ascii")
        )
        user.set_password(form.password.data)
        sess.add(user)
        sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form, title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session['quest_num'] = (-1, 0, 0)
    form = LoginForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        user = sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# @app.route('/new_quiz', methods=['GET', 'POST'])
# def test():
#     quiz_form = NewQuizForm()
#     quest_form = QuestionForm()
#     questions = session.get('question', [])
#     print(questions)
#     if request.method == 'POST':
#         print('Hello')
#         return render_template('questions_settings.html', type=request.form.get('select'), form=quest_form)
#
#     if quiz_form.validate_on_submit():
#         return render_template('questions_settings.html', form=quest_form)
#     if quest_form.validate_on_submit():
#         session['question'].append(quest_form.title.data)
#         return render_template('questions_settings.html', questions=questions, form=quest_form)
#     return render_template('quiz_settings.html', form=quiz_form)

@app.route('/new_quiz', methods=['GET', 'POST'])
@login_required
def new_quiz():
    form = NewQuizForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            image=base64.b64encode(form.image.data.read()).decode("ascii"),
            is_public=form.is_public.data,
        )
        user = sess.query(User).filter(User.id == flask_login.current_user.id).first()
        user.quizes.append(quiz)
        sess.add(quiz)
        sess.commit()
        return redirect(f'/new_quiz/{quiz.id}')
    return render_template('quiz_settings.html', form=form)


@app.route('/new_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quest_lsit(quiz_id):
    # print(session)
    form = QuestionForm()
    sess = db_session.create_session()
    questions = sess.query(Quiz).get(quiz_id).quiz['questions'] if sess.query(Quiz).get(quiz_id).quiz else []
    # questions = session.get('questions', [])
    if request.method == 'POST':
        # print('Hello')
        qtype = request.form.get('select')
        qid = len(questions) + 1

        if not questions:
            quiz = sess.query(Quiz).get(quiz_id)
            quiz.quiz = {'questions': []}
            sess.commit()

        # qid = len(session.get('questions', [])) + 1
        # if session.get('questions', []):
        #     session['questions'].append({'id': qid, 'type': qtype})
        #     session['questions'][qid - 1] = {'id': qid, 'type': qtype}
        # else:
        #     session['questions'] = [{'id': qid, 'type': qtype}]
        # print(session['questions'])
        session['type'] = qtype
        return redirect(f'/new_quiz/{quiz_id}/{qid}')
    return render_template('quest_list.html', questions=questions, quiz_id=quiz_id)


@app.route('/new_quiz/<int:quiz_id>/<int:quest_id>', methods=['GET', 'POST'])
@login_required
def new_quest(quiz_id, quest_id):
    form = QuestionForm()
    # print(form.title.data)
    # print(session['questions'])
    # qtype = session['questions'][quest_id - 1]['type']
    qtype = session['type']
    sess = db_session.create_session()
    quests = sess.query(Quiz).filter(Quiz.id == quiz_id).first().quiz['questions']
    sess.close()

    if quest_id - 1 < len(quests):
        qtype = quests[quest_id - 1]['type']

    if form.validate_on_submit():
        # print('Hello')
        if qtype == 'couple':
            answer = [form.answer.data]
            answer.extend([request.form.get(x) for x in request.form.getlist('cor')])
        else:
            answer = form.answer.data
        image = base64.b64encode(form.image.data.read()).decode("ascii")
        sl = {'id': quest_id,
              'type': qtype,
              'image': image,
              'title': form.title.data,
              'answer': answer,
              'var1': form.var1.data,
              'var2': form.var2.data,
              'var3': form.var3.data}
        sess = db_session.create_session()
        quiz = sess.query(Quiz).filter(Quiz.id == quiz_id).first()
        if quest_id - 1 < len(quiz.quiz['questions']):
            quests = quiz.quiz['questions'][::]
            if not form.image.data:
                image = quests[quest_id - 1]['image']
                sl['image'] = image
            quests[quest_id - 1] = sl
            quiz.quiz = {'questions': quests[::]}
        else:
            # quests = quiz.quiz['questions']
            # print(quests)
            # quests += [sl]
            # print(quests)
            quiz.quiz = {'questions': quiz.quiz['questions'] + [sl]}
        # print(quiz)
        sess.commit()
        # print(sess.query(Quiz).get(quiz_id).quiz)
        # quests = session['questions']
        # quests.extend([sl])
        # print(quests, 'quests')
        # session['questions'].extend([sl])
        # session['questions'] = quests
        # print(session['questions'])
        # print(session
        #       )
        return redirect(f'/new_quiz/{quiz_id}')
    # редактирование
    if quest_id - 1 < len(quests):
        quest = quests[quest_id - 1]
        qtype = quest['type']
        form.image.data = quest['image']
        form.title.data = quest['title']
        if qtype == 'couple':
            form.answer.data = quest['answer'][0]
        else:
            form.answer.data = quest['answer']
        form.var1.data = quest['var1']
        form.var2.data = quest['var2']
        form.var3.data = quest['var3']

    return render_template('questions_settings.html', form=form, type=qtype, quest=quest)


@app.route('/my_quizes')
@login_required
def my_quizes():
    return render_template('my_quizes.html')


@app.route('/delete/<int:quiz_id>/<int:quest_id>')
@login_required
def delete_quest(quiz_id, quest_id):
    sess = db_session.create_session()
    quiz = sess.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == flask_login.current_user.id).first()
    if quiz:
        quests = quiz.quiz['questions'][::]
        for i in range(quest_id, len(quests)):
            quests[i]['id'] -= 1
        del quests[quest_id - 1]

        quiz.quiz = {'questions': quests[::]}
        sess.commit()
    else:
        abort(404)
    return redirect(f'/new_quiz/{quiz_id}')


@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz_info(quiz_id):
    sess = db_session.create_session()
    quiz = sess.query(Quiz).get(quiz_id)
    if request.method == 'POST':
        session['player_name'] = request.form.get('player_name')
        session['quest_num'] = (-1, 0, 0)
        print(session['player_name'])
        return redirect(f'/play/{quiz_id}')
    qr = get_qrcode(request.base_url)
    return render_template('quiz.html', quiz=quiz, qr=qr)


@app.route('/play/<int:quiz_id>', methods=['GET', 'POST'])
def play(quiz_id):
    sess = db_session.create_session()
    quiz = sess.query(Quiz).get(quiz_id)
    q_id, quest_count, score = session.get('quest_num', (-1, 0, 0))
    if q_id != quiz_id:
        session['quest_num'] = (quiz_id, 0, 0)
        q_id, quest_count, score = quiz_id, 0, 0
    if request.method == 'POST':
        if quiz.quiz['questions'][quest_count]['type']:
            if set(request.form.getlist('answer_check')) == set(quiz.quiz['questions'][quest_count]['answer']):
                score += 1
            elif request.form.get('answer') == quiz.quiz['questions'][quest_count]['answer']:
                score += 1
            else:
                print('incorrect')
        else:
            print('incorrect')
        session['quest_num'] = (quiz_id, quest_count + 1, score)
        return redirect(f'/play/{quiz_id}')
        # return render_template('play.html', question=question)
    q_id, quest_count, score = session.get('quest_num', (-1, 0, 0))
    if quest_count >= len(quiz.quiz['questions']):
        return redirect('/final')
    question = quiz.quiz['questions'][quest_count]
    if q_id != quiz_id:
        session['quest_num'] = (quiz_id, 0, 0)
        q_id, quest_count, score = quiz_id, 0, 0

    return render_template('play.html', question=question)


@app.route('/final')
def final():
    q_id, quest_count, score = session.get('quest_num', (-1, 0, 0))
    # session['quest_num'] = (-1, 0, 0)
    sess = db_session.create_session()
    name = session['player_name']
    result = sess.query(Results).filter(Results.user_name == name, Results.quiz_id == q_id).first()
    if not result:
        res = Results(user_name=name,
                      quiz_id=q_id,
                      score=score)
        sess.add(res)
        sess.commit()
    results = sorted(sess.query(Results).filter(Results.quiz_id == q_id).all(), key=lambda x: x.score, reverse=True)
    return render_template('passed_quiz.html', score=score, results=results, maxx=quest_count)


@app.route('/catalog')
def catalog():
    sess = db_session.create_session()
    quizes = sess.query(Quiz).filter(Quiz.is_public == 1).all()
    return render_template('catalog.html', quizes=quizes)


@app.route('/delete/<int:quiz_id>')
@login_required
def delete_quiz(quiz_id):
    sess = db_session.create_session()
    quiz = sess.query(Quiz).get(quiz_id)
    sess.delete(quiz)
    sess.commit()
    sess.close()
    return redirect('/my_quizes')


def main():
    db_session.global_init("db/blogs.db")
    app.run('127.0.0.1', 8080)


if __name__ == '__main__':
    main()
