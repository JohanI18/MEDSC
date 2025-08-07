import api from '@/lib/api';
import { Patient, CreatePatientData, UpdatePatientData, Allergy, EmergencyContact, PreExistingCondition, FamilyBackground, ApiResponse } from '@/types';

export const patientService = {
  // Get all patients
  getPatients: async (): Promise<ApiResponse<Patient[]>> => {
    try {
      const response = await api.get('/api/patients');
      return {
        success: true,
        data: response.data.data || response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch patients'
      };
    }
  },

  // Get patient by ID
  getPatient: async (id: number): Promise<ApiResponse<Patient>> => {
    try {
      const response = await api.get(`/get-patient-details/${id}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch patient'
      };
    }
  },

  // Create new patient
  createPatient: async (patientData: CreatePatientData): Promise<ApiResponse<Patient>> => {
    try {
      const response = await api.post('/api/patients', patientData);
      return {
        success: true,
        data: response.data.data,
        message: 'Patient created successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create patient'
      };
    }
  },

  // Update patient
  updatePatient: async (id: number, patientData: UpdatePatientData): Promise<ApiResponse<Patient>> => {
    try {
      const response = await api.put(`/api/patients/${id}`, patientData);
      return {
        success: true,
        data: response.data.data,
        message: 'Patient updated successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to update patient'
      };
    }
  },

  // Delete patient
  deletePatient: async (id: number): Promise<ApiResponse<void>> => {
    try {
      await api.post(`/patient/${id}/delete`);
      return {
        success: true,
        message: 'Patient deleted successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to delete patient'
      };
    }
  },

  // Patient allergies
  addAllergy: async (patientId: number, allergyData: Omit<Allergy, 'id' | 'patient_id' | 'created_at'>): Promise<ApiResponse<Allergy>> => {
    try {
      const response = await api.post(`/patient/${patientId}/add-allergy`, allergyData);
      return {
        success: true,
        data: response.data,
        message: 'Allergy added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add allergy'
      };
    }
  },

  removeAllergy: async (allergyId: number): Promise<ApiResponse<void>> => {
    try {
      await api.delete(`/patient/allergy/${allergyId}`);
      return {
        success: true,
        message: 'Allergy removed successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to remove allergy'
      };
    }
  },

  // Emergency contacts
  addEmergencyContact: async (patientId: number, contactData: Omit<EmergencyContact, 'id' | 'patient_id' | 'created_at'>): Promise<ApiResponse<EmergencyContact>> => {
    try {
      const response = await api.post(`/patient/${patientId}/add-contact`, contactData);
      return {
        success: true,
        data: response.data,
        message: 'Emergency contact added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add emergency contact'
      };
    }
  },

  removeEmergencyContact: async (contactId: number): Promise<ApiResponse<void>> => {
    try {
      await api.delete(`/patient/contact/${contactId}`);
      return {
        success: true,
        message: 'Emergency contact removed successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to remove emergency contact'
      };
    }
  },

  // Pre-existing conditions
  addCondition: async (patientId: number, conditionData: Omit<PreExistingCondition, 'id' | 'patient_id' | 'created_at'>): Promise<ApiResponse<PreExistingCondition>> => {
    try {
      const response = await api.post(`/patient/${patientId}/add-condition`, conditionData);
      return {
        success: true,
        data: response.data,
        message: 'Condition added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add condition'
      };
    }
  },

  removeCondition: async (conditionId: number): Promise<ApiResponse<void>> => {
    try {
      await api.delete(`/patient/condition/${conditionId}`);
      return {
        success: true,
        message: 'Condition removed successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to remove condition'
      };
    }
  },

  // Family background
  addFamilyBackground: async (patientId: number, familyData: Omit<FamilyBackground, 'id' | 'patient_id' | 'created_at'>): Promise<ApiResponse<FamilyBackground>> => {
    try {
      const response = await api.post(`/patient/${patientId}/add-family-background`, familyData);
      return {
        success: true,
        data: response.data,
        message: 'Family background added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add family background'
      };
    }
  },

  removeFamilyBackground: async (backgroundId: number): Promise<ApiResponse<void>> => {
    try {
      await api.delete(`/patient/family-background/${backgroundId}`);
      return {
        success: true,
        message: 'Family background removed successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to remove family background'
      };
    }
  }
};
