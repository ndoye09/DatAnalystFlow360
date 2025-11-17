"""
Script pour peupler MySQL et MongoDB avec des données de test
Thème: Données cardiovasculaires et santé
"""

import mysql.connector
from pymongo import MongoClient
import random
from datetime import datetime, timedelta
import sys

# Configuration MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': 'Lebou09@',
    'database': 'data_analyst_db'
}

# Configuration MongoDB
MONGO_URI = 'mongodb://localhost:27019/'
MONGO_DB = 'data_analyst_db'

def seed_mysql():
    """Peupler MySQL avec des données de test"""
    print("🔵 Connexion à MySQL...")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Table 1: Patients
        print("📊 Création de la table 'patients'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INT PRIMARY KEY AUTO_INCREMENT,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                age INT,
                gender VARCHAR(10),
                height FLOAT,
                weight FLOAT,
                blood_type VARCHAR(5),
                registration_date DATE
            )
        """)
        
        # Insérer des données
        print("💉 Insertion de 100 patients...")
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 'William', 'Jennifer']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        genders = ['Male', 'Female']
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i in range(100):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            age = random.randint(25, 75)
            gender = random.choice(genders)
            height = round(random.uniform(150, 190), 2)
            weight = round(random.uniform(50, 110), 2)
            blood_type = random.choice(blood_types)
            reg_date = (datetime.now() - timedelta(days=random.randint(0, 365))).date()
            
            cursor.execute("""
                INSERT INTO patients (first_name, last_name, age, gender, height, weight, blood_type, registration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, age, gender, height, weight, blood_type, reg_date))
        
        # Table 2: Medical Tests
        print("📊 Création de la table 'medical_tests'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_tests (
                test_id INT PRIMARY KEY AUTO_INCREMENT,
                patient_id INT,
                test_date DATE,
                cholesterol INT,
                glucose INT,
                systolic_bp INT,
                diastolic_bp INT,
                heart_rate INT,
                test_type VARCHAR(50),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)
        
        print("🩺 Insertion de 300 tests médicaux...")
        test_types = ['Routine Checkup', 'Blood Test', 'ECG', 'Stress Test', 'Cardiac Screening']
        
        for i in range(300):
            patient_id = random.randint(1, 100)
            test_date = (datetime.now() - timedelta(days=random.randint(0, 180))).date()
            cholesterol = random.randint(150, 300)
            glucose = random.randint(70, 200)
            systolic_bp = random.randint(90, 180)
            diastolic_bp = random.randint(60, 120)
            heart_rate = random.randint(55, 110)
            test_type = random.choice(test_types)
            
            cursor.execute("""
                INSERT INTO medical_tests (patient_id, test_date, cholesterol, glucose, systolic_bp, diastolic_bp, heart_rate, test_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (patient_id, test_date, cholesterol, glucose, systolic_bp, diastolic_bp, heart_rate, test_type))
        
        # Table 3: Medications
        print("📊 Création de la table 'medications'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                medication_id INT PRIMARY KEY AUTO_INCREMENT,
                patient_id INT,
                medication_name VARCHAR(100),
                dosage VARCHAR(50),
                frequency VARCHAR(50),
                start_date DATE,
                end_date DATE,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)
        
        print("💊 Insertion de 150 prescriptions...")
        medications = [
            ('Aspirin', '100mg', 'Daily'),
            ('Lisinopril', '10mg', 'Daily'),
            ('Metformin', '500mg', 'Twice Daily'),
            ('Atorvastatin', '20mg', 'Daily'),
            ('Losartan', '50mg', 'Daily'),
            ('Metoprolol', '25mg', 'Twice Daily')
        ]
        
        for i in range(150):
            patient_id = random.randint(1, 100)
            med_name, dosage, frequency = random.choice(medications)
            start_date = (datetime.now() - timedelta(days=random.randint(30, 365))).date()
            end_date = (start_date + timedelta(days=random.randint(30, 180)))
            
            cursor.execute("""
                INSERT INTO medications (patient_id, medication_name, dosage, frequency, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (patient_id, med_name, dosage, frequency, start_date, end_date))
        
        conn.commit()
        print("✅ MySQL: Données insérées avec succès!")
        print(f"   - 100 patients")
        print(f"   - 300 tests médicaux")
        print(f"   - 150 prescriptions")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur MySQL: {e}")
        return False
    
    return True

def seed_mongodb():
    """Peupler MongoDB avec des données de test"""
    print("\n🟢 Connexion à MongoDB...")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        
        # Collection 1: Patient Activities
        print("📊 Création de la collection 'patient_activities'...")
        activities = db['patient_activities']
        activities.delete_many({})  # Nettoyer la collection
        
        print("🏃 Insertion de 200 activités de patients...")
        activity_types = ['Walking', 'Running', 'Cycling', 'Swimming', 'Yoga', 'Gym']
        
        activity_docs = []
        for i in range(200):
            doc = {
                'patient_id': random.randint(1, 100),
                'activity_date': (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
                'activity_type': random.choice(activity_types),
                'duration_minutes': random.randint(15, 120),
                'calories_burned': random.randint(50, 600),
                'heart_rate_avg': random.randint(60, 150),
                'steps': random.randint(1000, 15000) if random.choice(activity_types) in ['Walking', 'Running'] else None
            }
            activity_docs.append(doc)
        
        activities.insert_many(activity_docs)
        
        # Collection 2: Appointments
        print("📊 Création de la collection 'appointments'...")
        appointments = db['appointments']
        appointments.delete_many({})
        
        print("📅 Insertion de 150 rendez-vous...")
        doctors = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Garcia']
        specialties = ['Cardiology', 'General Medicine', 'Endocrinology', 'Nephrology']
        statuses = ['Scheduled', 'Completed', 'Cancelled', 'No-Show']
        
        appt_docs = []
        for i in range(150):
            doc = {
                'patient_id': random.randint(1, 100),
                'appointment_date': (datetime.now() + timedelta(days=random.randint(-30, 60))).isoformat(),
                'doctor_name': random.choice(doctors),
                'specialty': random.choice(specialties),
                'status': random.choice(statuses),
                'duration_minutes': random.choice([15, 30, 45, 60]),
                'notes': f"Appointment notes for patient {random.randint(1, 100)}",
                'follow_up_required': random.choice([True, False])
            }
            appt_docs.append(doc)
        
        appointments.insert_many(appt_docs)
        
        # Collection 3: Vital Signs Logs
        print("📊 Création de la collection 'vital_signs_logs'...")
        vitals = db['vital_signs_logs']
        vitals.delete_many({})
        
        print("❤️ Insertion de 500 relevés de signes vitaux...")
        vital_docs = []
        for i in range(500):
            doc = {
                'patient_id': random.randint(1, 100),
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                'systolic_bp': random.randint(90, 180),
                'diastolic_bp': random.randint(60, 120),
                'heart_rate': random.randint(55, 110),
                'temperature': round(random.uniform(36.0, 38.5), 1),
                'oxygen_saturation': random.randint(92, 100),
                'respiratory_rate': random.randint(12, 20),
                'measurement_method': random.choice(['Manual', 'Automated', 'Wearable Device'])
            }
            vital_docs.append(doc)
        
        vitals.insert_many(vital_docs)
        
        print("✅ MongoDB: Données insérées avec succès!")
        print(f"   - 200 activités de patients")
        print(f"   - 150 rendez-vous")
        print(f"   - 500 relevés de signes vitaux")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("🏥 SEED DATABASES - Cardiovascular Health Data")
    print("=" * 60)
    
    # Seed MySQL
    mysql_success = seed_mysql()
    
    # Seed MongoDB
    mongo_success = seed_mongodb()
    
    print("\n" + "=" * 60)
    if mysql_success and mongo_success:
        print("✅ Toutes les bases de données ont été peuplées avec succès!")
        print("\n📝 Prochaine étape:")
        print("   Relancez l'ETL avec: docker restart datalake-etl")
        print("   Puis vérifiez les logs: docker logs datalake-etl")
    else:
        print("❌ Erreur lors du peuplement des bases de données")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
    