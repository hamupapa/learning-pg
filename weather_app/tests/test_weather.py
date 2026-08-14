import pytest
from unittest.mock import patch, MagicMock
import requests

from service.weather import weather_code_to_label, get_weather_by_city


class TestWeatherCodeToLabel:
    """weather_code_to_label 関数のテストスイート"""
    
    # 正常系テスト
    def test_weather_code_0_returns_sunny(self):
        """天気コード 0 は '晴れ' を返す"""
        assert weather_code_to_label(0) == '晴れ'
    
    def test_weather_code_1_returns_mostly_sunny(self):
        """天気コード 1 は 'ほぼ晴れ' を返す"""
        assert weather_code_to_label(1) == 'ほぼ晴れ'
    
    def test_weather_code_3_returns_cloudy(self):
        """天気コード 3 は '曇り' を返す"""
        assert weather_code_to_label(3) == '曇り'
    
    def test_weather_code_45_returns_fog(self):
        """天気コード 45 は '霧' を返す"""
        assert weather_code_to_label(45) == '霧'
    
    def test_weather_code_63_returns_rain(self):
        """天気コード 63 は '雨' を返す"""
        assert weather_code_to_label(63) == '雨'
    
    def test_weather_code_73_returns_snow(self):
        """天気コード 73 は '雪' を返す"""
        assert weather_code_to_label(73) == '雪'
    
    def test_weather_code_95_returns_thunderstorm(self):
        """天気コード 95 は '雷雨' を返す"""
        assert weather_code_to_label(95) == '雷雨'
    
    # 異常系テスト
    def test_unknown_weather_code_negative(self):
        """負の天気コードは '不明' を返す"""
        assert weather_code_to_label(-1) == '不明'
    
    def test_unknown_weather_code_large(self):
        """範囲外の大きい天気コードは '不明' を返す"""
        assert weather_code_to_label(999) == '不明'
    
    def test_unknown_weather_code_100(self):
        """天気コード 100 は '不明' を返す"""
        assert weather_code_to_label(100) == '不明'
    
    # 境界値テスト
    def test_weather_code_minimum_valid(self):
        """最小の有効な天気コード（0）が正しく処理される"""
        result = weather_code_to_label(0)
        assert result == '晴れ'
        assert result != '不明'
    
    def test_weather_code_maximum_valid(self):
        """最大の有効な天気コード（99）が正しく処理される"""
        result = weather_code_to_label(99)
        assert result == '雷雨（強い雹）'
        assert result != '不明'


