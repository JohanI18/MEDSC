import api from '@/lib/api';

export interface ICD11Suggestion {
  code: string;
  title: string;
}

export interface ICD11SearchResult {
  code: string;
  title: string;
  id: string;
  score: number;
}

export interface ICD11SearchResponse {
  success: boolean;
  data?: ICD11SearchResult[];
  suggestions?: ICD11Suggestion[];
  total?: number;
  error?: string;
  message?: string;
}

export interface ICD11EntityResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export interface ICD11HealthResponse {
  success: boolean;
  status: 'healthy' | 'unhealthy' | 'unavailable' | 'error';
  message: string;
}

export const icd11Service = {
  /**
   * Busca diagnósticos en la API de CIE-11
   * @param query Término de búsqueda
   * @param maxResults Número máximo de resultados (default: 10)
   */
  search: async (query: string, maxResults: number = 10): Promise<ICD11SearchResponse> => {
    try {
      const response = await api.get('/icd11/search', {
        params: {
          q: query,
          max_results: maxResults
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error searching ICD-11:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Error al buscar diagnósticos'
      };
    }
  },

  /**
   * Obtiene sugerencias para autocompletado por NOMBRE de enfermedad
   * @param query Nombre de la enfermedad a buscar
   * @param limit Número máximo de sugerencias (default: 8)
   */
  autocompleteByDisease: async (query: string, limit: number = 8): Promise<ICD11Suggestion[]> => {
    try {
      if (!query || query.length < 2) {
        return [];
      }

      const response = await api.get('/icd11/autocomplete/disease', {
        params: {
          q: query,
          limit
        }
      });

      if (response.data.success) {
        return response.data.suggestions || [];
      }
      return [];
    } catch (error) {
      console.error('Error in ICD-11 disease autocomplete:', error);
      return [];
    }
  },

  /**
   * Obtiene sugerencias para autocompletado por CÓDIGO CIE-11
   * @param query Código CIE-11 a buscar
   * @param limit Número máximo de sugerencias (default: 8)
   */
  autocompleteByCode: async (query: string, limit: number = 8): Promise<ICD11Suggestion[]> => {
    try {
      if (!query || query.length < 2) {
        return [];
      }

      const response = await api.get('/icd11/autocomplete/code', {
        params: {
          q: query,
          limit
        }
      });

      if (response.data.success) {
        return response.data.suggestions || [];
      }
      return [];
    } catch (error) {
      console.error('Error in ICD-11 code autocomplete:', error);
      return [];
    }
  },

  /**
   * Obtiene sugerencias para autocompletado (general - detecta automáticamente)
   * @param query Término de búsqueda
   * @param limit Número máximo de sugerencias (default: 8)
   * @deprecated Usar autocompleteByDisease o autocompleteByCode
   */
  autocomplete: async (query: string, limit: number = 8): Promise<ICD11Suggestion[]> => {
    try {
      if (!query || query.length < 2) {
        return [];
      }

      const response = await api.get('/icd11/autocomplete', {
        params: {
          q: query,
          limit
        }
      });

      if (response.data.success) {
        return response.data.suggestions || [];
      }
      return [];
    } catch (error) {
      console.error('Error in ICD-11 autocomplete:', error);
      return [];
    }
  },

  /**
   * Obtiene los detalles de una entidad específica de CIE-11
   * @param entityId ID de la entidad
   */
  getEntity: async (entityId: string): Promise<ICD11EntityResponse> => {
    try {
      const response = await api.get(`/icd11/entity/${entityId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting ICD-11 entity:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener entidad'
      };
    }
  },

  /**
   * Verifica si el servicio ICD-11 está disponible
   */
  checkHealth: async (): Promise<ICD11HealthResponse> => {
    try {
      const response = await api.get('/icd11/health');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        status: 'unavailable',
        message: error.response?.data?.message || 'No se puede verificar el estado del servicio'
      };
    }
  }
};

export default icd11Service;
