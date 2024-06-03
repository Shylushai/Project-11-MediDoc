import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

def add_patient(name, age, gender, contact):
    cursor.execute('''
        INSERT INTO Patients (name, age, gender, contact) VALUES (?, ?, ?, ?)
    ''', (name, age, gender, contact))
    conn.commit()

def add_doctor(name, specialty, contact):
    cursor.execute('''
        INSERT INTO Doctors (name, specialty, contact) VALUES (?, ?, ?)
    ''', (name, specialty, contact))
    conn.commit()

def book_appointment(patient_id, doctor_id, date, time, reason):
    cursor.execute('''
        INSERT INTO Appointments (patient_id, doctor_id, date, time, reason) VALUES (?, ?, ?, ?, ?)
    ''', (patient_id, doctor_id, date, time, reason))
    conn.commit()

def get_patients():
    cursor.execute('SELECT * FROM Patients')
    return cursor.fetchall()

def get_doctors():
    cursor.execute('SELECT * FROM Doctors')
    return cursor.fetchall()

def get_appointments():
    cursor.execute('SELECT * FROM Appointments')
    return cursor.fetchall()

def main_menu():
    while True:
        print("\nHospital Patient Appointment System")
        print("1. Add Patient")
        print("2. Add Doctor")
        print("3. Book Appointment")
        print("4. View Patients")
        print("5. View Doctors")
        print("6. View Appointments")
        print("7. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            name = input("Enter patient name: ")
            age = int(input("Enter patient age: "))
            gender = input("Enter patient gender: ")
            contact = input("Enter patient contact: ")
            add_patient(name, age, gender, contact)
            print("Patient added successfully!")
        elif choice == '2':
            name = input("Enter doctor name: ")
            specialty = input("Enter doctor specialty: ")
            contact = input("Enter doctor contact: ")
            add_doctor(name, specialty, contact)
            print("Doctor added successfully!")
        elif choice == '3':
            patient_id = int(input("Enter patient ID: "))
            doctor_id = int(input("Enter doctor ID: "))
            date = input("Enter appointment date (YYYY-MM-DD): ")
            time = input("Enter appointment time (HH:MM): ")
            reason = input("Enter appointment reason: ")
            book_appointment(patient_id, doctor_id, date, time, reason)
            print("Appointment booked successfully!")
        elif choice == '4':
            patients = get_patients()
            print("\nPatients:")
            for patient in patients:
                print(patient)
        elif choice == '5':
            doctors = get_doctors()
            print("\nDoctors:")
            for doctor in doctors:
                print(doctor)
        elif choice == '6':
            appointments = get_appointments()
            print("\nAppointments:")
            for appointment in appointments:
                print(appointment)
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()
