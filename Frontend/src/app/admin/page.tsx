'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/layout/Layout';
import { adminService, Doctor, CreateDoctorData, UpdateDoctorData } from '@/services/admin';
import { 
  UserPlus, 
  Edit2, 
  Trash2, 
  Users, 
  Shield, 
  X,
  Eye,
  EyeOff
} from 'lucide-react';

interface DoctorFormData extends CreateDoctorData {
  confirmPassword?: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState<DoctorFormData>({
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
    speciality: '',
    role: 'medico'
  });
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const result = await adminService.getCurrentUser();
      if (result.success && result.data) {
        if (result.data.isAdmin) {
          setIsAdmin(true);
          loadDoctors();
        } else {
          setError('Acceso denegado. Se requiere rol de administrador.');
          setIsLoading(false);
        }
      } else {
        router.push('/login');
      }
    } catch (err) {
      router.push('/login');
    }
  };

  const loadDoctors = async () => {
    try {
      setIsLoading(true);
      const result = await adminService.listDoctors();
      if (result.success && result.data) {
        setDoctors(result.data);
      } else {
        setError(result.error || 'Error al cargar doctores');
      }
    } catch (err) {
      setError('Error al cargar doctores');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const resetForm = () => {
    setFormData({
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
      speciality: '',
      role: 'medico'
    });
    setFormError('');
  };

  const handleCreateDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);

    try {
      if (formData.password !== formData.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      if (formData.password.length < 6) {
        throw new Error('La contraseña debe tener al menos 6 caracteres');
      }

      const { confirmPassword, ...dataToSend } = formData;
      const result = await adminService.createDoctor(dataToSend);

      if (result.success) {
        setShowCreateModal(false);
        resetForm();
        loadDoctors();
      } else {
        throw new Error(result.error);
      }
    } catch (err: any) {
      setFormError(err.message || 'Error al crear doctor');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoctor) return;
    
    setFormError('');
    setIsSubmitting(true);

    try {
      const updateData: UpdateDoctorData = {
        firstName: formData.firstName,
        middleName: formData.middleName,
        lastName1: formData.lastName1,
        lastName2: formData.lastName2,
        phoneNumber: formData.phoneNumber,
        address: formData.address,
        speciality: formData.speciality,
        role: formData.role,
        status: 'active'
      };

      const result = await adminService.updateDoctor(selectedDoctor.id, updateData);

      if (result.success) {
        setShowEditModal(false);
        setSelectedDoctor(null);
        resetForm();
        loadDoctors();
      } else {
        throw new Error(result.error);
      }
    } catch (err: any) {
      setFormError(err.message || 'Error al actualizar doctor');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteDoctor = async (doctor: Doctor) => {
    if (!confirm(`¿Está seguro que desea eliminar a ${doctor.firstName} ${doctor.lastName1}?`)) {
      return;
    }

    try {
      const result = await adminService.deleteDoctor(doctor.id);
      if (result.success) {
        loadDoctors();
      } else {
        alert(result.error || 'Error al eliminar doctor');
      }
    } catch (err) {
      alert('Error al eliminar doctor');
    }
  };

  const openEditModal = (doctor: Doctor) => {
    setSelectedDoctor(doctor);
    setFormData({
      email: doctor.email,
      password: '',
      confirmPassword: '',
      firstName: doctor.firstName,
      middleName: doctor.middleName || '',
      lastName1: doctor.lastName1,
      lastName2: doctor.lastName2 || '',
      identifierCode: doctor.identifierCode,
      phoneNumber: doctor.phoneNumber,
      address: doctor.address,
      gender: doctor.gender,
      sex: doctor.sex,
      speciality: doctor.speciality,
      role: doctor.role
    });
    setShowEditModal(true);
  };

  if (isLoading) {
    return (
      <Layout currentPath="/admin">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  if (!isAdmin) {
    return (
      <Layout currentPath="/admin">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <Shield className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-red-700">Acceso Denegado</h2>
          <p className="text-red-600 mt-2">{error || 'Se requiere rol de administrador para acceder a esta página.'}</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPath="/admin">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Shield className="w-6 h-6 text-primary-600" />
              Panel de Administración
            </h1>
            <p className="text-gray-600 mt-1">Gestione los doctores del sistema</p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowCreateModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <UserPlus className="w-5 h-5" />
            Nuevo Doctor
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Doctors Table */}
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Doctores Registrados ({doctors.length})
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Doctor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Especialidad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {doctors.map((doctor) => (
                  <tr key={doctor.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {doctor.firstName} {doctor.lastName1}
                      </div>
                      <div className="text-sm text-gray-500">
                        {doctor.identifierCode}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doctor.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doctor.speciality}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doctor.role === 'admin' 
                          ? 'bg-purple-100 text-purple-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {doctor.role === 'admin' ? 'Administrador' : 'Médico'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doctor.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {doctor.status === 'active' ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => openEditModal(doctor)}
                        className="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteDoctor(doctor)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
                {doctors.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                      No hay doctores registrados
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create Doctor Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Crear Nuevo Doctor</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateDoctor} className="p-6 space-y-6">
              {formError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {formError}
                </div>
              )}

              {/* Account Info */}
              <div className="border-b pb-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Información de Cuenta</h4>
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
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Rol *</label>
                    <select
                      name="role"
                      value={formData.role}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="medico">Médico</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Personal Info */}
              <div className="border-b pb-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Información Personal</h4>
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
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {isSubmitting ? 'Creando...' : 'Crear Doctor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Doctor Modal */}
      {showEditModal && selectedDoctor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Editar Doctor</h3>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedDoctor(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleEditDoctor} className="p-6 space-y-6">
              {formError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {formError}
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    disabled
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Identificación</label>
                  <input
                    type="text"
                    value={formData.identifierCode}
                    disabled
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500"
                  />
                </div>
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
                  <label className="block text-sm font-medium text-gray-700">Especialidad *</label>
                  <input
                    type="text"
                    name="speciality"
                    required
                    value={formData.speciality}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
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
                <div>
                  <label className="block text-sm font-medium text-gray-700">Rol *</label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="medico">Médico</option>
                    <option value="admin">Administrador</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedDoctor(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
