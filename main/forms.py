# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email

class NewsletterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
