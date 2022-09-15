from flask import Flask, session, render_template, redirect, url_for
from wtforms import SubmitField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, length, Email
from flask_wtf import FlaskForm
import json
from funcs import *
from data import *
import boto3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

sns = boto3.resource('sns')
TOPIC_ARN = os.environ.get('TOPIC_ARN')


data_911 = get_data(endpoints.get('emergency', last_3days_911))
data_crime = get_data(endpoints.get('crime', last_3days_crime))
data_build = get_data(endpoints.get('build'), last_3k_build)

geojson = 'static/seattle_neighborhoods.geojson'
with open(geojson) as file:
    geojson = json.load(file)['features']


neighborhood_list = create_neighborhood_list(geojson)


class Map911Form(FlaskForm):
    incident = SelectField('Incident Type', choices=create_incident_list(data_911, incident_type_911))
    neighborhood = SelectField('Neighborhood', choices=neighborhood_list)
    submit = SubmitField("Submit")


class MapCrimeForm(FlaskForm):
    incident_crime = SelectField('Crime Type', choices=create_incident_list(data_crime, incident_type_crime))
    neighborhood = SelectField('Neighborhood', choices=neighborhood_list)
    submit = SubmitField("Submit")


class MapBuildForm(FlaskForm):
    incident_build = SelectField('Type', choices=create_incident_list(data_build, incident_type_build))
    neighborhood = SelectField('Neighborhood', choices=neighborhood_list)
    submit = SubmitField("Submit")


class ViolationsBuildForm(FlaskForm):
    neighborhood = SelectField('Neighborhood', choices=neighborhood_list)
    submit = SubmitField("Submit")


class AddressForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired(), length(min=10, max=100)])
    city = StringField("City", validators=[DataRequired(), length(min=2, max=100)])
    state = StringField("State", validators=[DataRequired(), length(min=2, max=2)])
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    content = TextAreaField("Message", render_kw={"rows": 3, "cols": 100}, validators=[DataRequired(),
                                                                                       length(min=2, max=5000)])
    submit = SubmitField("Send Message")


@app.context_processor
def inject():
    return dict(
        contact_form=ContactForm()
    )


