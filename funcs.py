import folium
from folium import plugins
from shapely.geometry import shape, Point
from data import *
from datetime import datetime
import requests
import urllib.parse
import pyproj
from shapely.ops import transform
from functools import partial
import pandas as pd
import plotly.express as px
import boto3
from botocore.exceptions import ClientError
import os

AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')


def create_sns_message(email, message):
    message = email + '\n' + message
    return message


def publish_sns_message(topic_arn, message):
    """
    Publishes a message to a topic.
    """
    sns = boto3.client('sns', region_name=AWS_DEFAULT_REGION)
    subject = 'Seattle 911 Contact Form'
    try:

        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject,
        )['MessageId']
    except ClientError as err:
        print(err)
    else:
        return response


def create_neighborhood_list(geojson):
    neighborhood_list = []
    for feature in geojson:
        if feature['properties']['city'] == 'Seattle':
            neighborhood_list.append(feature['properties']['name'])
    neighborhood_list.sort(reverse=True)
    neighborhood_list.insert(0, 'Entire City')
    return neighborhood_list


def create_incident_list(data, type_func):
    incident_list = [type_func(item) for item in data]
    incident_list = set(incident_list)
    incident_list = list(incident_list)
    incident_list.sort()
    incident_list.insert(0, 'All Incidents')
    return incident_list


