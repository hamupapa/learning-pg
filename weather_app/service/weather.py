import requests


def weather_code_to_label(code):
    mapping = {
        0: '晴れ',
        1: 'ほぼ晴れ',
        2: '晴れ時々曇り',
        3: '曇り',
        45: '霧',
        48: '霧氷',
        51: '小雨',
        53: '雨',
        55: '強い雨',
        56: '氷の雨',
        57: '強い氷の雨',
        61: '小雨',
        63: '雨',
        65: '大雨',
        66: '凍結雨',
        67: '強い凍結雨',
        71: '小雪',
        73: '雪',
        75: '大雪',
        77: 'ひょう',
        80: 'にわか雨',
        81: '強いにわか雨',
        82: '激しいにわか雨',
        85: 'にわか雪',
        86: '強いにわか雪',
        95: '雷雨',
        96: '雷雨（雹）',
        99: '雷雨（強い雹）',
    }
    return mapping.get(code, '不明')


def get_weather_by_city(city):
    try:
        geocode_url = (
            'https://geocoding-api.open-meteo.com/v1/search'
            f'?name={city}&count=1&language=ja&format=json'
        )
        geocode_response = requests.get(geocode_url, timeout=10)
        geocode_response.raise_for_status()
        geodata = geocode_response.json()

        results = geodata.get('results')
        if not results:
            return {'error': f'{city} の位置情報が見つかりませんでした。'}

        place = results[0]
        latitude = place['latitude']
        longitude = place['longitude']
        city_name = place.get('name', city)

        weather_url = (
            'https://api.open-meteo.com/v1/forecast'
            f'?latitude={latitude}&longitude={longitude}'
            '&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code'
            '&timezone=auto'
        )
        weather_response = requests.get(weather_url, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get('current', {})
        return {
            'city': city_name,
            'temperature': current.get('temperature_2m'),
            'humidity': current.get('relative_humidity_2m'),
            'wind_speed': current.get('wind_speed_10m'),
            'weather': weather_code_to_label(current.get('weather_code')),
        }
    except requests.RequestException as exc:
        return {'error': f'天気APIへのアクセスに失敗しました: {exc}'}
