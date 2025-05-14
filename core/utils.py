import requests
LOCATION_CORE_MAP = {
    'server1': ['seeecs', 'c2', 'nbs'],
    'server2': ['nice', 'ric'],
    'server3': ['smme', 'sports_complex', 'swimming_pool', 'c4'],
    'server4': ['scme', 'c1', 'igs', 'sada', 'nbs_ground', 'helipad_ground'],
    'server5': ['library', 'masjid', 'rims', 'iaec'],
    'server6': ['south_edge_cafe', 'main_office', 'library_lawn', 'convocation_ground'],
    'server7': ['gate1', 'gate2', 'gate10'],
    'male_hostels': [
        'rumi_hostel', 'johar_hostel', 'ghazali_hostel', 'beruni_hostel',
        'razi_hostel', 'rahmat_hostel', 'attar_hostel', 'liaquat_hostel',
        'hajveri_hostel', 'zakariya_hostel'
    ],
    'female_hostels': [
        'fatima_block1_pg', 'fatima_block2_pg', 'fatima_block1_ug',
        'zainab_hostel', 'ayesha_hostel', 'khadija_hostel', 'amna_hostel'
    ]
}

def get_solr_core(location_text):
    location_text = location_text.lower()
    for core, locations in LOCATION_CORE_MAP.items():
        if any(location in location_text for location in locations):
            return core
    return None
def geocode_location(location_text):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': location_text,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'nust-lostfound-app'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lon']), float(data['lat'])
    return None
def get_core_for_location(location_text):
    location_text = location_text.lower()
    for core, locations in LOCATION_CORE_MAP.items():
        if any(location in location_text for location in locations):
            return core
    return None