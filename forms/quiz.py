from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, FileField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class NewQuizForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    is_public = BooleanField('Показывать в каталоге')
    image = FileField('Обложка')
    submit = SubmitField('Далее')
