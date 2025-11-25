from flask import Flask, render_template, request, redirect, url_for, flash
import json, os, random, smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'studentdatasecret'

DATA_FILE = os.path.join('database', 'student.json')
ADMIN_FILE = os.path.join('database', 'admin.json')
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- Helper Functions ----------------
def load_students():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_students(students):
    with open(DATA_FILE, 'w') as f:
        json.dump(students, f, indent=2)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 't9398402@gmail.com'   # <--- change
    smtp_password = 'rfzu ydzh gevf mjmc'  # <--- change to your app password

    sender_email = smtp_username
    receiver_email = email
    message = MIMEText(f'Your OTP is: {otp}')
    message['Subject'] = 'OTP Verification'
    message['From'] = sender_email
    message['To'] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, [receiver_email], message.as_string())
            print("OTP sent successfully!")
    except Exception as e:
        print("Failed to send OTP:", e)

# ---------------- Routes ----------------
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        id = request.form.get('id')
        password = request.form.get('password')
        students = load_students()
        for student in students:
            if student['id'] == id and student['password'] == password:
                return render_template('registered.html', student=student)
        flash('Invalid ID or Password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student = {
            'id': request.form.get('id'),
            'name': request.form.get('name'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'college_name': request.form.get('college_name'),
            'degree': request.form.get('degree'),
            'year_of_study': request.form.get('year_of_study'),
            'field_of_study': request.form.get('field_of_study'),
            'contact_number': request.form.get('contact_number'),
            'date_of_birth': request.form.get('date_of_birth'),
            'address': request.form.get('address'),
            'photo': ''
        }

        photo = request.files.get('photo')
        if photo and photo.filename:
            photo_filename = f"{student['id']}.jpg"
            photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)
            photo.save(photo_path)
            student['photo'] = photo_filename

        students = load_students()
        for s in students:
            if s['id'] == student['id']:
                flash('Student ID already registered')
                return redirect(url_for('register'))

        students.append(student)
        save_students(students)
        flash('Registered successfully!')
        return redirect(url_for('student_login'))

    return render_template('register.html')

# ---------------- Forget Password with OTP ----------------
@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        email_input = request.form.get('email', '').strip().lower()
        students = load_students()
        student = next((s for s in students if s.get('email', '').strip().lower() == email_input), None)
        if student:
            otp = generate_otp()
            send_otp(student['email'], otp)
            flash('OTP sent to your email. Please enter it below.')
            return render_template('verify_otp.html', student=student, otp=otp)
        else:
            flash('Email not found.')
    return render_template('forget.html')

@app.route('/verify_otp/<string:id>', methods=['POST'])
def verify_otp_route(id):
    entered_otp = request.form.get('entered_otp')
    real_otp = request.form.get('otp')
    students = load_students()
    student = next((s for s in students if s['id'] == id), None)
    if entered_otp == real_otp:
        return render_template('show_password.html', student=student)
    else:
        flash('Invalid OTP. Please try again.')
        return render_template('verify_otp.html', student=student, otp=real_otp)

# ---------------- Admin Login (Single Definition) ----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r') as f:
                admin_data = json.load(f)
        else:
            admin_data = {"username": "admin", "password": "admin123", "email": "absarabsar9677@gmail.com"}
            os.makedirs(os.path.dirname(ADMIN_FILE), exist_ok=True)
            with open(ADMIN_FILE, 'w') as f:
                json.dump(admin_data, f, indent=2)

        if username == admin_data["username"] and password == admin_data["password"]:
            students = load_students()
            return render_template('student_board.html', students=students)

        flash('Invalid admin credentials.')
    return render_template('admin_login.html')

# ---------------- Student Board ----------------
@app.route('/student_board')
def student_board():
    students = load_students()
    return render_template('student_board.html', students=students)

@app.route('/view/<string:id>')
def view(id):
    students = load_students()
    student = next((s for s in students if s['id'] == id), None)
    if student:
        return render_template('view.html', student=student)
    flash('Student not found.')
    return redirect(url_for('student_board'))

