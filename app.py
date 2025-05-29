from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/photos'
DATA_FILE = 'database/student.json'

def load_students():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_students(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form.get('id')
        password = request.form.get('password')
        students = load_students()
        for student in students:
            if student['id'] == student_id and student['password'] == password:
                return render_template('registered.html', student=student)
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student = {
            "id": request.form.get('id'),
            "name": request.form.get('name'),
            "age": request.form.get('age'),
            "gender": request.form.get('gender'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "college_name": request.form.get('college_name'),
            "degree": request.form.get('degree'),
            "year_of_study": request.form.get('year_of_study'),
            "field_of_study": request.form.get('field_of_study'),
            "contact_number": request.form.get('contact_number'),
            "date_of_birth": request.form.get('date_of_birth'),
            "address": request.form.get('address')
        }
        photo = request.files.get('photo')
        if photo:
            photo_filename = student['id'] + os.path.splitext(photo.filename)[1]
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            student['photo'] = photo_filename
        students = load_students()
        students.append(student)
        save_students(students)
        return render_template('register.html', success="Registered Successfully")
    return render_template('register.html')

@app.route('/admin')
def admin():
    students = load_students()
    return render_template('student_board.html', students=students)

@app.route('/view/<student_id>')
def view(student_id):
    students = load_students()
    for student in students:
        if student['id'] == student_id:
            return render_template('view.html', student=student)
    return "Student not found", 404

@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    students = load_students()
    for student in students:
        if student['id'] == student_id:
            if request.method == 'POST':
                student['name'] = request.form.get('name', student['name'])
                student['age'] = request.form.get('age', student['age'])
                student['gender'] = request.form.get('gender', student['gender'])
                student['email'] = request.form.get('email', student['email'])
                student['college_name'] = request.form.get('college_name', student['college_name'])
                student['degree'] = request.form.get('degree', student['degree'])
                student['year_of_study'] = request.form.get('year_of_study', student['year_of_study'])
                student['field_of_study'] = request.form.get('field_of_study', student['field_of_study'])
                student['contact_number'] = request.form.get('contact_number', student['contact_number'])
                student['date_of_birth'] = request.form.get('date_of_birth', student['date_of_birth'])
                student['address'] = request.form.get('address', student['address'])
                save_students(students)
                return redirect(url_for('admin'))
            return render_template('update.html', student=student)
    return "Student not found", 404

@app.route('/delete/<student_id>')
def delete_student(student_id):
    students = load_students()
    for student in students:
        if student['id'] == student_id:
            if 'photo' in student:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], student['photo'])
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            students.remove(student)
            save_students(students)
            return redirect(url_for('admin'))
    return "Student not found", 404

if __name__ == '__main__':
    app.run(debug=True)
