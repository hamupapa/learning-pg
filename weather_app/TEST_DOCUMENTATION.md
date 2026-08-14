# Weather App - テストスイート

weather_app のテストスイート。正常系、異常系、境界値を網羅しています。

## テストの構成

### 1. `tests/test_weather.py` - ビジネスロジックの単体テスト

#### `TestWeatherCodeToLabel` クラス
`weather_code_to_label()` 関数のテスト

**正常系テスト（7件）**
- コード 0～95 の複数パターンで正しいラベルが返されることを確認
- 晴れ、曇り、霧、雨、雪、雷雨など主要な天気コードをカバー

**異常系テスト（3件）**
- 負の値（-1）、範囲外の大きい値（999, 100）で「不明」が返されることを確認

**境界値テスト（2件）**
- 最小有効値（0：晴れ）が正しく処理される
- 最大有効値（99：雷雨（強い雹））が正しく処理される

#### `TestGetWeatherByCity` クラス
`get_weather_by_city()` 関数のテスト

**正常系テスト（4件）**
- 有効な都市名（東京、大阪）で天気情報が正しく返される
- 気温が0度以下（札幌：-5.0°C）の場合に正しく処理される
- 湿度が0%の場合に正しく処理される

**異常系テスト（5件）**
- 存在しない都市名でエラーメッセージが返される
- API タイムアウト時のエラーハンドリング
- API 接続エラー時のエラーハンドリング
- API HTTP エラーの処理
- 不正なレスポンス（気温データがない）の処理

**境界値テスト（4件）**
- 非常に長い都市名（100文字）でも処理される
- 極度に高い気温（60°C）でも処理される
- レスポンスに name フィールドがない場合のフォールバック処理
- 特殊文字を含む都市名での処理

### 2. `tests/test_app.py` - Flask アプリケーションの統合テスト

#### `TestIndexRouteGet` クラス
GET リクエストのテスト

**正常系テスト（4件）**
- GET リクエストで 200 OK が返される
- HTML が返される（Content-Type チェック）
- form 要素が含まれる
- 初期状態では天気情報が表示されていない

#### `TestIndexRoutePost` クラス
POST リクエストのテスト

**正常系テスト（3件）**
- 有効な都市名で天気情報が返される
- 前後のスペースが削除される（strip()）
- 正しい HTML Content-Type で返される

**異常系テスト（3件）**
- 空の都市名では `get_weather_by_city()` が呼ばれない
- スペースのみの都市名では関数が呼ばれない
- 都市が見つからないエラーが処理される

**境界値テスト（4件）**
- 非常に長い都市名（1000文字）でも処理される
- 特殊文字を含む都市名（Saint-Pétersbourg）でも処理される
- 数字を含む都市名（東京123）でも処理される
- city パラメータがない POST リクエストの処理

#### `TestWeatherInfoDisplay` クラス
天気情報の表示に関するテスト

**テスト（2件）**
- 天気情報がテンプレートに正しく渡される
- 入力された都市名がテンプレートに正しく渡される

#### `TestFormState` クラス
フォーム状態のテスト

**テスト（1件）**
- POST 後、入力された都市名がフォームに保持される

## テストケースの統計

| カテゴリ | 件数 |
|---------|------|
| 正常系 | 16件 |
| 異常系 | 11件 |
| 境界値 | 12件 |
| **合計** | **39件** |

## テストの実行方法

### 前提条件
```bash
# requirements.txt から依存パッケージをインストール
pip install -r requirements.txt
```

### すべてのテストを実行
```bash
pytest tests/
```

### 特定のテストファイルを実行
```bash
# weather.py のテストのみ実行
pytest tests/test_weather.py

# app.py のテストのみ実行
pytest tests/test_app.py
```

### 特定のテストクラスを実行
```bash
pytest tests/test_weather.py::TestWeatherCodeToLabel
pytest tests/test_app.py::TestIndexRoutePost
```

### 特定のテストケースを実行
```bash
pytest tests/test_weather.py::TestWeatherCodeToLabel::test_weather_code_0_returns_sunny
```

### 詳細な出力を表示
```bash
pytest tests/ -v
```

### カバレッジを確認（pytest-cov をインストール後）
```bash
pytest tests/ --cov=service --cov=app
```

## テストの特徴

### モックの活用
- `@patch` デコレータで外部 API（geocoding-api.open-meteo.com、api.open-meteo.com）をモック
- HTTP リクエストをシミュレーションして信頼性の高いテストを実現

### エラーハンドリングのテスト
- タイムアウト、接続エラー、HTTP エラーなど実際の障害シナリオをカバー
- エラーメッセージが正しく返されることを確認

### 境界値テストの充実
- 最小値、最大値、極端な値（0、-5、60など）でのテスト
- 長い文字列、特殊文字、数字などのエッジケースをカバー

## 実装時の注意点

### 1. Flask テストクライアント
- `app.config['TESTING'] = True` でテストモードを有効化
- `app.test_client()` でテスト用のクライアントを作成

### 2. Fixtures
- `@pytest.fixture` で Flask テストクライアントを提供
- 複数のテストで共有される

### 3. モックの設定
- `mock_get.side_effect = [mock_geocode_response, mock_weather_response]` で複数の API 呼び出しをシミュレート
- `mock_get.return_value` で単一の API 呼び出しをシミュレート

## カスタマイズの例

### より詳細なシナリオをテストする
```python
# 降雨量や風速の確認など、より詳細な検証を追加
def test_weather_with_detailed_values(mock_get):
    # テストコード...
```

### パフォーマンステストを追加
```python
# API のレスポンス時間をテスト
def test_weather_api_response_time():
    # テストコード...
```

### 統合テストを追加
```python
# 実際の API を使用するテスト（オプション）
@pytest.mark.integration
def test_get_weather_with_real_api():
    # テストコード...
```