def address_lat_lon(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    return response[0]["lat"], response[0]["lon"]


def get_data(endpoint, query=''):
    if query:
        response = requests.get(endpoint + query)
    else:
        response = requests.get(endpoint)
    data = response.json()
    return data


def create_marker_text_911(item):
    try:
        text = f"<p style='text-align:center; font-weight:bold;'>{item.get('type')}</p>" \
             f"<p>{datetime.strptime(item.get('datetime'), '%Y-%m-%dT%X.%f').strftime('%b %d %Y')}</p>" \
             f"<p>{datetime.strptime(item.get('datetime'), '%Y-%m-%dT%X.%f').strftime('%I:%M %p')}</p>" \
             f"<p style='font-size:10px;'>Incident # {item.get('incident_number')}</p>"
    except KeyError:
        text = ''
    return text


def create_marker_text_crime(item):
    try:
        text = f"<p style='text-align:center; font-weight:bold;'>{item.get('offense')}</p>" \
             f"<p>Offense Type:{item.get('offense_parent_group')}</p>" \
             f"<p>{datetime.strptime(item.get('report_datetime'), '%Y-%m-%dT%X.%f').strftime('%b %d %Y')}</p>" \
             f"<p>{datetime.strptime(item.get('report_datetime'), '%Y-%m-%dT%X.%f').strftime('%I:%M %p')}</p>" \
             f"<p style='font-size:10px;'>Report # {item.get('report_number')}</p>" \
             f"<p style='font-size:10px;'>Offense ID {item.get('offense_id')}</p>" \
             f"<p style='font-size:10px;'>{item.get('_100_block_address')}</p>"
    except KeyError:
        text = ''
    return text


def create_marker_text_build(item):
    try:
        text = f"<p style='text-align:center; font-weight:bold;'>{item.get('permitclass')}</p>" \
         f"<p>{item.get('originaladdress1')}</p>" \
         f"<p>{item.get('description')}</p>" \
         f"<p style='font-size:10px;'><a href={item.get('link', {}).get('url', None)} " \
               f"target='_blank'>{item.get('link', {}).get('url', None)}</a></p>"
    except KeyError:
        text = ''
    return text


def create_marker_landuse(item):
    try:
        text = f"<p style='text-align:center; font-weight:bold;'>{item.get('permitclass')}</p>" \
             f"<p>{item.get('originaladdress1')}</p>" \
             f"<p>{item.get('description')}</p>" \
             f"<p style='font-size:10px;'><a href={item.get('link', {}).get('url', None)} " \
               f"target='_blank'>{item.get('link', {}).get('url', None)}</a></p>" \
             f"<p>Contractor<p>" \
             f"<p>{item.get('contractorcompanyname')}</p>"
    except KeyError:
        text = ''
    return text


def create_marker_violations(item):
    try:
        if item.get('recordtypedesc'):
            text = f"<p style='text-align:center; font-weight:bold;'>{item.get('recordtypedesc')}</p>" \
                "<p>Date of Complaint:</p>" \
                f"<p>{item.get('opendate')}</p>" \
                f"<p>{item.get('description')}</p>"
        else:
            text = "<p>Date of Complaint:</p>" \
                   f"<p>{item.get('opendate')}</p>" \
                   f"<p>{item.get('description')}</p>"
    except KeyError:
        text = ''
    return text


def incident_type_violations(item):
    return item.get('recordtypedesc')


def incident_type_landuse(item):
    return item.get('permitclass')


def incident_type_build(item):
    return item.get('permitclass')


def incident_type_crime(item):
    return item.get('offense_parent_group')


def incident_type_911(item):
    return item.get('type')


def get_marker_color_icon(item):
    if item in icon_data.keys():
        icon = icon_data.get(item).get('icon')
        color = icon_data.get(item).get('color')
    else:
        icon = icon_data.get('default').get('icon')
        color = icon_data.get('default').get('color')
    return color, icon


def address_circle_poly(lon, lat, radius=805):
    local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(
        lat, lon
    )
    wgs84_to_aeqd = partial(
        pyproj.transform,
        pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
        pyproj.Proj(local_azimuthal_projection),
    )
    aeqd_to_wgs84 = partial(
        pyproj.transform,
        pyproj.Proj(local_azimuthal_projection),
        pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
    )

    center = Point(float(lon), float(lat))
    point_transformed = transform(wgs84_to_aeqd, center)
    buffer = point_transformed.buffer(radius)
    # Get the polygon with lat lon coordinates
    circle_poly = transform(aeqd_to_wgs84, buffer)
    return circle_poly


def create_map(neighborhood, incident, data, geojson, marker_func, type_func,
               location=(47.608, -122.335), zoom_start=12):
    m = folium.Map(location=location, zoom_start=zoom_start)
    if neighborhood == 'Home':
        folium.Marker(
            location=location,
            icon=folium.Icon(color='red', icon='dot-circle-o', prefix='fa')
        ).add_to(m)
        folium.GeoJson(address_circle_poly(location[1], location[0]), name='geojson').add_to(m)
    if neighborhood == 'Entire City':
        m = folium.Map(location=location, zoom_start=zoom_start)
    else:
        for feature in geojson:
            if feature['properties']['name'] == neighborhood:
                center_lat = shape(feature["geometry"]).buffer(0).centroid.y
                center_lon = shape(feature["geometry"]).buffer(0).centroid.x
                m = folium.Map(location=[center_lat,
                               center_lon],
                               zoom_start=15)
                folium.GeoJson(feature['geometry'], name='geojson').add_to(m)
    for item in data:
        icon_color, icon_img = get_marker_color_icon(type_func(item))
        if incident == 'All Incidents':
            try:
                folium.Marker(
                    location=[item.get('latitude'), item.get('longitude')],
                    popup=marker_func(item),
                    icon=folium.Icon(color=icon_color, icon=icon_img, prefix='fa')
                    ).add_to(m)
            except KeyError:
                pass
        else:
            if type_func(item) == incident:
                try:
                    folium.Marker(
                          location=[item.get('latitude'), item.get('longitude')],
                          popup=marker_func(item),
                          icon=folium.Icon(color=icon_color, icon=icon_img, prefix='fa'),
                          ).add_to(m)
                except KeyError:
                    pass
    return m


def generate_heatmap(neighborhood, incident, data, geojson, type_func):
    m = folium.Map(location=[47.608, -122.335], tiles='Cartodb dark_matter', zoom_start=13)
    point_list = []
    if incident == 'All Incidents':
        for item in data:
            try:
                new_point = Point(float(item.get('longitude')), float(item.get('latitude')))
                point_list.append(new_point)
            except KeyError:
                pass
    else:
        for item in data:
            if type_func(item) == incident:
                try:
                    new_point = Point(float(item.get('longitude')), float(item.get('latitude')))
                    point_list.append(new_point)
                except KeyError:
                    pass
    if neighborhood != 'Entire City':
        for feature in geojson:
            if feature['properties']['name'] == neighborhood:
                center_lat = shape(feature["geometry"]).buffer(0).centroid.y
                center_lon = shape(feature["geometry"]).buffer(0).centroid.x
                m = folium.Map(location=[center_lat,
                                         center_lon],
                               zoom_start=15)
                folium.GeoJson(feature['geometry'], name='geojson').add_to(m)
    heat_data = [[point.xy[1][0], point.xy[0][0]] for point in point_list]
    plugins.HeatMap(heat_data).add_to(m)
    return m


def generate_911_sunburst(data_911):
    """Generates sunburst graph and stores it in static file"""
    incident_df = pd.DataFrame(data_911)
    df = incident_df.type.value_counts().rename_axis('incident').reset_index(name='counts')

    incident_type_list = []
    for incident in df.incident:
        if incident in fire_list:
            incident_type = 'Fire'
        elif incident in medical_list:
            incident_type = 'Medical'
        elif incident in police_list:
            incident_type = 'Police'
        else:
            incident_type = 'Other'
        incident_type_list.append(incident_type)

    df['incident_type'] = incident_type_list

    fig = px.sunburst(df, path=['incident_type', 'incident'], values='counts',
                      color_continuous_scale='Turbo'
                      )
    fig.update_traces(insidetextorientation='radial', hovertemplate='%{label} <br>Counts: %{value}')

    fig.write_image('static/images/graphs/sunburst_911.png')
    fig.write_html('static/sunburst_911.html')
    return 1


def generate_crime_sunburst(data_crime):
    """Generates sunburst graph and stores it in static file"""
    df = pd.DataFrame(data_crime)
    df = df.offense.value_counts().rename_axis('incident').reset_index(name='counts')
    crime_against_dict = {}
    for item in data_crime:
        crime_against_dict[item['offense']] = item['crime_against_category']
    parent_group = [crime_against_dict.get(series.incident) for index, series in df.iterrows()]
    df['offense_parent_group'] = parent_group
    fig = px.sunburst(df, path=['offense_parent_group', 'incident'], values='counts',

                      color_continuous_scale='Turbo'
                      )
    fig.update_traces(insidetextorientation='radial', hovertemplate='%{label} <br>Counts: %{value}')

    fig.write_html('static/sunburst_crime.html')
    fig.write_image('static/images/graphs/sunburst_crime.png')
    return 1


def generate_build_sunburst(data_build):
    """Generates sunburst graph and stores it in static file"""
    df = pd.DataFrame(data_build)
    df = df.permitclass.value_counts().rename_axis('permitclass').reset_index(name='counts')
    permitclassmapped_dict = {}
    try:
        for item in data_build:
            permitclassmapped_dict[item['permitclass']] = item['permitclassmapped']
    except KeyError:
        pass
    parent_group = [permitclassmapped_dict.get(series.permitclass) for index, series in df.iterrows()]
    df['permitclassmapped'] = parent_group
    fig = px.sunburst(df, path=['permitclassmapped', 'permitclass'], values='counts',

                      color_continuous_scale='Turbo'
                      )
    fig.update_traces(insidetextorientation='radial', hovertemplate='%{label} <br>Counts: %{value}')
    fig.write_image('static/images/graphs/sunburst_build.png')
    fig.write_html('static/sunburst_build.html')
