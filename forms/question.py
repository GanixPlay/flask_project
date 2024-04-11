from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    image = FileField('Обложка')
    title = StringField('Вопрос', validators=[DataRequired()])
    answer = StringField('Ответ', validators=[DataRequired()])
    var1 = StringField('Вариант ответа 2')
    var2 = StringField('Вариант ответа 3')
    var3 = StringField('Вариант ответа 4')
    submit = SubmitField('Сохранить')
