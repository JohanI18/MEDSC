'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';
import { Shield, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';

export default function SetupPage() {
  const router = useRouter();
  const [step, setStep] = useState<'check' | 'form' | 'success'>('check');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    bootstrap_secret: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    middleName: '',
    lastName1: '',
    lastName2: '',
    identifierCode: '',
    phoneNumber: '',
    address: '',
    gender: '',
    sex: '',
    speciality: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (formData.password !== formData.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      if (formData.password.length < 6) {
        throw new Error('La contraseña debe tener al menos 6 caracteres');
      }

      const { confirmPassword, ...dataToSend } = formData;
      const response = await api.post('/api/admin/bootstrap', dataToSend);

      if (response.data.success) {
        setStep('success');
      } else {
        throw new Error(response.data.error || 'Error al crear administrador');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Error al crear administrador');
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-6 shadow-lg rounded-lg sm:px-10 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900">¡Configuración Completada!</h2>
            <p className="mt-4 text-gray-600">
              El administrador ha sido creado exitosamente. Ahora puede iniciar sesión y acceder al panel de administración.
            </p>
            <div className="mt-6">
              <Link
                href="/login"
                className="w-full flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Ir al Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl">
        <div className="text-center mb-8">
          <Shield className="w-16 h-16 text-primary-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900">Configuración Inicial</h2>
          <p className="mt-2 text-gray-600">
            Cree el primer administrador del sistema
          </p>
        </div>

        <div className="bg-white py-8 px-6 shadow-lg rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Bootstrap Secret */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-yellow-800 mb-2">Clave de Inicialización</h3>
              <p className="text-xs text-yellow-700 mb-3">
                Ingrese la clave secreta de configuración. Por defecto es: <code className="bg-yellow-100 px-1 rounded">medsc-admin-setup-2026</code>
              </p>
              <input
                type="password"
                name="bootstrap_secret"
                required
                value={formData.bootstrap_secret}
                onChange={handleInputChange}
                placeholder="Clave de inicialización"
                className="block w-full px-3 py-2 border border-yellow-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
              />
            </div>

            {/* Account Info */}
            <div className="border-b pb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Información de Cuenta</h3>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email *</label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Contraseña *</label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        required
                        value={formData.password}
                        onChange={handleInputChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Confirmar Contraseña *</label>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="confirmPassword"
                      required
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Personal Info */}
            <div className="border-b pb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Información Personal</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                  <input
                    type="text"
                    name="firstName"
                    required
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Segundo Nombre</label>
                  <input
                    type="text"
                    name="middleName"
                    value={formData.middleName}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Primer Apellido *</label>
                  <input
                    type="text"
                    name="lastName1"
                    required
                    value={formData.lastName1}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Segundo Apellido</label>
                  <input
                    type="text"
                    name="lastName2"
                    value={formData.lastName2}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Identificación *</label>
                  <input
                    type="text"
                    name="identifierCode"
                    required
                    value={formData.identifierCode}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Teléfono *</label>
                  <input
                    type="text"
                    name="phoneNumber"
                    required
                    value={formData.phoneNumber}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Género *</label>
                  <select
                    name="gender"
                    required
                    value={formData.gender}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="Masculino">Masculino</option>
                    <option value="Femenino">Femenino</option>
                    <option value="No Binario">No Binario</option>
                    <option value="Otro">Otro</option>
                    <option value="Prefiero no decir">Prefiero no decir</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Sexo *</label>
                  <select
                    name="sex"
                    required
                    value={formData.sex}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="Masculino">Masculino</option>
                    <option value="Femenino">Femenino</option>
                    <option value="Prefiero no decir">Prefiero no decir</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Dirección *</label>
                  <textarea
                    name="address"
                    required
                    value={formData.address}
                    onChange={handleInputChange}
                    rows={2}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Especialidad *</label>
                  <input
                    type="text"
                    name="speciality"
                    required
                    value={formData.speciality}
                    onChange={handleInputChange}
                    placeholder="Ej: Medicina General, Cardiología, etc."
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900">
                ← Volver al Login
              </Link>
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Creando...' : 'Crear Administrador'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
