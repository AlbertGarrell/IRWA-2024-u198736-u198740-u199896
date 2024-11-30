import requests

def get_location(ip_address):
    response = requests.get(f"http://ip-api.com/json/{ip_address}")
    data = response.json()
    if data['status'] == 'success':
        return [data.get('country'), data.get('city')]
    else:
        return None, None