# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class AddLogoForm(FlaskForm):
    file = StringField('Вставьте логотип', validators=[DataRequired()])

    submit = SubmitField('Подтвердить')
