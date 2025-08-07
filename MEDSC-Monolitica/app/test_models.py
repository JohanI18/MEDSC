import unittest
from sqlalchemy import create_engine, inspect, text
from unittest.mock import MagicMock
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from datetime import date, datetime

from models import (
    Base, Patient, Doctor, Attention, Allergy, Credentials, Diagnostic,
    EmergencyContact, FamilyBackground, Histopathology, Imaging, Laboratory,
    PreExistingCondition, RegionalPhysicalExamination, ReviewOrgansSystem, Treatment
)

# --- Configuración de la Base de Datos de Prueba ---
MYSQL_USER = "usuario"
MYSQL_PASSWORD = "pass123"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = "3306"
MYSQL_DATABASE_TEST = "clinic"

DATABASE_URL_TEST = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE_TEST}?charset=utf8mb4"

class TestModels(unittest.TestCase):
    engine = None
    SessionLocal = None

    #Se conecta al servidor MySQL (sin especificar una base de datos inicialmente).
    #Ejecuta CREATE DATABASE IF NOT EXISTS clinic_test ... para asegurar que la base de datos de prueba exista.
    #Crea un motor (engine) de SQLAlchemy conectado a clinic_test.
    #Crea todas las tablas definidas en models.py (Base.metadata.create_all()) en la base de datos clinic_test.
    #Configura SessionLocal para crear sesiones de base de datos.

    @classmethod
    def setUpClass(cls):
        """
        Se ejecuta una vez antes de todas las pruebas en la clase.
        Crea la base de datos de prueba si no existe y las tablas.
        """
        # Conexión al servidor MySQL para crear la base de datos de prueba si no existe
        # temp_engine = create_engine(f"mysql+mysqlclient://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}?charset=utf8mb4") # Comenta o elimina esta
        temp_engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}?charset=utf8mb4") # Nueva línea
        with temp_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE_TEST} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"))
            connection.commit() # commit para CREATE DATABASE
        temp_engine.dispose()

        cls.engine = create_engine(DATABASE_URL_TEST)
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    #Elimina todas las tablas (Base.metadata.drop_all()) de la base de datos clinic_test.
    #(Opcionalmente, comentado) Podría eliminar la base de datos clinic_test.
    #Libera los recursos del motor (engine.dispose()).

    @classmethod
    def tearDownClass(cls):
        """
        Se ejecuta una vez después de todas las pruebas en la clase.
        Elimina todas las tablas.
        Opcionalmente, podrías eliminar la base de datos de prueba aquí.
        """
        if cls.engine:
            Base.metadata.drop_all(bind=cls.engine)
            # Para eliminar la base de datos de prueba (¡cuidado!):
            # temp_engine = create_engine(f"mysql+mysqlclient://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}?charset=utf8mb4")
            # with temp_engine.connect() as connection:
            #     connection.execute(f"DROP DATABASE IF EXISTS {MYSQL_DATABASE_TEST}")
            #     connection.commit()
            # temp_engine.dispose()
            cls.engine.dispose()

    # Antes de cada prueba, establece una nueva conexión a la base de datos.
    # Inicia una transacción (self.trans).
    # Crea una sesión de SQLAlchemy (self.session) vinculada a esta conexión.

    def setUp(self):
        """
        Se ejecuta antes de cada método de prueba.
        Inicia una transacción y crea una sesión.
        """
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        self.session = self.SessionLocal(bind=self.connection)

    # Después de cada prueba, cierra la sesión.
    # Hace rollback de la transacción (esto revierte todos los cambios hechos en la base de datos durante la prueba, asegurando que cada prueba comience con un estado limpio).
    # Cierra la conexión.

    def tearDown(self):
        """
        Se ejecuta después de cada método de prueba.
        Hace rollback de la transacción y cierra la sesión/conexión.
        Esto asegura que cada prueba comience con una base de datos limpia.
        """
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    # --- Pruebas para Patient ---

    # Verifica que se pueda crear y guardar un nuevo paciente (Patient) con datos válidos.
    # Comprueba que los datos recuperados coincidan con los ingresados (ej. firstName, identifierType).
    # Asegura que los campos de auditoría (created_at, updated_at) se establezcan automáticamente.
    # Verifica que is_deleted sea False por defecto.

    def test_create_patient(self):
        patient_data = {
            "identifierType": "Cedula",
            "identifierCode": "1234567890",
            "firstName": "Juan",
            "lastName1": "Perez",
            "address": "Calle Falsa 123",
            "birthdate": date(1990, 1, 1),
            "gender": "Masculino",
            "sex": "Masculino",
            "civilStatus": "Soltero/a",
            "bloodType": "O+"
        }
        new_patient = Patient(**patient_data)
        self.session.add(new_patient)
        self.session.commit()

        retrieved_patient = self.session.query(Patient).filter_by(identifierCode="1234567890").first()
        self.assertIsNotNone(retrieved_patient)
        self.assertEqual(retrieved_patient.firstName, "Juan")
        self.assertEqual(retrieved_patient.identifierType, "Cedula")
        self.assertIsNotNone(retrieved_patient.created_at)
        self.assertIsNotNone(retrieved_patient.updated_at)
        self.assertEqual(retrieved_patient.is_deleted, False)

    #Prueba la restricción UNIQUE en la columna identifierCode de Patient.
    #Intenta crear dos pacientes con el mismo identifierCode y espera que se lance una IntegrityError.

    def test_patient_identifier_code_unique(self):
        patient1 = Patient(identifierType="Cedula", identifierCode="UNIQUE001", firstName="Ana", lastName1="Gomez", address="Dir", birthdate=date(1980,1,1))
        self.session.add(patient1)
        self.session.commit()

        patient2_data = Patient(identifierType="Pasaporte", identifierCode="UNIQUE001", firstName="Pedro", lastName1="Luna", address="Dir2", birthdate=date(1990,1,1))
        self.session.add(patient2_data)
        with self.assertRaises(IntegrityError): # Esperamos un error de integridad por la restricción UNIQUE
            self.session.commit()
        self.session.rollback() # Importante para limpiar la sesión después de un error esperado

    # Intenta crear un paciente con un valor inválido para el campo identifierType (que es un Enum).
    # Espera que se lance una excepción (ValueError, DataError, IntegrityError, o StatementError) debido a la validación del Enum.

    def test_patient_invalid_enum(self):
        # Añadimos StatementError a las excepciones esperadas
        with self.assertRaises((ValueError, DataError, IntegrityError, StatementError)):
            patient_data = {
                "identifierType": "TipoInvalido", # Valor inválido para el ENUM
                "identifierCode": "9876543210",
                "firstName": "Maria",
                "lastName1": "Lopez",
                "address": "Avenida Siempre Viva 742",
                "birthdate": date(1985, 5, 15)
            }
            new_patient = Patient(**patient_data)
            self.session.add(new_patient)
            self.session.commit()
        self.session.rollback() # Asegúrate de que el rollback esté fuera del with,
                               # pero es mejor que esté aquí si el commit falla.
                               # Si el commit tiene éxito (lo cual no debería en esta prueba),
                               # el rollback limpiará. Si el commit falla, la sesión
                               # ya está en un estado "malo" y el rollback en tearDown la limpiará.

        # Crea un paciente.
    
    # Crea un paciente.
    # Modifica el atributo is_deleted a True y guarda.
    # Verifica que el paciente recuperado tenga is_deleted como True.
    # Verifica que una consulta que filtre por is_deleted=False no devuelva este paciente.

    def test_soft_delete_patient(self):
        patient = Patient(
            identifierType="Cedula", identifierCode="SOFTDEL01", firstName="Soft",
            lastName1="Delete", address="Test Address", birthdate=date(1990, 1, 1)
        )
        self.session.add(patient)
        self.session.commit()
        
        patient_id = patient.id
        
        # Realizar soft delete
        patient.is_deleted = True
        self.session.commit()
        
        # Recuperar el paciente (debería estar marcado como eliminado)
        deleted_patient = self.session.query(Patient).filter_by(id=patient_id).first()
        self.assertIsNotNone(deleted_patient)
        self.assertTrue(deleted_patient.is_deleted)
        
        # Una consulta típica podría filtrar los eliminados
        active_patient = self.session.query(Patient).filter_by(id=patient_id, is_deleted=False).first()
        self.assertIsNone(active_patient)

    # --- Pruebas para Doctor ---

    # Verifica que se pueda crear y guardar un nuevo doctor (Doctor) con datos válidos.
    # Comprueba que los datos recuperados coincidan con los ingresados (ej. speciality, email).

    def test_create_doctor(self):
        doctor_data = {
            "identifierCode": "DOC001",
            "firstName": "Carlos",
            "lastName1": "Sanchez",
            "phoneNumber": "555-1234",
            "address": "Consultorio 101",
            "gender": "Masculino",
            "sex": "Masculino",
            "speciality": "Cardiología",
            "email": "carlos.sanchez@example.com"
        }
        new_doctor = Doctor(**doctor_data)
        self.session.add(new_doctor)
        self.session.commit()

        retrieved_doctor = self.session.query(Doctor).filter_by(identifierCode="DOC001").first()
        self.assertIsNotNone(retrieved_doctor)
        self.assertEqual(retrieved_doctor.speciality, "Cardiología")
        self.assertEqual(retrieved_doctor.email, "carlos.sanchez@example.com")

    # Prueba la restricción UNIQUE en la columna email de Doctor.
    # Intenta crear dos doctores con el mismo email y espera una IntegrityError.

    def test_doctor_email_unique(self):
        doc1 = Doctor(identifierCode="DOC_A", firstName="A", lastName1="B", phoneNumber="1", address="C", gender="Masculino", sex="Masculino", speciality="D", email="test@example.com")
        self.session.add(doc1)
        self.session.commit()

        doc2 = Doctor(identifierCode="DOC_B", firstName="E", lastName1="F", phoneNumber="2", address="G", gender="Femenino", sex="Femenino", speciality="H", email="test@example.com")
        self.session.add(doc2)
        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()

    # --- Pruebas para Attention y Relaciones ---

    # Crea un Patient y un Doctor.
    # Crea una Attention vinculada a ese paciente y doctor.
    # Verifica que la Attention se guarde correctamente y que los datos coincidan.
    # Comprueba que las relaciones funcionen:
    #     Se puede acceder al patient desde la attention (retrieved_attention.patient).
    #     Se puede acceder al doctor desde la attention (retrieved_attention.doctor).
    #     La attention creada aparezca en la lista patient.attentions y doctor.attentions (relaciones inversas).

    def test_create_attention_with_relations(self):
        # Crear Paciente
        patient = Patient(identifierType="Cedula", identifierCode="PAT001ATT", firstName="Laura", lastName1="Velez", address="Casa", birthdate=date(1995,3,3))
        self.session.add(patient)
        # Crear Doctor
        doctor = Doctor(identifierCode="DOC001ATT", firstName="Roberto", lastName1="Dias", phoneNumber="123", address="Hosp", gender="Masculino", sex="Masculino", speciality="General", email="roberto.dias@att.com")
        self.session.add(doctor)
        self.session.commit() # Commit para obtener IDs

        attention_data = {
            "date": datetime.now(),
            "reasonConsultation": "Dolor de cabeza",
            "currentIllness": "Migraña",
            "evolution": "Estable",
            "idPatient": patient.id,
            "idDoctor": doctor.id
        }
        new_attention = Attention(**attention_data)
        self.session.add(new_attention)
        self.session.commit()

        retrieved_attention = self.session.query(Attention).filter_by(id=new_attention.id).first()
        self.assertIsNotNone(retrieved_attention)
        self.assertEqual(retrieved_attention.reasonConsultation, "Dolor de cabeza")
        self.assertIsNotNone(retrieved_attention.patient)
        self.assertEqual(retrieved_attention.patient.firstName, "Laura")
        self.assertIsNotNone(retrieved_attention.doctor)
        self.assertEqual(retrieved_attention.doctor.firstName, "Roberto")

        # Probar relación inversa
        self.assertIn(retrieved_attention, patient.attentions)
        self.assertIn(retrieved_attention, doctor.attentions)


    # --- Pruebas para Allergy y relación con Patient (cascade delete-orphan) ---

    # Crea un Patient.
    # Crea múltiples Allergy asociadas a ese paciente (usando idPatient y asignación directa de objeto).
    # Verifica que el paciente recuperado tenga la cantidad correcta de alergias y que los datos sean correctos.
    # Prueba el comportamiento cascade="all, delete-orphan":
    #     Elimina el Patient.
    #     Verifica que el Patient ya no exista.
    #     Verifica que las Allergy asociadas también hayan sido eliminadas de la base de datos.

    def test_patient_allergy_relationship_and_cascade(self):
        patient = Patient(identifierType="Pasaporte", identifierCode="PATALL001", firstName="Sofia", lastName1="Rey", address="Apto 1", birthdate=date(2000,10,10))
        self.session.add(patient)
        self.session.commit()

        allergy1 = Allergy(allergies="Polen", idPatient=patient.id)
        allergy2 = Allergy(allergies="Maní", patient=patient) # También se puede asignar por objeto
        self.session.add_all([allergy1, allergy2])
        self.session.commit()

        retrieved_patient = self.session.query(Patient).filter_by(id=patient.id).first()
        self.assertEqual(len(retrieved_patient.allergies), 2)
        self.assertTrue(any(a.allergies == "Polen" for a in retrieved_patient.allergies))

        # Probar cascade="all, delete-orphan"
        allergy_id_to_check = allergy1.id
        self.session.delete(patient)
        self.session.commit()

        deleted_patient = self.session.query(Patient).filter_by(id=patient.id).first()
        self.assertIsNone(deleted_patient) # Asumiendo que no hay soft delete en este nivel
        
        # Verificar que las alergias fueron borradas por la cascada
        # Nota: Si Patient tuviera un soft_delete, las alergias no se borrarían por la cascada
        # a menos que la lógica de soft_delete también maneje las cascadas.
        # SQLAlchemy "delete-orphan" se activa cuando el hijo es desasociado O el padre es borrado.
        orphan_allergy = self.session.query(Allergy).filter_by(id=allergy_id_to_check).first()
        self.assertIsNone(orphan_allergy)

    # --- Pruebas para Credentials ---

    # Crea un Doctor.
    # Crea Credentials para ese doctor, vinculando idUser al doctor.id y userType a 'doctor'.
    # Verifica que las credenciales se guarden y que la relación credentials.doctor apunte al doctor correcto.

    def test_create_credentials_for_doctor(self):
        doctor = Doctor(
            identifierCode="CRDOC001", firstName="Dr.", lastName1="House",
            phoneNumber="555-000", address="Hospital", gender="Masculino",
            sex="Masculino", speciality="Diagnóstico", email="house@example.com"
        )
        self.session.add(doctor)
        self.session.commit() # Para obtener doctor.id

        credentials_data = {
            "identifierCode": "CRDOC001", # Debe coincidir con Doctor.identifierCode
            "password": "hashed_password_here", # En una app real, esto estaría hasheado
            "idUser": doctor.id,
            "userType": "doctor"
        }
        new_credentials = Credentials(**credentials_data)
        self.session.add(new_credentials)
        self.session.commit()

        retrieved_credentials = self.session.query(Credentials).filter_by(idUser=doctor.id, userType="doctor").first()
        self.assertIsNotNone(retrieved_credentials)
        self.assertEqual(retrieved_credentials.identifierCode, "CRDOC001")
        self.assertIsNotNone(retrieved_credentials.doctor) # Probar la relación
        self.assertEqual(retrieved_credentials.doctor.firstName, "Dr.")

    # Crea un Patient.
    # Crea Credentials para ese paciente, vinculando idUser al patient.id y userType a 'patient'.
    # Verifica que las credenciales se guarden y que la relación credentials.doctor sea None (ya que es para un paciente).

    def test_create_credentials_for_patient(self):
        patient = Patient(
            identifierType="GeneratedIdentifier", identifierCode="CRPAT001",
            firstName="John", lastName1="Doe", address="Anytown", birthdate=date(1970, 1, 1)
        )
        self.session.add(patient)
        self.session.commit() # Para obtener patient.id

        credentials_data = {
            "identifierCode": "CRPAT001", # Debe coincidir con Patient.identifierCode
            "password": "another_hashed_password",
            "idUser": patient.id,
            "userType": "patient"
        }
        new_credentials = Credentials(**credentials_data)
        self.session.add(new_credentials)
        self.session.commit()

        retrieved_credentials = self.session.query(Credentials).filter_by(idUser=patient.id, userType="patient").first()
        self.assertIsNotNone(retrieved_credentials)
        self.assertEqual(retrieved_credentials.identifierCode, "CRPAT001")
        # Aquí, la relación 'doctor' en Credentials debería ser None
        self.assertIsNone(retrieved_credentials.doctor)

    # Prueba la restricción UniqueConstraint('identifierCode', 'userType', ...) en Credentials.
    # Crea credenciales para un doctor.
    # Intenta crear otras credenciales con el mismo identifierCode y userType='doctor' (pero diferente idUser), esperando una IntegrityError.
    # Verifica que SÍ se puedan crear credenciales con el mismo identifierCode si el userType es diferente (ej. 'patient').

    def test_credentials_unique_constraint(self):
        # Crear un doctor y sus credenciales
        doctor1 = Doctor(identifierCode="UNIQUE_CRED_DOC", firstName="Test", lastName1="Doc", phoneNumber="1", address="A", gender="Masculino", sex="Masculino", speciality="B", email="uniquecred@doc.com")
        self.session.add(doctor1)
        self.session.commit()
        
        cred1 = Credentials(identifierCode="ID_CODE_123", password="p1", idUser=doctor1.id, userType="doctor")
        self.session.add(cred1)
        self.session.commit()

        # Intentar crear otras credenciales con el mismo identifierCode y userType DEBE fallar
        cred2_fail = Credentials(identifierCode="ID_CODE_123", password="p2", idUser=doctor1.id + 1, userType="doctor") # Otro idUser pero mismo idCode y type
        self.session.add(cred2_fail)
        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()

        # Pero con diferente userType DEBERÍA funcionar
        patient1 = Patient(identifierType="Cedula", identifierCode="ID_CODE_123", firstName="Test", lastName1="Patient", address="B", birthdate=date(2000,1,1))
        self.session.add(patient1)
        self.session.commit()

        cred3_ok = Credentials(identifierCode="ID_CODE_123", password="p3", idUser=patient1.id, userType="patient")
        self.session.add(cred3_ok)
        self.session.commit() # Esto debería funcionar
        self.assertIsNotNone(cred3_ok.id)

    # --- Pruebas para Diagnostic y relación con Attention ---

    # Crea un Patient, Doctor y una Attention asociada.
    # Crea un Diagnostic vinculado a esa Attention.
    # Verifica que el diagnóstico se guarde correctamente y que los datos sean correctos.
    # Comprueba que la relación diagnostic.attention funcione y que el diagnóstico aparezca en attention.diagnostics.

    def test_create_diagnostic(self):
        # Preparar datos para Attention
        patient = Patient(identifierType="Cedula", identifierCode="PATDIAG01", firstName="Diag", lastName1="Nostico", address="C", birthdate=date(1988,8,8))
        doctor = Doctor(identifierCode="DOCDIAG01", firstName="Dr.", lastName1="Diag", phoneNumber="456", address="HospDiag", gender="Femenino", sex="Femenino", speciality="Interna", email="dr.diag@example.com")
        self.session.add_all([patient, doctor])
        self.session.commit()
        attention = Attention(date=datetime.now(), reasonConsultation="Checkup", currentIllness="None", evolution="Good", idPatient=patient.id, idDoctor=doctor.id)
        self.session.add(attention)
        self.session.commit()

        diagnostic_data = {
            "cie10Code": "A001",
            "disease": "Cólera debido a Vibrio cholerae 01, biotipo cholerae",
            "observations": "Paciente presenta síntomas clásicos.",
            "diagnosticCondition": "Confirmado",
            "chronology": "Agudo",
            "idAttention": attention.id
        }
        new_diagnostic = Diagnostic(**diagnostic_data)
        self.session.add(new_diagnostic)
        self.session.commit()

        retrieved_diagnostic = self.session.query(Diagnostic).filter_by(id=new_diagnostic.id).first()
        self.assertIsNotNone(retrieved_diagnostic)
        self.assertEqual(retrieved_diagnostic.cie10Code, "A001")
        self.assertIsNotNone(retrieved_diagnostic.attention)
        self.assertEqual(retrieved_diagnostic.attention.id, attention.id)
        self.assertIn(retrieved_diagnostic, attention.diagnostics)

    # --- Pruebas para EmergencyContact y relación con Patient ---

    # Crea un Patient.
    # Crea un EmergencyContact asociado a ese paciente.
    # Verifica que el contacto de emergencia se guarde.
    # Comprueba que el paciente recuperado tenga el contacto de emergencia en su lista patient.emergency_contacts y que los datos del contacto sean correctos. (Nota: la línea con MagicMock() en el código original era un placeholder y, si se elimina o se usa joinedload correctamente, la prueba valida la relación).

    def test_create_emergency_contact(self):
        patient = Patient(identifierType="Pasaporte", identifierCode="PATEMERG01", firstName="Emer", lastName1="Gency", address="Contact St.", birthdate=date(1975,4,12))
        self.session.add(patient)
        self.session.commit()

        ec_data = {
            "firstName": "Contacto",
            "lastName": "Emergencia",
            "address": "Misma Calle",
            "relationship": "Esposa",
            "phoneNumber1": "555-6789",
            "idPatient": patient.id
        }
        new_ec = EmergencyContact(**ec_data)
        self.session.add(new_ec)
        self.session.commit()

        retrieved_patient = self.session.query(Patient).filter_by(id=patient.id).options(
            # Carga ansiosa para asegurar que se prueba la relación
            MagicMock() # Esto es solo para evitar un error si no tienes `joinedload` importado
            # from sqlalchemy.orm import joinedload
            # .options(joinedload(Patient.emergency_contacts))
        ).first()
        self.assertIsNotNone(retrieved_patient)
        self.assertEqual(len(retrieved_patient.emergency_contacts), 1)
        self.assertEqual(retrieved_patient.emergency_contacts[0].firstName, "Contacto")
        self.assertEqual(retrieved_patient.emergency_contacts[0].patient.id, patient.id)

    # --- Pruebas para FamilyBackground ---

    # Crea un Patient.
    # Crea un FamilyBackground asociado a ese paciente.
    # Verifica que se guarde y que el paciente recuperado tenga el antecedente en patient.family_backgrounds.
    # Comprueba un valor Enum (degreeRelationship).

    def test_create_family_background(self):
        patient = Patient(identifierType="Cedula", identifierCode="PATFAM01", firstName="Fam", lastName1="Background", address="Historial St.", birthdate=date(1992,11,30))
        self.session.add(patient)
        self.session.commit()

        fb_data = {
            "familyBackground": "Padre con Hipertensión",
            "time": date(2020, 1, 1), # Fecha del diagnóstico del familiar o relevante
            "degreeRelationship": "1", # ENUM
            "idPatient": patient.id
        }
        new_fb = FamilyBackground(**fb_data)
        self.session.add(new_fb)
        self.session.commit()

        retrieved_patient = self.session.query(Patient).filter_by(id=patient.id).first()
        self.assertIsNotNone(retrieved_patient.family_backgrounds)
        self.assertEqual(len(retrieved_patient.family_backgrounds), 1)
        self.assertEqual(retrieved_patient.family_backgrounds[0].degreeRelationship, "1")

    # --- Pruebas para PreExistingCondition ---

    # Crea un Patient.
    # Crea una PreExistingCondition asociada.
    # Verifica que se guarde y que el paciente recuperado la tenga en patient.pre_existing_conditions.
    def test_create_pre_existing_condition(self):
        patient = Patient(identifierType="Cedula", identifierCode="PATPREEX01", firstName="Pre", lastName1="Existing", address="Condition Av.", birthdate=date(1960,7,7))
        self.session.add(patient)
        self.session.commit()

        pec_data = {
            "diseaseName": "Diabetes Mellitus Tipo 2",
            "time": date(2010, 5, 15),
            "medicament": "Metformina",
            "treatment": "Dieta y ejercicio",
            "idPatient": patient.id
        }
        new_pec = PreExistingCondition(**pec_data)
        self.session.add(new_pec)
        self.session.commit()
        
        retrieved_patient = self.session.query(Patient).filter_by(id=patient.id).first()
        self.assertIsNotNone(retrieved_patient.pre_existing_conditions)
        self.assertEqual(len(retrieved_patient.pre_existing_conditions), 1)
        self.assertEqual(retrieved_patient.pre_existing_conditions[0].diseaseName, "Diabetes Mellitus Tipo 2")

    # --- Pruebas para tablas hijas de Attention (Histopathology, Imaging, Laboratory, etc.) ---
    # Ejemplo para Histopathology, los otros serían similares

    # Crea Patient, Doctor y Attention.
    # Crea una Histopathology vinculada a la Attention.
    # Verifica que se guarde y que la Attention recuperada la tenga en attention.histopathologies.
    def test_create_histopathology(self):
        patient = Patient(identifierType="Cedula", identifierCode="PATHISTO01", firstName="Histo", lastName1="Pat", address="C", birthdate=date(1988,8,8))
        doctor = Doctor(identifierCode="DOCHISTO01", firstName="Dr.", lastName1="Histo", phoneNumber="456", address="HospDiag", gender="Femenino", sex="Femenino", speciality="Patología", email="dr.histo@example.com")
        self.session.add_all([patient, doctor])
        self.session.commit()
        attention = Attention(date=datetime.now(), reasonConsultation="Biopsia", currentIllness="Nódulo", evolution="Pendiente", idPatient=patient.id, idDoctor=doctor.id)
        self.session.add(attention)
        self.session.commit()

        histo_data = {
            "histopathology": "Reporte de biopsia: hallazgos benignos.",
            "idAttention": attention.id
        }
        new_histo = Histopathology(**histo_data)
        self.session.add(new_histo)
        self.session.commit()

        retrieved_attention = self.session.query(Attention).filter_by(id=attention.id).first()
        self.assertIsNotNone(retrieved_attention.histopathologies)
        self.assertEqual(len(retrieved_attention.histopathologies), 1)
        self.assertTrue("benignos" in retrieved_attention.histopathologies[0].histopathology)
        self.assertEqual(retrieved_attention.histopathologies[0].attention.id, attention.id)

    # Agrega pruebas similares para:
    # Imaging, Laboratory, RegionalPhysicalExamination, ReviewOrgansSystem, Treatment
    # Todas siguen un patrón similar: crear la Attention padre, luego crear el objeto hijo,
    # y verificar la relación.

    # Crea Patient, Doctor y Attention.
    # Crea un Treatment vinculado a la Attention.
    # Verifica que se guarde y que la Attention recuperada lo tenga en attention.treatments.
    # (Comentario en el código indica que se deberían agregar pruebas similares para Imaging, Laboratory, RegionalPhysicalExamination, ReviewOrgansSystem).

    def test_create_treatment(self):
        patient = Patient(identifierType="Cedula", identifierCode="PATTREAT01", firstName="Treat", lastName1="Ment", address="Treatment St", birthdate=date(1980,1,1))
        doctor = Doctor(identifierCode="DOCTREAT01", firstName="Dr.", lastName1="Prescribe", phoneNumber="789", address="Clinic Treat", gender="Masculino", sex="Masculino", speciality="Farmacología", email="dr.prescribe@example.com")
        self.session.add_all([patient, doctor])
        self.session.commit()
        attention = Attention(date=datetime.now(), reasonConsultation="Dolor", currentIllness="Artritis", evolution="Controlado", idPatient=patient.id, idDoctor=doctor.id)
        self.session.add(attention)
        self.session.commit()

        treatment_data = {
            "medicament": "Ibuprofeno",
            "via": "Oral",
            "dosage": "400",
            "unity": "mg",
            "frequency": "Cada 8 horas",
            "indications": "Tomar con alimentos",
            "idAttention": attention.id
        }
        new_treatment = Treatment(**treatment_data)
        self.session.add(new_treatment)
        self.session.commit()

        retrieved_attention = self.session.query(Attention).filter_by(id=attention.id).first()
        self.assertIsNotNone(retrieved_attention.treatments)
        self.assertEqual(len(retrieved_attention.treatments), 1)
        self.assertEqual(retrieved_attention.treatments[0].medicament, "Ibuprofeno")


if __name__ == '__main__':
    unittest.main()