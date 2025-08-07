import api from '@/lib/api';
import { ApiResponse } from '@/types';

export interface DashboardStats {
  totalPatients: number;
  totalAttentions: number;
  attentionsToday: number;
  attentionsThisMonth: number;
  topDoctors: Array<{
    name: string;
    attentionCount: number;
  }>;
  topDiagnoses: Array<{
    disease: string;
    count: number;
  }>;
}

export const dashboardService = {
  // Get dashboard statistics
  getStats: async (): Promise<ApiResponse<DashboardStats>> => {
    try {
      // Get patients count
      const patientsResponse = await api.get('/api/patients');
      const totalPatients = patientsResponse.data.data?.length || 0;

      // Get attention statistics
      const statsResponse = await api.get('/api/statistics');
      const attentionStats = statsResponse.data.data;

      const stats: DashboardStats = {
        totalPatients,
        totalAttentions: attentionStats.totalAttentions || 0,
        attentionsToday: attentionStats.attentionsToday || 0,
        attentionsThisMonth: attentionStats.attentionsThisMonth || 0,
        topDoctors: attentionStats.topDoctors || [],
        topDiagnoses: attentionStats.topDiagnoses || []
      };

      return {
        success: true,
        data: stats
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch dashboard statistics'
      };
    }
  }
};
