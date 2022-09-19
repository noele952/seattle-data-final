from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class ContactForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    content = TextAreaField("Message", render_kw={"rows": 3, "cols": 100}, validators=[DataRequired(),
                                                                                       Length(min=2, max=5000)])
    submit = SubmitField("Send Message")
