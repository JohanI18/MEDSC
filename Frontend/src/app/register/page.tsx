'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Shield, ArrowLeft } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();

  // Redirect to login after a delay or show message
  useEffect(() => {
    // Optional: auto-redirect after 5 seconds
    // const timer = setTimeout(() => router.push('/login'), 5000);
    // return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-lg rounded-lg sm:px-10">
          <div className="text-center">
            <Shield className="w-16 h-16 text-primary-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900">Registro Deshabilitado</h2>
            <p className="mt-4 text-gray-600">
              El registro público de doctores ha sido deshabilitado por motivos de seguridad.
            </p>
            <p className="mt-2 text-gray-600">
              Si necesita una cuenta, por favor contacte al administrador del sistema.
            </p>
            <div className="mt-6 space-y-3">
              <Link 
                href="/login"
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Ir al Login
              </Link>
            </div>
            <p className="mt-4 text-sm text-gray-500">
              ¿Ya tienes una cuenta?{' '}
              <Link href="/login" className="font-medium text-primary-600 hover:text-primary-500">
                Inicia sesión
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
