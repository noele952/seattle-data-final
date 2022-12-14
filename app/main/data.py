from datetime import datetime, timedelta

fmt = '%Y-%m-%dT%X.%f'
last_3k_build = '?$limit=3000'
last_3days_911 = f"?$where=:created_at > '{(datetime.now() + timedelta(days=-3)).strftime(fmt)}'"
last_3days_crime = f"?$where=report_datetime between '{(datetime.now() + timedelta(days=-3)).strftime(fmt)}' and " \
                   f"'{datetime.now().strftime(fmt)}'"
last_60days_violations = f"?$where=opendate between '{(datetime.now() + timedelta(days=-60)).strftime(fmt)}' and " \
                         f"'{datetime.now().strftime(fmt)}'"


endpoints = {
    'emergency': 'https://data.seattle.gov/resource/kzjm-xkqj.json',
    'crime': 'https://data.seattle.gov/resource/tazs-3rd5.json',
    'build': 'https://data.seattle.gov/resource/8tqq-u7ib.json',
    'landuse': 'https://data.seattle.gov/resource/q2zt-n6jk.json',
    'violations': 'https://data.seattle.gov/resource/ez4a-iug7.json',
}

fire_list = ['Automatic Fire Alarm Resd', 'Auto Fire Alarm', 'Bark Fire', 'Brush Fire Freeway', 'Car Fire',
             'Fire in Building', 'Rubbish Fire', 'Brush Fire', 'Dumpster Fire', 'Illegal Burn',
             'Encampment Fire',
             'Automatic Fire Alarm False', ]
medical_list = ['Triaged Incident', 'Nurseline/AMR', 'Aid Response', 'Mutual Aid- Aid', 'BC Aid Response',
                'Aid Response Yellow', 'Medic Response- Overdose', 'Medic Response- 6 per Rule',
                'Single Medic Unit',
                'BC Medic Response- 6 per rule', 'Medic Response', 'Medic Response- 7 per Rule']
police_list = ['Scenes Of Violence 7', '4RED - 2 + 1 + 1', 'MVI - Motor Vehicle Incident', 'Encampment Aid',
               '1RED 1 Unit', 'AFA4 - Auto Alarm 2 + 1 + 1', 'MVI Freeway']

