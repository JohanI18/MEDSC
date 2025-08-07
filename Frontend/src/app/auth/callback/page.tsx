'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('');
  const [mounted, setMounted] = useState(false);

  // Evitar errores de hidratación
  useEffect(() => {
    setMounted(true);
    setStatus('Procesando...');
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    const handleAuthCallback = async () => {
      try {
        setStatus('Obteniendo parámetros...');
        
        // Obtener los parámetros de la URL
        const access_token = searchParams.get('access_token');
        const refresh_token = searchParams.get('refresh_token');
        const type = searchParams.get('type');
        const error = searchParams.get('error');
        const error_description = searchParams.get('error_description');
        
        // También verificar si viene como fragment (después del #)
        const hash = window.location.hash;
        const hashParams = new URLSearchParams(hash.replace('#', ''));
        const hashAccessToken = hashParams.get('access_token');
        const hashRefreshToken = hashParams.get('refresh_token');
        const hashType = hashParams.get('type');

        console.log('Auth callback params:', {
          url_access_token: access_token ? 'present' : 'missing',
          url_refresh_token: refresh_token ? 'present' : 'missing',
          hash_access_token: hashAccessToken ? 'present' : 'missing',
          hash_refresh_token: hashRefreshToken ? 'present' : 'missing',
          type: type || hashType,
          error,
          error_description,
          full_url: window.location.href,
          hash: hash
        });

        // Usar tokens del hash si no están en la URL query
        const finalAccessToken = access_token || hashAccessToken;
        const finalRefreshToken = refresh_token || hashRefreshToken;
        const finalType = type || hashType;

        setStatus('Validando tokens...');

        if (error) {
          console.error('Auth error:', error, error_description);
          setStatus('Error en autenticación');
          router.push(`/login?error=${encodeURIComponent(error_description || error)}`);
          return;
        }

        // Si es un recovery type y tenemos access_token, redirigir a reset password
        if (finalType === 'recovery' && finalAccessToken) {
          setStatus('Redirigiendo a cambio de contraseña...');
          const redirectUrl = `/reset-password?access_token=${finalAccessToken}${finalRefreshToken ? `&refresh_token=${finalRefreshToken}` : ''}`;
          console.log('Redirecting to:', redirectUrl);
          router.push(redirectUrl);
          return;
        }

        // Si es signup confirmation
        if (finalType === 'signup') {
          setStatus('Cuenta confirmada exitosamente');
          router.push('/login?message=Account confirmed successfully');
          return;
        }

        // Para otros casos con access token, redirigir al dashboard
        if (finalAccessToken) {
          setStatus('Redirigiendo al dashboard...');
          router.push('/dashboard');
          return;
        }

        // Si no hay tokens válidos, mostrar información de debug
        setStatus('No se encontraron tokens válidos');
        console.warn('No valid tokens found, redirecting to login');
        
        // Esperar un poco para mostrar el debug info
        setTimeout(() => {
          router.push('/login?error=No se pudieron procesar los tokens de autenticación');
        }, 3000);

      } catch (error) {
        console.error('Error in auth callback:', error);
        setStatus('Error procesando autenticación');
        router.push('/login?error=Authentication processing failed');
      }
    };

    handleAuthCallback();
  }, [mounted, router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md w-full space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="text-gray-600">{status || 'Iniciando...'}</p>
        
        {/* Debug info - solo mostrar después del mount */}
        {mounted && (
          <div className="mt-8 text-left bg-gray-100 p-4 rounded text-xs">
            <strong>Debug Info:</strong>
            <div>Status: {status}</div>
            <div>URL disponible: Sí</div>
          </div>
        )}
        
        <div className="mt-4">
          <button 
            onClick={() => router.push('/login')}
            className="text-indigo-600 hover:text-indigo-500 text-sm underline"
          >
            Ir al login manualmente
          </button>
        </div>
      </div>
    </div>
  );
}
