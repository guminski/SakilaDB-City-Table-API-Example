import os
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    make_response,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from models import *

app = Flask(__name__)
LOCAL_DB = os.environ['LOCAL_SAKILA_DB']  #

engine = create_engine(f'postgresql+psycopg2://{LOCAL_DB}', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


class InternalServerError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def make_json_list_response(data):
    city_list = list()
    for city in data:
        city_list.append(city.city)
    city_list.sort()
    return jsonify(city_list)


@app.route('/')
def main_view():
    return render_template('main.html')


@app.route('/counter')
def counter_view():
    count = session.query(Visit).with_for_update().filter_by(id=1).first()
    count.count += 1
    if 'reset' in request.args:
        count.count = 0
    session.commit()
    return str(count.count)


@app.route('/cities', methods=['GET', 'POST'])
def cities_route():
    print(request.method)
    if request.method == 'GET':

        # Getting all possible expected query strings, otherwise - setting as False
        per_page = request.args.get('per_page', False)
        page = request.args.get('page', False)
        country_name = request.args.get('country_name', False)

        # Checking given query strings value and filter data
        if per_page and page and country_name:
            cities = session.query(City).join(Country).filter(Country.country == country_name).limit(
                per_page).offset(int(per_page) * (int(page) - 1)).all()
            return make_json_list_response(cities)

        elif per_page and page:
            cities = session.query(City).limit(per_page).offset(int(per_page) * (int(page) - 1)).all()
            return make_json_list_response(cities)

        elif country_name:
            cities = session.query(City).join(Country).filter(Country.country == country_name).all()
            return make_json_list_response(cities)

        else:
            all_cities = session.query(City)
            return make_json_list_response(all_cities)

    else:
        # getting posted JSON
        posted_json_data = request.get_json()
        country_data_from_json = {
            'country_id': posted_json_data.get('country_id'),
            'city_name': posted_json_data.get('city_name')
        }

        # validate if posted country_id exist
        country_id_data = session.query(Country)
        country_id_list = list()
        for country in country_id_data:
            country_id_list.append(country.country_id)

        if country_data_from_json['country_id'] in country_id_list and 'city_name' in country_data_from_json:

            added_city = City(
                country_id=country_data_from_json['country_id'],
                city=country_data_from_json['city_name'],
                last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            try:
                session.add(added_city)
                session.commit()
            except InternalServerError:
                session.rollback()
                raise InternalServerError('Insert city to db failed', status_code=500)

            # JSON response after success db commit
            add_city_success_data = session.query(City).join(Country).filter(
                City.city == country_data_from_json['city_name']).first()

            add_city_success_json = {
                'country_id': add_city_success_data.country_id,
                'city_name': add_city_success_data.city,
                'city_id': add_city_success_data.id
            }
            return jsonify(add_city_success_json)

        else:
            return make_response(jsonify({"error": "Wrong JSON data"}), 400)


if __name__ == '__main__':
    app.run(debug=True)
