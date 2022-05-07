# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired


class AddCourseworkForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    leader = IntegerField('Глава', validators=[DataRequired()])
    coursework = StringField('Тема', validators=[DataRequired()])
    coursework_sheets = IntegerField('Количество листов', validators=[DataRequired()])
    students = StringField('Ученики (индексы через запятую)', validators=[DataRequired()])
    deadline = DateField('Дедлайн', validators=[DataRequired()])
    direction = IntegerField('Направление', validators=[DataRequired()])
    is_finished = BooleanField('Завершено?')

    submit = SubmitField('Подтвердить')