@app.route("/contact", methods=["POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        pass
        message = create_sns_message(form.email.data, form.content.data)
        publish_sns_message(TOPIC_ARN, message)
    return redirect(url_for(session['page']))


@app.route('/', methods=['GET', 'POST'])
def index():
    session['page'] = 'index'
    session['address'] = ''
    form = AddressForm()
    if form.validate_on_submit():
        address = form.address.data + ' ' + form.city.data + ', ' + form.state.data
        address_lat, address_lon = address_lat_lon(address)
        session['address'] = [float(address_lat), float(address_lon)]
    if session['address']:
        global data_911
        data_911 = get_data(endpoints.get('emergency', last_3days_911))
        global data_crime
        data_crime = get_data(endpoints.get('crime', last_3days_crime))
        global data_build
        data_build = get_data(endpoints.get('build'), last_3k_build)
        data_landuse = get_data(endpoints.get('landuse'))
        data_violations = get_data(endpoints.get('violations', last_60days_violations))
        m1 = create_map('Home', 'All Incidents', data_911, geojson, create_marker_text_911, incident_type_911,
                        location=session['address'], zoom_start=15)
        m1 = m1._repr_html_()
        m2 = create_map('Home', 'All Incidents', data_crime, geojson, create_marker_text_crime, incident_type_crime,
                        location=session['address'], zoom_start=15)
        m2 = m2._repr_html_()
        m3 = create_map('Home', 'All Incidents', data_build, geojson, create_marker_text_build, incident_type_build,
                        location=session['address'], zoom_start=15)
        m3 = m3._repr_html_()
        m4 = create_map('Home', 'All Incidents', data_landuse, geojson, create_marker_landuse, incident_type_landuse,
                        location=session['address'], zoom_start=15)
        m4 = m4._repr_html_()
        m5 = create_map('Home', 'All Incidents', data_violations, geojson, create_marker_violations,
                        incident_type_violations,
                        location=session['address'], zoom_start=15)
        m5 = m5._repr_html_()
        return render_template('index.html', form=form, map1=m1, map2=m2, map3=m3, map4=m4, map5=m5)
    return render_template('index.html', form=form)


@app.route('/emergency', methods=['GET', 'POST'])
def emergency():
    global data_911
    data_911 = get_data(endpoints.get('emergency', last_3days_911))
    session['page'] = 'emergency'
    form = Map911Form()
    generate_911_sunburst(data_911)
    if form.submit.data and form.validate():
        "form validate"
        m = create_map(form.neighborhood.data, form.incident.data, data_911, geojson, create_marker_text_911,
                       incident_type_911)
        m = m._repr_html_()
        m2 = generate_heatmap('Entire City', 'All Incidents', data_911, geojson, incident_type_911)
        m2 = m2._repr_html_()
        return render_template('emergency.html', form=form, map=m, map2=m2)
    m = create_map('Entire City', 'All Incidents', data_911, geojson, create_marker_text_911, incident_type_911)
    m = m._repr_html_()
    m2 = generate_heatmap('Entire City', 'All Incidents', data_911, geojson, incident_type_911)
    m2 = m2._repr_html_()
    return render_template('emergency.html', form=form, map=m, map2=m2)


@app.route('/crime', methods=['GET', 'POST'])
def crime():
    global data_crime
    data_crime = get_data(endpoints.get('crime', last_3days_crime))
    session['page'] = 'crime'
    form = MapCrimeForm()
    generate_crime_sunburst(data_crime)
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, form.incident_crime.data, data_crime, geojson, create_marker_text_crime,
                       incident_type_crime)
        m = m._repr_html_()
        m2 = generate_heatmap('Entire City', 'All Incidents', data_911, geojson, incident_type_911)
        m2 = m2._repr_html_()
        return render_template('crime.html', form=form, map=m, map2=m2)
    m = create_map('Entire City', 'All Incidents', data_crime, geojson, create_marker_text_crime, incident_type_crime)
    m = m._repr_html_()
    m2 = generate_heatmap('Entire City', 'All Incidents', data_crime, geojson, incident_type_crime)
    m2 = m2._repr_html_()
    return render_template('crime.html', form=form, map=m, map2=m2)


@app.route('/violations', methods=['GET', 'POST'])
def violations():
    data_violations = get_data(endpoints.get('violations', last_60days_violations))
    session['page'] = 'violations'
    form = ViolationsBuildForm()
    generate_crime_sunburst(data_crime)
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, 'All Incidents', data_violations, geojson, create_marker_violations,
                       incident_type_violations)
        m = m._repr_html_()
        return render_template('violations.html', form=form, map=m)
    m = create_map('Entire City', 'All Incidents', data_violations, geojson, create_marker_violations,
                   incident_type_violations)
    m = m._repr_html_()
    return render_template('violations.html', form=form, map=m)


@app.route('/build', methods=['GET', 'POST'])
def build():
    global data_build
    data_build = get_data(endpoints.get('build'), last_3k_build)
    data_landuse = get_data(endpoints.get('landuse'))
    session['page'] = 'build'
    form = MapBuildForm()
    generate_build_sunburst(data_build)
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, form.incident_build.data, data_build, geojson, create_marker_text_build,
                       incident_type_build)
        m = m._repr_html_()
        m3 = create_map(form.neighborhood.data, 'All Incidents', data_landuse, geojson, create_marker_landuse,
                        incident_type_landuse)
        m3 = m3._repr_html_()
        m2 = generate_heatmap('Entire City', 'All Incidents', data_build, geojson,
                              incident_type_build)
        m2 = m2._repr_html_()
        return render_template('build.html', form=form, map=m, map2=m2, map3=m3)
    m = create_map('Entire City', 'All Incidents', data_build, geojson, create_marker_text_build, incident_type_build)
    m = m._repr_html_()

    m3 = create_map('Entire City', 'All Incidents', data_landuse, geojson, create_marker_landuse,
                    incident_type_landuse)
    m3 = m3._repr_html_()
    m2 = generate_heatmap('Entire City', 'All Incidents', data_build, geojson, incident_type_build)
    m2 = m2._repr_html_()
    return render_template('build.html', form=form, map=m, map2=m2, map3=m3)


if __name__ == '__main__':
    app.run()
