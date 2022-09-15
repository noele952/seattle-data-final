from flask import Flask, render_template
import json
from funcs import *
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"

data = requests.get('https://data.seattle.gov/resource/kzjm-xkqj.json').json()

geojson = 'static/seattle_neighborhoods.geojson'
with open(geojson) as file:
    geojson = json.load(file)['features']


@app.route('/', methods=['GET', 'POST'])
def index():
    m = create_map('Entire City', 'All Incidents', data, geojson, create_marker_text_911, incident_type_911)
    m = m._repr_html_()
    return m


if __name__ == '__main__':
    app.run(debug=True)
