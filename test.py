from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Функция инициализации базы данных (создаёт таблицу, если её нет)
def init_db():
    conn = sqlite3.connect('survey_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            age INTEGER,
            course_ids TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Функция для получения соединения с базой данных
def get_db_connection():
    conn = sqlite3.connect('survey_data.db')
    conn.row_factory = sqlite3.Row  # Для удобства доступа к строкам
    return conn

# Эндпоинт для проверки работы API (GET)
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API работает!"})

# Эндпоинт для отправки анкеты (POST)
@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    data = request.get_json()  # Получаем JSON-данные

    device_id = data.get('device_id')
    age = data.get('age')
    course_ids = data.get('course_ids')

    # Проверка возраста
    if age is None:
        return jsonify({'Ошибка': 'Возраст обязателен!'}), 400
    try:
        age = int(age)
        if age <= 0:
            return jsonify({'Ошибка': 'Если ты только что был зачат, то, возможно, возраст 0 — это нормально! Вот только откуда в утробе взялось устройство?'}), 400
    except ValueError:
        return jsonify({'Ошибка': 'Неверный возраст. Введите корректное число!'}), 400

    # Проверка идентификаторов курсов
    if not course_ids or not isinstance(course_ids, list):
        return jsonify({'Ошибка': 'Идентификаторы курсов должны быть в виде списка!'}), 400

    validated_course_ids = []
    try:
        for cid in course_ids:
            cid_int = int(cid)
            if cid_int <= 0:
                return jsonify({'Ошибка': 'Должны использоваться положительные чилса!'}), 400
            validated_course_ids.append(cid_int)
    except (ValueError, TypeError):
        return jsonify({'Ошибка': 'Возраст вводится в цифровом формате!'}), 400

    # Запись анкеты в базу данных
    try:
        conn = sqlite3.connect('survey_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO survey_responses (device_id, age, course_ids)
            VALUES (?, ?, ?)
        ''', (device_id, age, ','.join(map(str, validated_course_ids))))
        conn.commit()
        conn.close()
        return jsonify({'Поздравляю': 'Анкета успешно отправлена!'})
    except sqlite3.Error as e:
        return jsonify({'Ошибка': f'Ошибка базы данных: {e}'}), 500

# Эндпоинт для получения всех анкет (GET)
@app.route('/surveys', methods=['GET'])
def get_surveys():
    try:
        conn = sqlite3.connect('survey_data.db')
        cursor = conn.cursor()
        # Выбирает только анкеты, где возраст > 0
        cursor.execute("SELECT * FROM survey_responses WHERE age > 0")
        surveys = cursor.fetchall()
        conn.close()

        # Фильтрация записей: выбираем только те, у которых все course_ids положительные числа
        valid_surveys = []
        for survey in surveys:
            try:
                cid_list = list(map(int, survey[3].split(',')))
                if all(cid > 0 for cid in cid_list):
                    valid_surveys.append([survey[0], survey[1], survey[2], survey[3]])
            except Exception:
                continue

        return jsonify(valid_surveys)
    except sqlite3.Error as e:
        return jsonify({'error': f'Ошибка базы данных: {e}'}), 500

# Очистка всех данных в таблице
@app.route('/clear_surveys', methods=['DELETE'])
def clear_surveys():
    try:
        conn = sqlite3.connect('survey_data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM survey_responses")
        conn.commit()
        conn.close()
        return jsonify({"message": "Все данные успешно очищены!"})
    except sqlite3.Error as e:
        return jsonify({'error': f"Database error: {e}"}), 500


if __name__ == '__main__':
    init_db()  # Инициализация базы данных при запуске
    app.run(debug=True)