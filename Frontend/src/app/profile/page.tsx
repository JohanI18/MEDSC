'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/layout/Layout';
import { User, Mail, Stethoscope, Shield } from 'lucide-react';
import { adminService, CurrentUser } from '@/services/admin';

export default function ProfilePage() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const result = await adminService.getCurrentUser();
      if (result.success && result.data) {
        setUser(result.data);
      } else {
        setError(result.error || 'Error al cargar el perfil');
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  return (
    <Layout currentPath="/profile">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mi Perfil</h1>
          <p className="text-gray-600">Información de tu cuenta</p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
          </div>
        ) : user ? (
          <div className="card">
            <div className="flex items-center space-x-4 mb-6">
              <div className="bg-primary-600 p-3 rounded-full">
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {user.firstName} {user.lastName1}
                </h2>
                <p className="text-sm text-gray-500">
                  {user.isAdmin ? 'Administrador' : 'Médico'}
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Correo electrónico</p>
                  <p className="font-medium text-gray-900">{user.email}</p>
                </div>
              </div>

              {user.speciality && (
                <div className="flex items-center space-x-3">
                  <Stethoscope className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Especialidad</p>
                    <p className="font-medium text-gray-900">{user.speciality}</p>
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-3">
                <Shield className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Rol</p>
                  <p className="font-medium text-gray-900">{user.role}</p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </Layout>
  );
}