icon_data = {'Aid Response': {'icon': 'ambulance', 'color': 'red'},
             'Medic Response': {'icon': 'ambulance', 'color': 'red'},
             'Medic Response- 6 Per Rule': {'icon': 'ambulance', 'color': 'red'},
             'Medic Response- 7 Per Rule': {'icon': 'ambulance', 'color': 'red'},
             'Single Medic Unit': {'icon': 'ambulance', 'color': 'red'},
             'Triaged Incident': {'icon': 'plus-square', 'color': 'red'},
             'Aid Response - Yellow': {'icon': 'ambulance', 'color': 'green'},
             'Nurseline/AMR': {'icon': 'user-md', 'color': 'green'},
             'Encampment Aid': {'icon': 'envelope-open', 'color': 'green'},
             'Aid Response Yellow': {'icon': 'ambulance', 'color': 'green'},
             'Medic Response - Overdose': {'icon': 'heartbeat', 'color': 'orange'},
             'MVI - Motor Vehicle Incident': {'icon': 'car', 'color': 'green'},
             'Rescue Elevator': {'icon': 'building', 'color': 'green'},
             'Fire in Building': {'icon': 'house-fire', 'color': 'red'},
             'Automatic Fire Alarm Resd': {'icon': 'fire', 'color': 'red'},
             'Rescue Extrication': {'icon': 'plus-square', 'color': 'red'},
             'Auto Fire Alarm': {'icon': 'fire', 'color': 'orange'},
             'Illegal Burn': {'icon': 'fire-extinguisher', 'color': 'orange'},
             'Rubbish Fire': {'icon': 'fire-extinguisher', 'color': 'orange'},
             'Activated CO Detector': {'icon': 'warning', 'color': 'green'},
             'Natural Gas Odor': {'icon': 'warning', 'color': 'green'},
             'Natural Gas Leak': {'icon': 'warning', 'color': 'green'},
             'Water Job Major': {'icon': 'shower', 'color': 'blue'},
             'Water Job Minor': {'icon': 'shower', 'color': 'blue'},
             'ship': {'icon': 'anchor', 'color': 'blue'},
             'default': {'icon': 'asterisk', 'color': 'purple'},
             'ARSON': {'icon': 'house-fire', 'color': 'red'},
             'ASSAULT OFFENSES': {'icon': 'warning', 'color': 'red'},
             'BAD CHECKS': {'icon': 'drivers-license', 'color': 'green'},
             'BURGLARY/BREAKING&ENTERING': {'icon': 'home', 'color': 'red'},
             'COUNTERFEITING/FORGERY': {'icon': 'money', 'color': 'green'},
             'DESTRUCTION/DAMAGE/VANDALISM OF PROPERTY': {'icon': 'warning', 'color': 'orange'},
             'DRIVING UNDER THE INFLUENCE': {'icon': 'car', 'color': 'orange'},
             'DRUG/NARCOTIC OFFENSES': {'icon': 'flask', 'color': 'purple'},
             'FRAUD OFFENSES': {'icon': 'drivers-license', 'color': 'blue'},
             'KIDNAPPING/ABDUCTION': {'icon': 'bolt', 'color': 'red'},
             'LARCENY-THEFT': {'icon': 'money', 'color': 'blue'},
             'MOTOR VEHICLE THEFT': {'icon': 'car', 'color': 'red'},
             'ROBBERY': {'icon': 'warning', 'color': 'red'},
             'SEX OFFENSES': {'icon': 'times-circle', 'color': 'red'},
             'STOLEN PROPERTY OFFENSES': {'icon': 'home', 'color': 'orange'},
             'TRESPASS OF REAL PROPERTY': {'icon': 'home', 'color': 'green'},
             'WEAPON LAW VIOLATIONS': {'icon': 'bomb', 'color': 'orange'},
             'Commercial': {'icon': 'shopping-bag', 'color': 'orange'},
             'Industrial': {'icon': 'industry', 'color': 'orange'},
             'Institutional': {'icon': 'institution', 'color': 'blue'},
             'Multifamily': {'icon': 'users', 'color': 'green'},
             'Single Family/Duplex': {'icon': 'home', 'color': 'green'},
             'Vacant Land': {'icon': 'times-rectangle', 'color': 'orange'},
             'Construction': {'icon': 'fa-gavel', 'color': 'black'},
             'Construction , Noise': {'icon': 'fa-gavel', 'color': 'black'},
             'Construction , Shoreline': {'icon': 'fa-gavel', 'color': 'black'},
             'Construction , Tree': {'icon': 'fa-tree', 'color': 'green'},
             'Emergency , Vacant Building': {'icon': 'fa-home', 'color': 'black'},
             'Land Use': {'icon': 'fa-times-circle', 'color': 'blue'},
             'Land UseConstruction ,': {'icon': 'fa-volume-up', 'color': 'orange'},
             'Land UseConstruction , Noise ,': {'icon': 'fa-gavel', 'color': 'black'},
             'Land UseLandLord/Tenant ,': {'icon': 'fa-leaf', 'color': 'blue'},
             'Land UseTree ,': {'icon': 'fa-tree', 'color': 'green'},
             'Land UseWeeds ,': {'icon': 'fa-leaf', 'color': 'green'},
             'LandLord/Tenant': {'icon': 'fa-user', 'color': 'blue'},
             'LandLord/Tenant , Weeds': {'icon': 'fa-leaf', 'color': 'green'},
             'Noise': {'icon': 'fa-volume-up', 'color': 'red'},
             'Shoreline': {'icon': 'fa-window-close', 'color': 'blue'},
             'Tree': {'icon': 'fa-tree', 'color': 'green'},
             'Vacant Building': {'icon': 'fa-home', 'color': 'black'},
             'Weeds': {'icon': 'fa-leaf', 'color': 'green'}}
