export interface Patient {
  id: number;
  first_name: string;
  middle_name?: string;
  last_name: string;
  last_name2?: string;
  email: string;
  phone: string;
  address: string;
  date_of_birth: string;
  gender: string;
  sex?: string;
  civil_status?: string;
  nationality?: string;
  job?: string;
  blood_type?: string;
  identification_type: string;
  identification_number: string;
  // Backward compatibility
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  // Complete related data
  allergies: Allergy[];
  emergency_contacts: EmergencyContact[];
  pre_existing_conditions: PreExistingCondition[];
  family_backgrounds: FamilyBackground[];
  created_at: string;
  updated_at: string;
}

export interface Allergy {
  id: number;
  allergy: string;
}

export interface EmergencyContact {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  relationship: string;
  phone1: string;
  phone2?: string;
  address: string;
}

export interface PreExistingCondition {
  id: number;
  disease_name: string;
  time?: string;
  medicament?: string;
  treatment?: string;
}

export interface FamilyBackground {
  id: number;
  family_background: string;
  time?: string;
  degree_relationship: string;
}

export interface VitalSigns {
  id: number;
  attention_id: number;
  blood_pressure_systolic: number;
  blood_pressure_diastolic: number;
  heart_rate: number;
  temperature: number;
  respiratory_rate: number;
  oxygen_saturation?: number;
  weight?: number;
  height?: number;
  created_at: string;
}

export interface Attention {
  id: number;
  patient_id: number;
  doctor_id: number;
  attention_date: string;
  reason_for_visit: string;
  status: 'in_progress' | 'completed';
  vital_signs?: VitalSigns;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface CreatePatientData {
  first_name: string;
  middle_name?: string;
  last_name: string;
  last_name2?: string;
  email: string;
  phone?: string;
  address: string;
  date_of_birth: string;
  gender?: string;
  sex?: string;
  civil_status?: string;
  nationality?: string;
  job?: string;
  blood_type?: string;
  identification_type: string;
  identification_number: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  // Additional data
  allergies?: string[];
  emergency_contacts?: CreateEmergencyContact[];
  pre_existing_conditions?: CreatePreExistingCondition[];
  family_backgrounds?: CreateFamilyBackground[];
}

export interface CreateEmergencyContact {
  first_name: string;
  last_name: string;
  relationship: string;
  phone1: string;
  phone2?: string;
  address: string;
}

export interface CreatePreExistingCondition {
  disease_name: string;
  time?: string;
  medicament?: string;
  treatment?: string;
}

export interface CreateFamilyBackground {
  family_background: string;
  time?: string;
  degree_relationship: string;
}

export interface UpdatePatientData {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  last_name2?: string;
  email?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  gender?: string;
  sex?: string;
  civil_status?: string;
  nationality?: string;
  job?: string;
  blood_type?: string;
  identification_type?: string;
  identification_number?: string;
  // Arrays with optional IDs for updates
  allergies?: Array<{
    id?: number;
    allergy: string;
  }>;
  emergency_contacts?: Array<{
    id?: number;
    first_name: string;
    last_name: string;
    relationship: string;
    phone1: string;
    phone2?: string;
    address: string;
  }>;
  pre_existing_conditions?: Array<{
    id?: number;
    disease_name: string;
    time?: string;
    medicament?: string;
    treatment?: string;
  }>;
  family_backgrounds?: Array<{
    id?: number;
    family_background: string;
    time?: string;
    degree_relationship: string;
  }>;
}
