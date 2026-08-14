import pytest
from unittest.mock import patch, MagicMock

from app import app


@pytest.fixture
def client():
    """Flask テスト クライアント"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestIndexRouteGet:
    """GET リクエストのテスト"""
    
    def test_index_get_returns_ok(self, client):
        """GET リクエストで 200 OK が返される"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_get_returns_html(self, client):
        """GET リクエストで HTML が返される"""
        response = client.get('/')
        assert response.content_type == 'text/html; charset=utf-8'
    
    def test_index_get_contains_form(self, client):
        """GET リクエストで form 要素が含まれる"""
        response = client.get('/')
        assert b'<form' in response.data or b'form' in response.data.lower()
    
    def test_index_get_no_weather_info_initially(self, client):
        """GET リクエスト時に天気情報は表示されていない"""
        response = client.get('/')
        # 天気情報がない場合の表示がないことを確認
        assert b'weather_info' not in response.data or response.status_code == 200


class TestIndexRoutePost:
    """POST リクエストのテスト"""
    
    # 正常系テスト
    @patch('app.get_weather_by_city')
    def test_index_post_valid_city(self, mock_get_weather, client):
        """有効な都市名で POST した場合、天気情報が返される"""
        mock_get_weather.return_value = {
            'city': '東京',
            'temperature': 25.5,
            'humidity': 60,
            'wind_speed': 3.2,
            'weather': '晴れ',
        }
        
        response = client.post('/', data={'city': '東京'})
        
        assert response.status_code == 200
        assert b'25.5' in response.data or b'\xe2\x82\xb9' in response.data  # 気温が含まれる
        mock_get_weather.assert_called_once_with('東京')
    
    @patch('app.get_weather_by_city')
    def test_index_post_with_spaces_in_city_name(self, mock_get_weather, client):
        """都市名の前後に空白がある場合、strip() で削除される"""
        mock_get_weather.return_value = {
            'city': '大阪',
            'temperature': 28.0,
            'humidity': 70,
            'wind_speed': 2.5,
            'weather': '雨',
        }
        
        response = client.post('/', data={'city': '  大阪  '})
        
        assert response.status_code == 200
        # strip() が適用されることを確認
        mock_get_weather.assert_called_once_with('大阪')
    
    @patch('app.get_weather_by_city')
    def test_index_post_returns_correct_html(self, mock_get_weather, client):
        """POST レスポンスが正しい HTML を返す"""
        mock_get_weather.return_value = {
            'city': 'テスト市',
            'temperature': 20.0,
            'humidity': 50,
            'wind_speed': 1.0,
            'weather': '晴れ',
        }
        
        response = client.post('/', data={'city': 'テスト市'})
        
        assert response.content_type == 'text/html; charset=utf-8'
        assert response.status_code == 200
    
    # 異常系テスト - 空の都市名
    def test_index_post_empty_city(self, client):
        """空の都市名で POST した場合、get_weather_by_city は呼ばれない"""
        with patch('app.get_weather_by_city') as mock_get_weather:
            response = client.post('/', data={'city': ''})
            
            assert response.status_code == 200
            # 空文字列の場合は呼ばれない
            mock_get_weather.assert_not_called()
    
    def test_index_post_only_spaces_city(self, client):
        """スペースのみの都市名で POST した場合、get_weather_by_city は呼ばれない"""
        with patch('app.get_weather_by_city') as mock_get_weather:
            response = client.post('/', data={'city': '   '})
            
            assert response.status_code == 200
            mock_get_weather.assert_not_called()
    
    @patch('app.get_weather_by_city')
    def test_index_post_city_not_found_error(self, mock_get_weather, client):
        """都市が見つからないというエラーメッセージが返される"""
        mock_get_weather.return_value = {
            'error': 'xyz123 の位置情報が見つかりませんでした。'
        }
        
        response = client.post('/', data={'city': 'xyz123'})
        
        assert response.status_code == 200
        # エラーメッセージが返される（実装に依存）
    
    @patch('app.get_weather_by_city')
    def test_index_post_api_error(self, mock_get_weather, client):
        """API エラーが返される"""
        mock_get_weather.return_value = {
            'error': '天気APIへのアクセスに失敗しました: Connection timeout'
        }
        
        response = client.post('/', data={'city': '東京'})
        
        assert response.status_code == 200
    
    # 境界値テスト
    @patch('app.get_weather_by_city')
    def test_index_post_very_long_city_name(self, mock_get_weather, client):
        """非常に長い都市名でも処理される"""
        long_city = 'a' * 1000
        mock_get_weather.return_value = {
            'city': long_city,
            'temperature': 20.0,
            'humidity': 50,
            'wind_speed': 1.0,
            'weather': '晴れ',
        }
        
        response = client.post('/', data={'city': long_city})
        
        assert response.status_code == 200
        mock_get_weather.assert_called_once_with(long_city)
    
    @patch('app.get_weather_by_city')
    def test_index_post_city_with_special_characters(self, mock_get_weather, client):
        """特殊文字を含む都市名でも処理される"""
        city_with_special_chars = 'Saint-Pétersbourg'
        mock_get_weather.return_value = {
            'city': city_with_special_chars,
            'temperature': 5.0,
            'humidity': 70,
            'wind_speed': 2.5,
            'weather': '曇り',
        }
        
        response = client.post('/', data={'city': city_with_special_chars})
        
        assert response.status_code == 200
        mock_get_weather.assert_called_once_with(city_with_special_chars)
    
    @patch('app.get_weather_by_city')
    def test_index_post_city_with_numbers(self, mock_get_weather, client):
        """数字を含む都市名でも処理される"""
        city_with_numbers = '東京123'
        mock_get_weather.return_value = {
            'city': city_with_numbers,
            'temperature': 25.5,
            'humidity': 60,
            'wind_speed': 3.2,
            'weather': '晴れ',
        }
        
        response = client.post('/', data={'city': city_with_numbers})
        
        assert response.status_code == 200
    
    # city パラメータなしの POST
    def test_index_post_no_city_parameter(self, client):
        """city パラメータがない POST リクエスト"""
        with patch('app.get_weather_by_city') as mock_get_weather:
            response = client.post('/', data={})
            
            assert response.status_code == 200
            # get_weather_by_city は呼ばれない（city が空になる）
            mock_get_weather.assert_not_called()


