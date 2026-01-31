import api from '@/lib/api';
import { ApiResponse } from '@/types';

export interface Doctor {
  id: number;
  supabase_id: string;
  identifierCode: string;
  firstName: string;
  middleName?: string;
  lastName1: string;
  lastName2?: string;
  email: string;
  phoneNumber: string;
  address: string;
  gender: string;
  sex: string;
  speciality: string;
  role: string;
  status: string;
  created_at?: string;
}

export interface CreateDoctorData {
  email: string;
  password: string;
  firstName: string;
  middleName?: string;
  lastName1: string;
  lastName2?: string;
  identifierCode: string;
  phoneNumber: string;
  address: string;
  gender: string;
  sex: string;
  speciality: string;
  role?: string;
}

export interface UpdateDoctorData {
  firstName?: string;
  middleName?: string;
  lastName1?: string;
  lastName2?: string;
  phoneNumber?: string;
  address?: string;
  speciality?: string;
  role?: string;
  status?: string;
}

export interface CurrentUser {
  id: number;
  supabase_id?: string;
  email: string;
  firstName?: string;
  lastName1?: string;
  speciality?: string;
  role: string;
  isAdmin: boolean;
}

export const adminService = {
  /**
   * Get current user info including role
   */
  getCurrentUser: async (): Promise<ApiResponse<CurrentUser>> => {
    try {
      const response = await api.get('/api/admin/me');
      return {
        success: true,
        data: response.data.user
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener usuario'
      };
    }
  },

  /**
   * List all doctors (admin only)
   */
  listDoctors: async (): Promise<ApiResponse<Doctor[]>> => {
    try {
      const response = await api.get('/api/admin/doctors');
      return {
        success: true,
        data: response.data.doctors
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al listar doctores'
      };
    }
  },

  /**
   * Create a new doctor (admin only)
   */
  createDoctor: async (data: CreateDoctorData): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/api/admin/doctors', data);
      return {
        success: true,
        data: response.data,
        message: 'Doctor creado exitosamente'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al crear doctor'
      };
    }
  },

  /**
   * Update a doctor (admin only)
   */
  updateDoctor: async (doctorId: number, data: UpdateDoctorData): Promise<ApiResponse<any>> => {
    try {
      const response = await api.put(`/api/admin/doctors/${doctorId}`, data);
      return {
        success: true,
        data: response.data,
        message: 'Doctor actualizado exitosamente'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al actualizar doctor'
      };
    }
  },

  /**
   * Delete a doctor (admin only)
   */
  deleteDoctor: async (doctorId: number): Promise<ApiResponse<any>> => {
    try {
      const response = await api.delete(`/api/admin/doctors/${doctorId}`);
      return {
        success: true,
        data: response.data,
        message: 'Doctor eliminado exitosamente'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al eliminar doctor'
      };
    }
  }
};
