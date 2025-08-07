import api from '@/lib/api';
import { LoginCredentials, RegisterData, ApiResponse } from '@/types';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/login', credentials);
      return {
        success: true,
        data: response.data,
        message: 'Login successful'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      };
    }
  },

  register: async (data: RegisterData): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/register', data);
      return {
        success: true,
        data: response.data,
        message: 'Registration successful'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed'
      };
    }
  },

  logout: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/logout');
      return {
        success: true,
        data: response.data,
        message: 'Logout successful'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Logout failed'
      };
    }
  },

  forgotPassword: async (email: string): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post('/forgot-password', { email });
      return {
        success: true,
        data: response.data,
        message: 'Email de recuperación enviado exitosamente'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Error al enviar email de recuperación'
      };
    }
  },

  resetPassword: async (password: string, confirm_password: string, access_token: string): Promise<ApiResponse<any>> => {
    try {
      const response = await api.post(`/reset-password?access_token=${access_token}`, { 
        password, 
        confirm_password 
      });
      return {
        success: true,
        data: response.data,
        message: 'Contraseña actualizada exitosamente'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Error al actualizar contraseña'
      };
    }
  },

  getCurrentUser: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await api.get('/me');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to get user info'
      };
    }
  }
};
