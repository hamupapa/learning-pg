from dotenv import load_dotenv
from flask import Flask, render_template, request

from service.weather import get_weather_by_city

load_dotenv()

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_info = None
    city = ''

    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if city:
            weather_info = get_weather_by_city(city)

    return render_template('index.html', weather_info=weather_info, city=city)


if __name__ == '__main__':
    app.run(debug=True)
