import api from '@/lib/api';
import { Attention, VitalSigns, ApiResponse } from '@/types';

export const attentionService = {
  // Select patient for attention
  selectPatientForAttention: async (patientId: number): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/select-patient-for-attention', { patient_id: patientId });
      return {
        success: true,
        data: response.data,
        message: 'Patient selected for attention'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to select patient'
      };
    }
  },

  // Add vital signs
  addVitalSigns: async (vitalSignsData: Omit<VitalSigns, 'id' | 'attention_id' | 'created_at'>): Promise<ApiResponse<VitalSigns>> => {
    try {
      const response = await api.post('/add-vital-signs', vitalSignsData);
      return {
        success: true,
        data: response.data,
        message: 'Vital signs added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add vital signs'
      };
    }
  },

  // Add initial evaluation
  addInitialEvaluation: async (evaluationData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-initial-evaluation', evaluationData);
      return {
        success: true,
        data: response.data,
        message: 'Initial evaluation added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add initial evaluation'
      };
    }
  },

  // Add physical exam
  addPhysicalExam: async (examData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-physical-exam', examData);
      return {
        success: true,
        data: response.data,
        message: 'Physical exam added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add physical exam'
      };
    }
  },

  // Remove physical exam
  removePhysicalExam: async (examId: number): Promise<ApiResponse<void>> => {
    try {
      await api.post('/remove-physical-exam', { exam_id: examId });
      return {
        success: true,
        message: 'Physical exam removed successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to remove physical exam'
      };
    }
  },

  // Add organ system review
  addOrganSystemReview: async (reviewData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-organ-system-review', reviewData);
      return {
        success: true,
        data: response.data,
        message: 'Organ system review added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add organ system review'
      };
    }
  },

  // Add diagnostic
  addDiagnostic: async (diagnosticData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-diagnostic', diagnosticData);
      return {
        success: true,
        data: response.data,
        message: 'Diagnostic added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add diagnostic'
      };
    }
  },

  // Add treatment
  addTreatment: async (treatmentData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-treatment', treatmentData);
      return {
        success: true,
        data: response.data,
        message: 'Treatment added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add treatment'
      };
    }
  },

  // Add laboratory
  addLaboratory: async (labData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-laboratory', labData);
      return {
        success: true,
        data: response.data,
        message: 'Laboratory exam added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add laboratory exam'
      };
    }
  },

  // Add imaging
  addImaging: async (imagingData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-imaging', imagingData);
      return {
        success: true,
        data: response.data,
        message: 'Imaging exam added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add imaging exam'
      };
    }
  },

  // Add histopathology
  addHistopathology: async (histoData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-histopathology', histoData);
      return {
        success: true,
        data: response.data,
        message: 'Histopathology exam added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add histopathology exam'
      };
    }
  },

  // Add evolution
  addEvolution: async (evolutionData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/add-evolution', evolutionData);
      return {
        success: true,
        data: response.data,
        message: 'Evolution added successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to add evolution'
      };
    }
  },

  // Complete attention
  completeAttention: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/complete-attention');
      return {
        success: true,
        data: response.data,
        message: 'Attention completed successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to complete attention'
      };
    }
  },

  // Reset attention session
  resetAttentionSession: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/reset-attention-session');
      return {
        success: true,
        data: response.data,
        message: 'Attention session reset successfully'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to reset attention session'
      };
    }
  },

  // Navigation helpers
  continueToOrganSystems: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/continue-to-organ-systems');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.message || 'Failed to continue' };
    }
  },

  continueToDiagnostics: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/continue-to-diagnostics');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.message || 'Failed to continue' };
    }
  },

  continueToTreatments: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/continue-to-treatments');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.message || 'Failed to continue' };
    }
  },

  continueToExtraExams: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/continue-to-extra-exams');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.message || 'Failed to continue' };
    }
  },

  continueToEvolution: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/continue-to-evolution');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.message || 'Failed to continue' };
    }
  }
};