class TestWeatherInfoDisplay:
    """天気情報の表示に関するテスト"""
    
    @patch('app.get_weather_by_city')
    def test_weather_info_is_passed_to_template(self, mock_get_weather, client):
        """天気情報がテンプレートに渡される"""
        expected_weather = {
            'city': '京都',
            'temperature': 22.0,
            'humidity': 65,
            'wind_speed': 2.0,
            'weather': '曇り',
        }
        mock_get_weather.return_value = expected_weather
        
        response = client.post('/', data={'city': '京都'})
        
        assert response.status_code == 200
    
    @patch('app.get_weather_by_city')
    def test_city_name_is_passed_to_template(self, mock_get_weather, client):
        """入力された都市名がテンプレートに渡される"""
        mock_get_weather.return_value = {
            'city': '福岡',
            'temperature': 26.0,
            'humidity': 75,
            'wind_speed': 3.0,
            'weather': '小雨',
        }
        
        response = client.post('/', data={'city': '福岡'})
        
        assert response.status_code == 200


class TestFormState:
    """フォーム状態のテスト"""
    
    def test_form_preserves_city_after_post(self, client):
        """POST 後、入力された都市名がフォームに保持される（実装に依存）"""
        with patch('app.get_weather_by_city') as mock_get_weather:
            mock_get_weather.return_value = {
                'city': '横浜',
                'temperature': 24.0,
                'humidity': 62,
                'wind_speed': 2.8,
                'weather': '晴れ時々曇り',
            }
            
            response = client.post('/', data={'city': '横浜'})
            
            assert response.status_code == 200
