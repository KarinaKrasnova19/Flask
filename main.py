from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Car
from flask_restful import Api, Resource, abort
from functools import wraps
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'super_secret_key'  # Для сессий
api = Api(app)

# Подключение к базе данных
engine = create_engine('sqlite:///cars-collection.db?check_same_thread=False', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Проверка авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'karina' and password == '12345':
            session['logged_in'] = True
            return redirect(url_for('show_cars'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Обработка ошибок 404
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'url not found'}), 404
    return render_template('404.html'), 404

# API: Получение списка автомобилей
@app.route('/api/cars')
@login_required
def get_cars():
    cars = db_session.query(Car).all()
    return jsonify({
        'cars': [item.to_dict(only=('id', 'brand', 'model', 'year', 'price')) for item in cars]
    })

# API: Добавление автомобиля
@app.route('/api/cars', methods=['POST'])
@login_required
def create_car():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['brand', 'model', 'year', 'price']):
        return jsonify({'error': 'Bad request'})
    car = Car(
        brand=request.json['brand'],
        model=request.json['model'],
        year=request.json['year'],
        price=request.json['price']
    )
    db_session.add(car)
    db_session.commit()
    return jsonify({'success': 'OK'})

# API: Работа с конкретным автомобилем
def abort_if_car_not_found(car_id):
    car = db_session.query(Car).get(car_id)
    if not car:
        abort(404, message=f"Car {car_id} not found")

class CarResource(Resource):
    @login_required
    def get(self, car_id):
        abort_if_car_not_found(car_id)
        car = db_session.query(Car).get(car_id)
        return jsonify(car.to_dict(only=('id', 'brand', 'model', 'year', 'price')))

    @login_required
    def delete(self, car_id):
        abort_if_car_not_found(car_id)
        car = db_session.query(Car).get(car_id)
        db_session.delete(car)
        db_session.commit()
        return jsonify({'success': 'OK'})

    @login_required
    def put(self, car_id):
        abort_if_car_not_found(car_id)
        car = db_session.query(Car).get(car_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        data = request.json
        if 'brand' in data:
            car.brand = data['brand']
        if 'model' in data:
            car.model = data['model']
        if 'year' in data:
            car.year = data['year']
        if 'price' in data:
            car.price = data['price']
        db_session.add(car)
        db_session.commit()
        return jsonify({'success': 'OK'})

# Веб-интерфейс: Список автомобилей
@app.route('/')
@app.route('/cars')
@login_required
def show_cars():
    cars = db_session.query(Car).all()
    return render_template('cars.html', cars=cars)

# Веб-интерфейс: Добавление автомобиля
@app.route('/cars/new/', methods=['GET', 'POST'])
@login_required
def new_car():
    if request.method == 'POST':
        new_car = Car(
            brand=request.form['brand'],
            model=request.form['model'],
            year=request.form['year'],
            price=request.form['price']
        )
        db_session.add(new_car)
        db_session.commit()
        return redirect(url_for('show_cars'))
    return render_template('newCar.html')

# Веб-интерфейс: Редактирование автомобиля
@app.route('/cars/<int:car_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    car = db_session.query(Car).filter_by(id=car_id).one()
    if request.method == 'POST':
        if request.form['brand']:
            car.brand = request.form['brand']
        if request.form['model']:
            car.model = request.form['model']
        if request.form['year']:
            car.year = request.form['year']
        if request.form['price']:
            car.price = request.form['price']
        db_session.add(car)
        db_session.commit()
        return redirect(url_for('show_cars'))
    return render_template('editCar.html', car=car)

# Веб-интерфейс: Удаление автомобиля
@app.route('/cars/<int:car_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_car(car_id):
    car = db_session.query(Car).filter_by(id=car_id).one()
    if request.method == 'POST':
        db_session.delete(car)
        db_session.commit()
        return redirect(url_for('show_cars'))
    return render_template('deleteCar.html', car=car)

# Регистрация ресурса API
api.add_resource(CarResource, '/api/cars/<int:car_id>')

if __name__ == '__main__':
    app.run(debug=True)
