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
LOCAL_DB = os.environ['LOCAL_SAKILA_DB']    #

engine = create_engine(f'postgresql+psycopg2://{LOCAL_DB}', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


def make_json_list(data):
    city_list = list()
    for city in data:
        city_list.append(city.city)
    city_list.sort()
    return jsonify(city_list)


def query_string_arg_only_country_name():
    country = request.args['country_name']
    cities = session.query(City).join(Country).filter(Country.country == country).all()
    return make_json_list(cities)


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
def cities():
    if request.method == 'GET':
        # validation of possible query strings

        if 'per_page' and 'page' in request.args and 'country_name' not in request.args:
            limit = request.args.get('per_page')
            offset = request.args.get('page')
            cities = session.query(City).limit(limit).offset(int(limit) * (int(offset) - 1)).all()
            return make_json_list(cities)

        elif 'country_name' in request.args and 'page' not in request.args:
            return query_string_arg_only_country_name()

        elif 'per_page' and 'page' and 'country_name' in request.args:
            country_name = request.args['country_name']
            limit = request.args.get('per_page')
            offset = request.args.get('page')
            cities = session.query(City).join(Country).filter(Country.country == country_name).limit(limit).offset(
                int(limit) * (int(offset) - 1)).all()
            return make_json_list(cities)

        else:
            all_cities = session.query(City)
            return make_json_list(all_cities)

    elif request.method == 'POST':
        # getting posted JSON
        posted_json_data = request.get_json()
        country_data_from_json = {
            'country_id': posted_json_data.get('country_id'),
            'city_name': posted_json_data.get('city_name')
        }

        # constructor to validate country IDs and POSTed data
        country_id_data = session.query(Country)
        country_id_list = list()
        for country in country_id_data:
            country_id_list.append(country.country_id)

        if country_data_from_json['country_id'] in country_id_list and 'city_name' in country_data_from_json:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            added_city = City(
                country_id=country_data_from_json['country_id'],
                city=country_data_from_json['city_name'],
                last_update=now
            )

            session.add(added_city)
            session.commit()

            # preparing JSON request after commit to db
            add_city_success_data = session.query(City).join(Country).filter(
                City.city == country_data_from_json['city_name']).first()
            add_city_sucess_json = {
                'country_id': add_city_success_data.country_id,
                'city_name': add_city_success_data.city,
                'city_id': add_city_success_data.id
            }
            return jsonify(add_city_sucess_json)

        else:
            return make_response(jsonify({"error": "Wrong json data"}), 400)


if __name__ == '__main__':
    app.run(debug=True)

