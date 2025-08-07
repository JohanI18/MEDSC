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
