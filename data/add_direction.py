# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired


class AddDirectionForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    teacher = IntegerField('Учитель (индекс)', validators=[DataRequired()])
    students = StringField('Ученики (индексы через запятую)', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])

    submit = SubmitField('Подтвердить')