class TestGetWeatherByCity:
    """get_weather_by_city 関数のテストスイート"""
    
    # 正常系テスト
    @patch('service.weather.requests.get')
    def test_get_weather_valid_city_tokyo(self, mock_get):
        """有効な都市名（東京）で天気情報が正しく返される"""
        # Geocoding API のモック
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': '東京',
                'latitude': 35.6762,
                'longitude': 139.6503,
            }]
        }
        
        # Weather API のモック
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': 25.5,
                'relative_humidity_2m': 60,
                'wind_speed_10m': 3.2,
                'weather_code': 0,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('東京')
        
        assert result['city'] == '東京'
        assert result['temperature'] == 25.5
        assert result['humidity'] == 60
        assert result['wind_speed'] == 3.2
        assert result['weather'] == '晴れ'
        assert 'error' not in result
    
    @patch('service.weather.requests.get')
    def test_get_weather_valid_city_osaka(self, mock_get):
        """有効な都市名（大阪）で天気情報が正しく返される"""
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': '大阪',
                'latitude': 34.6937,
                'longitude': 135.5023,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': 28.0,
                'relative_humidity_2m': 70,
                'wind_speed_10m': 2.5,
                'weather_code': 63,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('大阪')
        
        assert result['city'] == '大阪'
        assert result['temperature'] == 28.0
        assert result['weather'] == '雨'
    
    @patch('service.weather.requests.get')
    def test_get_weather_with_temperature_below_zero(self, mock_get):
        """気温が0度以下の場合に正しく処理される（境界値）"""
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': '札幌',
                'latitude': 43.0642,
                'longitude': 141.3469,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': -5.0,
                'relative_humidity_2m': 40,
                'wind_speed_10m': 5.0,
                'weather_code': 71,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('札幌')
        
        assert result['temperature'] == -5.0
        assert result['weather'] == '小雪'
    
    @patch('service.weather.requests.get')
    def test_get_weather_with_extreme_humidity_values(self, mock_get):
        """湿度が0%と100%の場合に正しく処理される（境界値）"""
        # 湿度 0%
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': 'テスト都市',
                'latitude': 0.0,
                'longitude': 0.0,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'relative_humidity_2m': 0,
                'wind_speed_10m': 0.0,
                'weather_code': 0,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('テスト都市')
        assert result['humidity'] == 0
    
    # 異常系テスト - 都市が見つからない
    @patch('service.weather.requests.get')
    def test_get_weather_city_not_found(self, mock_get):
        """存在しない都市名でエラーメッセージが返される"""
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {'results': []}
        
        mock_get.return_value = mock_geocode_response
        
        result = get_weather_by_city('存在しない都市xyz123')
        
        assert 'error' in result
        assert '存在しない都市xyz123' in result['error']
        assert '位置情報が見つかりません' in result['error']
    
    # 異常系テスト - API エラー
    @patch('service.weather.requests.get')
    def test_get_weather_api_timeout_error(self, mock_get):
        """API がタイムアウトしてもエラーメッセージが返される"""
        mock_get.side_effect = requests.Timeout('Connection timeout')
        
        result = get_weather_by_city('東京')
        
        assert 'error' in result
        assert 'API へのアクセスに失敗' in result['error']
    
    @patch('service.weather.requests.get')
    def test_get_weather_api_connection_error(self, mock_get):
        """API への接続エラーでエラーメッセージが返される"""
        mock_get.side_effect = requests.ConnectionError('Connection failed')
        
        result = get_weather_by_city('東京')
        
        assert 'error' in result
        assert 'API へのアクセスに失敗' in result['error']
    
    @patch('service.weather.requests.get')
    def test_get_weather_api_http_error(self, mock_get):
        """API が HTTP エラーを返してもエラーメッセージが返される"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')
        mock_get.return_value = mock_response
        
        result = get_weather_by_city('東京')
        
        assert 'error' in result
        assert 'API へのアクセスに失敗' in result['error']
    
    # 異常系テスト - 不正なレスポンス
    @patch('service.weather.requests.get')
    def test_get_weather_missing_temperature(self, mock_get):
        """気温データがない場合に None が返される"""
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': '東京',
                'latitude': 35.6762,
                'longitude': 139.6503,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'relative_humidity_2m': 60,
                'wind_speed_10m': 3.2,
                'weather_code': 0,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('東京')
        
        assert result['temperature'] is None
        assert result['city'] == '東京'
    
    # 境界値テスト
    @patch('service.weather.requests.get')
    def test_get_weather_city_name_very_long(self, mock_get):
        """非常に長い都市名でも処理される"""
        long_city_name = 'a' * 100
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': long_city_name,
                'latitude': 0.0,
                'longitude': 0.0,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'relative_humidity_2m': 50,
                'wind_speed_10m': 1.0,
                'weather_code': 0,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city(long_city_name)
        
        assert result['city'] == long_city_name
        assert 'error' not in result
    
    @patch('service.weather.requests.get')
    def test_get_weather_temperature_extreme_hot(self, mock_get):
        """極度に高い気温でも処理される（境界値）"""
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'name': '砂漠',
                'latitude': 0.0,
                'longitude': 0.0,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': 60.0,
                'relative_humidity_2m': 10,
                'wind_speed_10m': 5.0,
                'weather_code': 0,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('砂漠')
        
        assert result['temperature'] == 60.0
    
    @patch('service.weather.requests.get')
    def test_get_weather_no_city_name_in_results(self, mock_get):
        """レスポンスに name フィールドがない場合"""
        mock_geocode_response = MagicMock()
        mock_geocode_response.json.return_value = {
            'results': [{
                'latitude': 35.6762,
                'longitude': 139.6503,
            }]
        }
        
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'relative_humidity_2m': 50,
                'wind_speed_10m': 1.0,
                'weather_code': 0,
            }
        }
        
        mock_get.side_effect = [mock_geocode_response, mock_weather_response]
        
        result = get_weather_by_city('テスト')
        
        # フォールバックとして元の都市名が使われる
        assert result['city'] == 'テスト'
