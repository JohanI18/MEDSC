'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Search, UserPlus, Edit, Trash2, Phone, Mail } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import { patientService } from '@/services/patients';
import { Patient } from '@/types';
import toast from 'react-hot-toast';
import AddPatientModal from '@/components/patients/AddPatientModal';
import PatientDetailsModal from '@/components/patients/PatientDetailsModal';
import EditPatientModal from '@/components/patients/EditPatientModal';

export default function PatientsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const { data: patients = [], isLoading, error, refetch } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const result = await patientService.getPatients();
      if (!result.success) {
        throw new Error(result.error);
      }
      // Asegurar que siempre devolvemos un array
      const patientsData = result.data || [];
      return Array.isArray(patientsData) ? patientsData : [];
    }
  });

  // Verificar que patients es un array antes de filtrar
  const filteredPatients = Array.isArray(patients) ? patients.filter(patient =>
    `${patient.first_name} ${patient.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.identification_number.includes(searchTerm)
  ) : [];

  const handleDeletePatient = async (patientId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este paciente?')) {
      const result = await patientService.deletePatient(patientId);
      if (result.success) {
        toast.success('Paciente eliminado exitosamente');
        refetch();
      } else {
        toast.error(result.error || 'Error al eliminar paciente');
      }
    }
  };

  const handlePatientClick = (patient: Patient) => {
    setSelectedPatient(patient);
    setShowDetailsModal(true);
  };

  const handleEditPatient = (patient: Patient) => {
    setSelectedPatient(patient);
    setShowEditModal(true);
  };

  const handleCloseDetailsModal = () => {
    setShowDetailsModal(false);
    setSelectedPatient(null);
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setSelectedPatient(null);
  };

  if (error) {
    return (
      <Layout currentPath="/patients">
        <div className="text-center py-12">
          <p className="text-red-600">Error al cargar pacientes</p>
          <button
            onClick={() => refetch()}
            className="mt-4 btn-primary"
          >
            Reintentar
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPath="/patients">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Pacientes</h1>
            <p className="text-gray-600">Gestiona la información de los pacientes</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Agregar Paciente
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Buscar por nombre, email o número de identificación..."
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Patients List */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando pacientes...</p>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="text-center py-12">
            <UserPlus className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay pacientes</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm ? 'No se encontraron pacientes que coincidan con tu búsqueda.' : 'Comienza agregando un nuevo paciente.'}
            </p>
            {!searchTerm && (
              <div className="mt-6">
                <button
                  onClick={() => setShowAddModal(true)}
                  className="btn-primary flex items-center gap-2 mx-auto"
                >
                  <Plus className="w-4 h-4" />
                  Agregar Paciente
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {filteredPatients.map((patient) => (
                <li key={patient.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div 
                        className="flex-1 cursor-pointer hover:bg-gray-50 -m-2 p-2 rounded transition-colors"
                        onClick={() => handlePatientClick(patient)}
                      >
                        <div className="flex items-center justify-between">
                          <p className="text-lg font-medium text-primary-600 truncate">
                            {patient.first_name} {patient.last_name}
                          </p>
                        </div>
                        <div className="mt-2 sm:flex sm:justify-between">
                          <div className="sm:flex space-y-1 sm:space-y-0 sm:space-x-6">
                            <p className="flex items-center text-sm text-gray-500">
                              <Mail className="flex-shrink-0 mr-1.5 h-4 w-4" />
                              {patient.email}
                            </p>
                            <p className="flex items-center text-sm text-gray-500">
                              <Phone className="flex-shrink-0 mr-1.5 h-4 w-4" />
                              {patient.phone}
                            </p>
                          </div>
                          <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                            <p>{patient.identification_type}: {patient.identification_number}</p>
                          </div>
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                          <p>Género: {patient.gender} | Fecha de nacimiento: {new Date(patient.date_of_birth).toLocaleDateString()}</p>
                          <p>Dirección: {patient.address}</p>
                        </div>
                      </div>
                      
                      <div className="ml-2 flex-shrink-0 flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditPatient(patient);
                          }}
                          className="text-primary-600 hover:text-primary-900"
                          title="Editar paciente"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeletePatient(patient.id);
                          }}
                          className="text-red-600 hover:text-red-900"
                          title="Eliminar paciente"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Stats */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserPlus className="h-8 w-8 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total de Pacientes
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {patients.length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Patient Modal */}
      <AddPatientModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onPatientAdded={refetch}
      />

      {/* Patient Details Modal */}
      {selectedPatient && (
        <PatientDetailsModal
          isOpen={showDetailsModal}
          onClose={handleCloseDetailsModal}
          patient={selectedPatient}
        />
      )}

      {/* Edit Patient Modal */}
      {selectedPatient && (
        <EditPatientModal
          isOpen={showEditModal}
          onClose={handleCloseEditModal}
          patient={selectedPatient}
          onPatientUpdated={refetch}
        />
      )}
    </Layout>
  );
}
