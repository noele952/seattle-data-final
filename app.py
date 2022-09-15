from flask import Flask, session, render_template, send_from_directory, redirect, url_for
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, length, Email
from flask_wtf import FlaskForm
import json
from funcs import *
from data import *
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"

data = requests.get('https://data.seattle.gov/resource/kzjm-xkqj.json').json()

geojson = 'static/seattle_neighborhoods.geojson'
with open(geojson) as file:
    geojson = json.load(file)['features']


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
    # if form.validate_on_submit():
    #     message = create_sns_message(form.email.data, form.content.data)
    #     publish_sns_message(topic, message)
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
        data_911 = get_data(endpoints.get('emergency', last_3days_911))
        data_crime = get_data(endpoints.get('crime', last_3days_crime))
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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)
