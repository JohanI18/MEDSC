'use client';

import { useState } from 'react';
import api from '@/lib/api';

export default function TestPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const testCors = async () => {
    setLoading(true);
    try {
      const response = await api.get('/test-cors');
      setResult({ success: true, data: response.data });
    } catch (error: any) {
      setResult({ 
        success: false, 
        error: error.message,
        details: error.response?.data || 'Sin detalles'
      });
    }
    setLoading(false);
  };

  const testLogin = async () => {
    setLoading(true);
    try {
      const response = await api.post('/login', {
        email: 'test@test.com',
        password: 'test123'
      });
      setResult({ success: true, data: response.data });
    } catch (error: any) {
      setResult({ 
        success: false, 
        error: error.message,
        details: error.response?.data || 'Sin detalles'
      });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">
          Test de Conexión Backend
        </h1>

        <div className="space-y-4 mb-8">
          <button
            onClick={testCors}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
          >
            {loading ? 'Probando...' : 'Test CORS'}
          </button>

          <button
            onClick={testLogin}
            disabled={loading}
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 ml-4"
          >
            {loading ? 'Probando...' : 'Test Login'}
          </button>
        </div>

        {result && (
          <div className={`p-4 rounded-md ${result.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <h3 className={`font-medium ${result.success ? 'text-green-800' : 'text-red-800'}`}>
              {result.success ? '✅ Éxito' : '❌ Error'}
            </h3>
            <pre className="mt-2 text-sm overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}

        <div className="mt-8 p-4 bg-yellow-100 rounded-md">
          <h3 className="font-medium text-yellow-800">Instrucciones:</h3>
          <ol className="mt-2 text-sm text-yellow-700 list-decimal list-inside space-y-1">
            <li>Asegúrate de que el backend Flask esté ejecutándose en http://localhost:5000</li>
            <li>Haz clic en "Test CORS" para verificar la conectividad básica</li>
            <li>Haz clic en "Test Login" para probar la autenticación (fallará pero debe mostrar error controlado)</li>
            <li>Si ves errores de CORS, revisa la configuración del backend</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
