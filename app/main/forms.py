from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email
from .utils import *


class Map911Form(FlaskForm):
    incident = SelectField('Incident Type',
                           choices=create_incident_list(get_data(endpoints.get('emergency'), last_3days_911),
                                                        incident_type_911))
    neighborhood = SelectField('Neighborhood', choices=get_neighborhood_list())
    submit = SubmitField("Submit")


class MapCrimeForm(FlaskForm):
    incident_crime = SelectField('Crime Type',
                                 choices=create_incident_list(get_data(endpoints.get('crime'), last_3days_crime),
                                                              incident_type_crime))
    neighborhood = SelectField('Neighborhood', choices=get_neighborhood_list())
    submit = SubmitField("Submit")


class MapBuildForm(FlaskForm):
    incident_build = SelectField('Type',
                                 choices=create_incident_list(get_data(endpoints.get('build'), last_3k_build),
                                                              incident_type_build))
    neighborhood = SelectField('Neighborhood', choices=get_neighborhood_list())
    submit = SubmitField("Submit")


class ViolationsBuildForm(FlaskForm):
    neighborhood = SelectField('Neighborhood', choices=get_neighborhood_list())
    submit = SubmitField("Submit")


class AddressForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired(), Length(min=10, max=100)])
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    content = TextAreaField("Message", render_kw={"rows": 3, "cols": 100}, validators=[DataRequired(),
                                                                                       Length(min=2, max=5000)])
    submit = SubmitField("Send Message")
