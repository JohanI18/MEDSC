from utils.db import db
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.sql import func

from sqlalchemy import DateTime

# --- TABLAS PRINCIPALES ---

class ActivityLogs(db.Model):
    __tablename__ = "activity_logs"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_0900_ai_ci"
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_supabase_id = db.Column(db.String(255), nullable=False, index=True)
    user_type = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by = db.Column(db.String(255), nullable=False)


class Patient(db.Model):
    __tablename__ = "patients"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    identifierType  = db.Column(
                        SA_Enum(
                          'Cedula',
                          'Pasaporte',
                          'GeneratedIdentifier',
                          name='patients_identifierType_enum',
                          native_enum=False, validate_strings=True
                        ),
                        nullable=False
                      )
    identifierCode  = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False, unique=True, index=True)
    firstName       = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    middleName      = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    lastName1       = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    lastName2       = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    nationality     = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    address         = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    phoneNumber     = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    birthdate       = db.Column(db.Date, nullable=False)
    gender          = db.Column(
                        SA_Enum(
                          'Masculino',
                          'Femenino',
                          'No Binario',
                          'Otro',
                          'Prefiero no decir',
                          name='patients_gender_enum',
                          native_enum=False, validate_strings=True
                        ),
                        nullable=True
                      )
    sex             = db.Column(
                        SA_Enum(
                          'Masculino',
                          'Femenino',
                          'Prefiero no decir',
                          name='patients_sex_enum',
                          native_enum=False, validate_strings=True
                        ),
                        nullable=True
                      )
    civilStatus     = db.Column(
                        SA_Enum(
                          'Soltero/a',
                          'UniónDeHecho',
                          'Casado/a',
                          'Divorciado/a',
                          'Viudo/a',
                          name='patients_civilStatus_enum',
                          native_enum=False, validate_strings=True
                        ),
                        nullable=True
                      )
    job             = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=True)
    bloodType       = db.Column(
                        SA_Enum(
                          'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-',
                          name='patients_bloodType_enum',
                          native_enum=False, validate_strings=True
                        ),
                        nullable=True
                      )
    email           = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=True) # Considerar db.String(255) si tiene un límite
    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    # Relaciones
    attentions = db.relationship("Attention", back_populates="patient") # Ajustar cascade según la política de BD
    allergies = db.relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    emergency_contacts = db.relationship("EmergencyContact", back_populates="patient", cascade="all, delete-orphan")
    family_backgrounds = db.relationship("FamilyBackground", back_populates="patient", cascade="all, delete-orphan")
    pre_existing_conditions = db.relationship("PreExistingCondition", back_populates="patient", cascade="all, delete-orphan")

class Doctor(db.Model):
    __tablename__ = "doctor"
    __table_args__ = {
        "mysql_charset": "utf8mb4", # Consistencia con otras tablas
        "mysql_collate": "utf8mb4_0900_ai_ci" # Consistencia con otras tablas
    }

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    identifierCode = db.Column(db.String(255), unique=True, nullable=False, index=True)
    supabase_id    = db.Column(db.String(36), unique=True, nullable=True, index=True)  # Campo para Supabase ID (UUID)
    firstName      = db.Column(db.String(255), nullable=False)
    middleName     = db.Column(db.String(255), nullable=True) # Ya estaba nullable=True
    lastName1      = db.Column(db.String(255), nullable=False)
    lastName2      = db.Column(db.String(255), nullable=True) # Ya estaba nullable=True
    phoneNumber    = db.Column(db.String(255), nullable=False)
    address        = db.Column(db.Text, nullable=False)
    gender         = db.Column(
        SA_Enum('Masculino', 'Femenino', 'No Binario', 'Otro', 'Prefiero no decir', name='doctor_gender_enum', native_enum=False, validate_strings=True),
        nullable=False
    )
    sex            = db.Column(
        SA_Enum('Masculino', 'Femenino', 'Prefiero no decir', name='doctor_sex_enum', native_enum=False, validate_strings=True),
        nullable=False
    )
    speciality     = db.Column(db.String(255), nullable=False)
    email          = db.Column(db.String(255), nullable=False, unique=True) # unique=True es bueno aquí
    supabase_id    = db.Column(db.String(255), unique=True, nullable=True, index=True)  # Campo para Supabase ID (UUID)
    role           = db.Column(db.String(50), nullable=False, server_default='medico')
    status         = db.Column(db.String(50), nullable=False, server_default='active')
    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    # Relaciones
    attentions = db.relationship("Attention", back_populates="doctor")

    # Agregar esta propiedad para obtener mensajes no leídos
    @property
    def unread_messages_count(self):
        from sqlalchemy import func
        from flask import session
        if not session.get('doctor_id'):
            return 0
        return ChatMessage.query.filter_by(
            receiver_id=self.id, 
            is_read=False
        ).count()

