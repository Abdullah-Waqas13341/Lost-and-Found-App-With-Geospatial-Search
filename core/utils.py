import requests

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
