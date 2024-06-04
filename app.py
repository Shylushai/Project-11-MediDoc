from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from flask_bcrypt import Bcrypt
from tenacity import retry, stop_after_attempt, wait_fixed
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)
logging.basicConfig(level=logging.DEBUG)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row
    return conn

# User loader
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'], role=user['role'])
    return None

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

# Retry decorator for database operations
@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def execute_query(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        conn.commit()
    except sqlite3.OperationalError as e:
        logging.error(f"Database operation failed: {e}")
        raise
    finally:
        conn.close()

@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def fetch_query(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        rows = cursor.fetchall()
        return rows
    except sqlite3.OperationalError as e:
        logging.error(f"Database operation failed: {e}")
        raise
    finally:
        conn.close()

@app.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        patients = fetch_query('SELECT * FROM Patients')
        doctors = fetch_query('SELECT * FROM Doctors')
        appointments = fetch_query('SELECT * FROM Appointments')
        users = fetch_query('SELECT * FROM Users')
    else:
        patients = []
        doctors = fetch_query('SELECT * FROM Doctors')
        appointments = fetch_query('SELECT * FROM Appointments WHERE patient_id = ?', (current_user.id,))
    
    return render_template('index.html', patients=patients, doctors=doctors, appointments=appointments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(id=user['id'], username=user['username'], password=user['password'], role=user['role'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/manage_appointments', methods=['POST'])
@login_required
def manage_appointments():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    appointment_id = request.form['appointment_id']
    action = request.form['action']

    if action == 'confirm':
        execute_query('UPDATE Appointments SET status = ? WHERE id = ?', ('Confirmed', appointment_id))
    elif action == 'decline':
        execute_query('UPDATE Appointments SET status = ? WHERE id = ?', ('Declined', appointment_id))

    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']
        try:
            execute_query('INSERT INTO Users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
            flash('Registration successful, please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'error')
    return render_template('register.html')

@app.route('/admin_setup', methods=['GET', 'POST'])
@login_required
def admin_setup():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    suggested_times = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
        "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
        "04:30 PM", "05:00 PM"
    ]

    if request.method == 'POST':
        try:
            # Handle adding department
            if 'department_name' in request.form:
                department_name = request.form['department_name'].strip()
                if department_name:
                    logging.debug(f"Adding department: {department_name}")
                    execute_query('INSERT INTO Departments (name) VALUES (?)', (department_name,))
            
            # Handle adding doctor
            if 'doctor_name' in request.form:
                doctor_name = request.form['doctor_name'].strip()
                specialty = request.form['specialty'].strip()
                contact = request.form['contact'].strip()
                if doctor_name and specialty and contact:
                    logging.debug(f"Adding doctor: {doctor_name}, {specialty}, {contact}")
                    execute_query('INSERT INTO Doctors (name, specialty, contact) VALUES (?, ?, ?)',
                                  (doctor_name, specialty, contact))
            
            # Handle setting time slots
            if 'time_slots_select' in request.form:
                selected_slots = request.form.getlist('time_slots')
                logging.debug(f"Setting time slots: {selected_slots}")
                execute_query('DELETE FROM AvailableTimeSlots')
                for slot in selected_slots:
                    execute_query('INSERT INTO AvailableTimeSlots (time) VALUES (?)', (slot,))
                    
            return redirect(url_for('admin_setup'))

        except sqlite3.IntegrityError as e:
            logging.error(f"Database integrity error: {e}")
            flash('An integrity error occurred while processing your request. Please ensure that no duplicate entries are made.', 'error')
        except sqlite3.OperationalError as e:
            logging.error(f"Database operational error: {e}")
            flash('A database error occurred while processing your request. Please try again.', 'error')

    departments = fetch_query('SELECT * FROM Departments')

    return render_template('admin_setup.html', suggested_times=suggested_times, departments=departments)




@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    execute_query('DELETE FROM Patients WHERE id = ?', (patient_id,))
    return redirect(url_for('index'))

@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    execute_query('DELETE FROM Doctors WHERE id = ?', (doctor_id,))
    return redirect(url_for('index'))

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    execute_query('DELETE FROM Appointments WHERE id = ?', (appointment_id,))
    return redirect(url_for('index'))

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        patient_id = current_user.id
        patient_name = request.form['patient_name']
        contact = request.form['contact']
        email = request.form['email']
        doctor_id = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        reason = request.form['reason'] if request.form['reason'] else 'No message provided'
        execute_query('INSERT INTO Appointments (patient_id, doctor_id, date, time, reason, status) VALUES (?, ?, ?, ?, ?, ?)',
                      (patient_id, doctor_id, date, time, reason, 'Pending'))
        return redirect(url_for('index'))
    departments = fetch_query('SELECT * FROM Departments')
    doctors = fetch_query('SELECT * FROM Doctors')
    available_slots = fetch_query('SELECT * FROM AvailableTimeSlots')
    return render_template('book_appointment.html', departments=departments, doctors=doctors, available_slots=available_slots)

@app.route('/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    if request.method == 'POST':
        role = request.form['role']
        newrole = request.form['newrole']
        print(role)
        print(newrole)
        execute_query("UPDATE Users SET role='{value1}' WHERE id ='{value2}'".format(value1 = newrole, value2 = role))
        users = fetch_query('SELECT * FROM Users')
        return render_template('user_management.html', users=users)
    users = fetch_query('SELECT * FROM Users')
    return render_template('user_management.html', users=users)


@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    if request.method == 'GET':
        execute_query('DELETE FROM Users WHERE id = {value}'.format(value = id))
    execute_query('DELETE FROM Users WHERE id = {value}'.format(value = id))
    return redirect(url_for('user_management'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
