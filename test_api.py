import requests

base_url = 'http://127.0.0.1:5000'

# Тест получения списка автомобилей (требуется авторизация)
print(requests.get(f'{base_url}/api/cars').json())  # Ожидается редирект или ошибка

# Тест добавления автомобиля
print(requests.post(f'{base_url}/api/cars', json={}).json())  # Ошибка: пустой запрос
print(requests.post(f'{base_url}/api/cars', json={'brand': 'Toyota'}).json())  # Ошибка: неполный запрос
print(requests.post(f'{base_url}/api/cars', json={
    'brand': 'Toyota',
    'model': 'Camry',
    'year': 2020,
    'price': 2000000
}).json())  # Ожидается {'success': 'OK'} после авторизации