class Attention(db.Model):
    __tablename__ = "attention"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_0900_ai_ci"
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False, index=True)
    weight = db.Column(db.Numeric(6, 2), nullable=True)
    height = db.Column(db.Numeric(5, 2), nullable=True)
    temperature = db.Column(db.Numeric(4, 1), nullable=True)
    bloodPressure = db.Column(db.String(20), nullable=True)
    heartRate = db.Column(db.Integer, nullable=True)
    oxygenSaturation = db.Column(db.Integer, nullable=True)
    breathingFrequency = db.Column(db.Integer, nullable=True)
    glucose = db.Column(db.Numeric(5, 1), nullable=True)
    hemoglobin = db.Column(db.Numeric(4, 1), nullable=True)
    reasonConsultation = db.Column(db.String(255), nullable=False)
    currentIllness = db.Column(db.String(255), nullable=False)
    evolution = db.Column(db.String(255), nullable=True)

    idPatient = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    idDoctor = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    # Relaciones
    patient = db.relationship("Patient", back_populates="attentions")
    doctor = db.relationship("Doctor", back_populates="attentions")

    diagnostics = db.relationship("Diagnostic", back_populates="attention", cascade="all, delete-orphan")
    histopathologies = db.relationship("Histopathology", back_populates="attention", cascade="all, delete-orphan")
    imagings = db.relationship("Imaging", back_populates="attention", cascade="all, delete-orphan")
    laboratories = db.relationship("Laboratory", back_populates="attention", cascade="all, delete-orphan")
    regional_physical_examinations = db.relationship("RegionalPhysicalExamination", back_populates="attention", cascade="all, delete-orphan")
    review_organs_systems = db.relationship("ReviewOrgansSystem", back_populates="attention", cascade="all, delete-orphan")
    treatments = db.relationship("Treatment", back_populates="attention", cascade="all, delete-orphan")


# --- TABLAS DEPENDIENTES ---

class Allergy(db.Model):
    __tablename__ = "allergies"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    allergies        = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    # CAMBIADO: idClinicHistory -> idPatient
    idPatient        = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    # Relación
    patient = db.relationship("Patient", back_populates="allergies")

class Diagnostic(db.Model):
    __tablename__ = "diagnostic"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id                     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cie10Code              = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False, index=True) # Añadido index
    disease                = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    observations           = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False) # Cambiado a db.Text
    diagnosticCondition    = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    chronology             = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    idAttention            = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="diagnostics")

class EmergencyContact(db.Model):
    __tablename__ = "emergencyContact"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName        = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    lastName         = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    address          = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    relationship     = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    phoneNumber1     = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    phoneNumber2     = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    # CAMBIADO: idClinicHistory -> idPatient
    idPatient        = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    patient = db.relationship("Patient", back_populates="emergency_contacts")

class FamilyBackground(db.Model):
    __tablename__ = "familyBackground"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id                   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    familyBackground     = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    time                 = db.Column(db.Date, nullable=False)
    degreeRelationship   = db.Column(SA_Enum('1', '2', '3', '4', name='familyBackground_degreeRelationship_enum', native_enum=False, validate_strings=True), nullable=False)
    # CAMBIADO: idClinicHistory -> idPatient
    idPatient            = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    patient = db.relationship("Patient", back_populates="family_backgrounds")