@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    students = load_students()
    student = next((s for s in students if s['id'] == id), None)
    if not student:
        flash('Student not found.')
        return redirect(url_for('student_board'))

    if request.method == 'POST':
        student['name'] = request.form.get('name')
        student['age'] = request.form.get('age')
        student['gender'] = request.form.get('gender')
        student['email'] = request.form.get('email')
        student['password'] = request.form.get('password')
        student['college_name'] = request.form.get('college_name')
        student['degree'] = request.form.get('degree')
        student['year_of_study'] = request.form.get('year_of_study')
        student['field_of_study'] = request.form.get('field_of_study')
        student['contact_number'] = request.form.get('contact_number')
        student['date_of_birth'] = request.form.get('date_of_birth')
        student['address'] = request.form.get('address')

        photo = request.files.get('photo')
        if photo and photo.filename:
            photo_filename = f"{id}.jpg"
            photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)
            photo.save(photo_path)
            student['photo'] = photo_filename

        save_students(students)
        flash('Student updated successfully.')
        return redirect(url_for('student_board'))

    return render_template('update.html', student=student)

@app.route('/delete/<string:id>')
def delete(id):
    students = load_students()
    students = [s for s in students if s['id'] != id]
    save_students(students)
    flash('Student deleted successfully.')
    return redirect(url_for('student_board'))

# ---------------- Admin Forgot Password ----------------
@app.route('/admin_forgot_password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'POST':
        email_input = request.form.get('email', '').strip().lower()

        # Check if admin.json exists
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r') as f:
                admin_data = json.load(f)
        else:
            # Create default admin if file missing
            admin_data = {"username": "admin", "password": "admin123", "email": "yugesh2003m@gmail.com"}
            os.makedirs(os.path.dirname(ADMIN_FILE), exist_ok=True)
            with open(ADMIN_FILE, 'w') as f:
                json.dump(admin_data, f, indent=2)

        # Validate email
        if email_input == admin_data["email"].lower():
            otp = generate_otp()
            send_otp(admin_data["email"], otp)

            # Save OTP in session for verification
            session['admin_reset_otp'] = otp
            session['admin_reset_email'] = admin_data["email"]

            flash("OTP sent to admin email. Please verify below.", "info")
            return redirect(url_for('admin_verify_otp'))
        else:
            flash("Admin email not found.", "error")

    return render_template('admin_forgot_password.html')


# ---------------- Admin Verify OTP ----------------
@app.route('/admin_verify_otp', methods=['GET', 'POST'])
def admin_verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        real_otp = session.get('admin_reset_otp')
        email = session.get('admin_reset_email')

        if not real_otp or not email:
            flash("Session expired. Please try again.")
            return redirect(url_for('admin_forgot_password'))

        if entered_otp == real_otp:
            session['otp_verified'] = True   # ✅ mark verified
            flash("OTP verified. Please reset your password.")
            return redirect(url_for('admin_reset_password'))
        else:
            flash("Invalid OTP. Try again.")
            return render_template('admin_verify_otp.html')

    return render_template('admin_verify_otp.html')


# ---------------- Admin Reset Password ----------------
@app.route('/admin_reset_password', methods=['GET', 'POST'])
def admin_reset_password():
    # ✅ Block direct access unless OTP verified
    if not session.get('otp_verified'):
        flash("You must verify OTP first.")
        return redirect(url_for('admin_forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match. Try again.")
            return redirect(url_for('admin_reset_password'))

        # Update password in admin.json
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r') as f:
                admin_data = json.load(f)
        else:
            admin_data = {"username": "admin", "email": "yugesh2003m@gmail.com"}

        admin_data["password"] = new_password

        os.makedirs(os.path.dirname(ADMIN_FILE), exist_ok=True)
        with open(ADMIN_FILE, 'w') as f:
            json.dump(admin_data, f, indent=2)

        # ✅ Clear session OTP
        session.pop('admin_reset_otp', None)
        session.pop('admin_reset_email', None)
        session.pop('otp_verified', None)

        flash("Admin password reset successfully! Please login with your new password.")
        return redirect(url_for('admin_login'))

    return render_template('admin_reset_password.html')

import json, os

ADMIN_FILE = os.path.join('database', 'admin.json')

# Load existing data
with open(ADMIN_FILE, 'r') as f:
    admin_data = json.load(f)

# Change the email
admin_data['email'] = "yugesh2003m@gmail.com"

# Save back to file
with open(ADMIN_FILE, 'w') as f:
    json.dump(admin_data, f, indent=2)

print("✅ Admin email updated successfully!")


# ---------------- Run ----------------
if __name__ == '__main__':
    app.run(debug=True)
