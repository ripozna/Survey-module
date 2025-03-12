from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)  # Создаем экземпляр Flask

# Главная страница с формой
@app.route('/')
def home():
    return render_template('index.html')

# Обработка POST-запроса с данными формы
@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    device_id = request.form.get('device_id')
    age = request.form.get('age')
    course_ids = request.form.get('course_ids')

    # Проверка на пустое поле возраста
    if not age:
        return 'Error: Age is required!', 400

    try:
        age = int(age)
    except ValueError:
        return 'Error: Invalid age. Please enter a valid number.', 400

    # Проверка на отрицательные значения или 0
    if age <= 0:
        return 'Error: Age must be a positive number greater than zero.', 400

    # Преобразуем список курсов из строки в список
    if not course_ids:
        return 'Error: Course IDs are required!', 400
    
    
    course_ids_list = course_ids.split(',')
    if len(course_ids_list) == 1 and course_ids_list[0] == '':
        return 'Ошибка: Если вы вписали несколько ID курсов,то должны использовать запятые.Пример:1,2,3.', 400

    course_ids = [int(course.strip()) for course in course_ids.split(',')]

    
    conn = sqlite3.connect('survey_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO survey_responses (device_id, age, course_ids)
    VALUES (?, ?, ?)
    ''', (device_id, age, ','.join(map(str, course_ids))))

    conn.commit()
    conn.close()

    return 'Ваша форма принята'

if __name__ == '__main__':
    app.run(debug=True)