class Histopathology(db.Model):
    __tablename__ = "histopathology"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    histopathology    = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    idAttention       = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="histopathologies")

class Imaging(db.Model):
    __tablename__ = "imaging"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    typeImaging    = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    imaging        = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    idAttention    = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="imagings")

class Laboratory(db.Model):
    __tablename__ = "laboratory"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    typeExam      = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    exam          = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    idAttention   = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="laboratories")

class PreExistingCondition(db.Model):
    __tablename__ = "preExistingCondition"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diseaseName      = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    time             = db.Column(db.Date, nullable=False)
    medicament       = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    treatment        = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=True)
    # CAMBIADO: idClinicHistory -> idPatient
    idPatient        = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    patient = db.relationship("Patient", back_populates="pre_existing_conditions")

class RegionalPhysicalExamination(db.Model):
    __tablename__ = "regionalPhysicalExamination"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    typeExamination  = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    examination      = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    idAttention      = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="regional_physical_examinations")

class ReviewOrgansSystem(db.Model): # Nombre de clase singular
    __tablename__ = "reviewOrgansSystems" # Nombre de tabla plural
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    typeReview    = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    review        = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    idAttention   = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="review_organs_systems")

class Treatment(db.Model):
    __tablename__ = "treatment"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci"
    }

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medicament   = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    via          = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    dosage       = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    unity        = db.Column(db.String(255, collation="utf8mb4_general_ci"), nullable=False)
    frequency    = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    indications  = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    warning      = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=True) # Confirmado nullable=True
    idAttention  = db.Column(db.Integer, db.ForeignKey('attention.id'), nullable=False, index=True)

    created_at      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by      = db.Column(db.String(255), nullable=False)
    updated_at      = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by      = db.Column(db.String(255), nullable=False)
    is_deleted      = db.Column(db.Boolean, default=False, index=True, nullable=False) # Añadido index

    attention = db.relationship("Attention", back_populates="treatments")

class ChatMessage(db.Model):
    __tablename__ = "chat_message"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_0900_ai_ci"
    }
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)  # Hacer nullable para permitir Supabase only
    receiver_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)  # Hacer nullable
    sender_supabase_id = db.Column(db.String(255), nullable=False)  # Requerido para identificar sender
    sender_type = db.Column(db.String(50), nullable=False, server_default='medico')
    receiver_supabase_id = db.Column(db.String(255), nullable=False)  # Requerido para identificar receiver
    receiver_type = db.Column(db.String(50), nullable=False, server_default='medico')
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.String(255), nullable=False)  # Campo requerido por la base de datos
    
    # Relaciones (opcionales ahora que usamos Supabase IDs)
    sender = db.relationship("Doctor", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship("Doctor", foreign_keys=[receiver_id], backref="received_messages")

# --- ÍNDICES ADICIONALES (Ejemplos, algunos ya están por index=True en columnas) ---
# Estos se crean automáticamente si index=True está en la columna.
# Si necesitas índices compuestos, los defines aquí.

db.Index('idx_patients_name', Patient.firstName, Patient.lastName1, Patient.lastName2)
db.Index('idx_doctor_name', Doctor.firstName, Doctor.lastName1, Doctor.lastName2)

# Nota sobre cascade en Patient.attentions:
# Lo he dejado como estaba (`cascade="all, delete-orphan"`). Si tu FK en la base de datos
# para `attention.idPatient` -> `patients.id` es `ON DELETE RESTRICT`,
# entonces un borrado de un `Patient` que tenga `Attention`s fallará a nivel de base de datos
# antes de que SQLAlchemy intente el borrado en cascada. Si la FK es `ON DELETE CASCADE`,
# entonces la base de datos y SQLAlchemy trabajarán en conjunto. Ajusta el `cascade`
# o la política `ON DELETE` de la FK para que sean consistentes con tu lógica deseada.
# Para las demás relaciones "hijas" de Patient, he mantenido `cascade="all, delete-orphan"`
# asumiendo que esos elementos sí deben borrarse si el paciente se borra.
# Similar para Attention y sus tablas hijas.