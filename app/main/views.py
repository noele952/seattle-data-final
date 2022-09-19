from . import main_blueprint
from .forms import ContactForm, AddressForm, Map911Form, MapCrimeForm, MapBuildForm, ViolationsBuildForm
from .utils import *
from flask import render_template, redirect, url_for, current_app, abort, session


@main_blueprint.route('/admin')
def admin():
    abort(400)


@main_blueprint.context_processor
def inject():
    return dict(contact_form=ContactForm())


@main_blueprint.route("/contact", methods=["POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        sender = form.email.data
        message = form.content.data
        contact_form_email(sender, message)
    return redirect(url_for(session['page']))


@main_blueprint.route('/address-reset')
def reset():
    session['address'] = ''
    return redirect(url_for('main.index'))


@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    session['page'] = 'index'
    form = AddressForm()
    if form.validate_on_submit():
        print('form validate')
        try:
            address = form.address.data + ' Seattle, WA'
            address_lat, address_lon = address_lat_lon(address)
            session['address'] = [float(address_lat), float(address_lon)]
        except IndexError:
            error = "That is not a valid address"
            return render_template('index.html', form=form, error=error, active='home')
    if len(session['address']) != 0:
        print("address in session")
        print(f"Session address:{session['address']}")
        print(f"Type Session address:{type(session['address'])}")
        print(f"Length Session address:{len(session['address'])}")
        print(f"Session page:{session['page']}")
        data_911 = get_data(endpoints.get('emergency'), last_3days_911)
        data_crime = get_data(endpoints.get('crime'), last_3days_crime)
        data_build = get_data(endpoints.get('build'), last_3k_build)
        data_landuse = get_data(endpoints.get('landuse'))
        data_violations = get_data(endpoints.get('violations', last_60days_violations))
        m1 = create_map('Home', 'All Incidents', data_911, create_marker_text_911, incident_type_911,
                        location=session['address'], zoom_start=15)
        m2 = create_map('Home', 'All Incidents', data_crime, create_marker_text_crime, incident_type_crime,
                        location=session['address'], zoom_start=15)
        m3 = create_map('Home', 'All Incidents', data_build, create_marker_text_build, incident_type_build,
                        location=session['address'], zoom_start=15)
        m4 = create_map('Home', 'All Incidents', data_landuse,  create_marker_landuse, incident_type_landuse,
                        location=session['address'], zoom_start=15)
        m5 = create_map('Home', 'All Incidents', data_violations, create_marker_violations,
                        incident_type_violations,
                        location=session['address'], zoom_start=15)
        print("at the end")
        return render_template('index.html', form=form, map1=m1, map2=m2, map3=m3, map4=m4, map5=m5, active='home')
    return render_template('index.html', form=form, active='home')


@main_blueprint.route('/emergency', methods=['GET', 'POST'])
def emergency():
    data_911 = get_data(endpoints.get('emergency', last_3days_911))
    session['page'] = 'emergency'
    form = Map911Form()
    generate_911_sunburst(data_911)
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, form.incident.data, data_911, create_marker_text_911,
                       incident_type_911)
        m2 = generate_heatmap('Entire City', 'All Incidents', data_911, incident_type_911)
        return render_template('emergency.html', form=form, map=m, map2=m2, active='emergency')
    m = create_map('Entire City', 'All Incidents', data_911, create_marker_text_911, incident_type_911)
    m2 = generate_heatmap('Entire City', 'All Incidents', data_911, incident_type_911)
    return render_template('emergency.html', form=form, map=m, map2=m2, active='emergency')


@main_blueprint.route('/crime', methods=['GET', 'POST'])
def crime():
    data_crime = get_data(endpoints.get('crime', last_3days_crime))
    session['page'] = 'crime'
    form = MapCrimeForm()
    generate_crime_sunburst(data_crime)
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, form.incident_crime.data, data_crime, create_marker_text_crime,
                       incident_type_crime)
        m2 = generate_heatmap('Entire City', 'All Incidents', data_crime, incident_type_911)
        return render_template('crime.html', form=form, map=m, map2=m2, active='crime')
    m = create_map('Entire City', 'All Incidents', data_crime, create_marker_text_crime, incident_type_crime)
    m2 = generate_heatmap('Entire City', 'All Incidents', data_crime, incident_type_crime)
    return render_template('crime.html', form=form, map=m, map2=m2, active='crime')


@main_blueprint.route('/violations', methods=['GET', 'POST'])
def violations():
    data_violations = get_data(endpoints.get('violations', last_60days_violations))
    session['page'] = 'violations'
    form = ViolationsBuildForm()
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, 'All Incidents', data_violations, create_marker_violations,
                       incident_type_violations)
        return render_template('violations.html', form=form, map=m, active='violations')
    m = create_map('Entire City', 'All Incidents', data_violations, create_marker_violations,
                   incident_type_violations)

    return render_template('violations.html', form=form, map=m, active='violations')


@main_blueprint.route('/build', methods=['GET', 'POST'])
def build():
    data_build = get_data(endpoints.get('build'), last_3k_build)
    data_landuse = get_data(endpoints.get('landuse'))
    session['page'] = 'build'
    form = MapBuildForm()
    generate_build_sunburst(data_build)
    if form.submit.data and form.validate():
        m = create_map(form.neighborhood.data, form.incident_build.data, data_build, create_marker_text_build,
                       incident_type_build)
        m3 = create_map(form.neighborhood.data, 'All Incidents', data_landuse, create_marker_landuse,
                        incident_type_landuse)
        m2 = generate_heatmap('Entire City', 'All Incidents', data_build, incident_type_build)
        return render_template('build.html', form=form, map=m, map2=m2, map3=m3, active='build')
    m = create_map('Entire City', 'All Incidents', data_build, create_marker_text_build, incident_type_build)
    m3 = create_map('Entire City', 'All Incidents', data_landuse, create_marker_landuse,
                    incident_type_landuse)
    m2 = generate_heatmap('Entire City', 'All Incidents', data_build, incident_type_build)
    return render_template('build.html', form=form, map=m, map2=m2, map3=m3, active='build')
