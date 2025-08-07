'use client';

import { X, User, Phone, Mail, MapPin, Calendar, Heart, AlertTriangle, Users, Stethoscope } from 'lucide-react';
import { Patient } from '@/types';

interface PatientDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  patient: Patient;
}

export default function PatientDetailsModal({ isOpen, onClose, patient }: PatientDetailsModalProps) {
  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    if (!dateString) return 'No especificado';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const calculateAge = (birthDate: string) => {
    if (!birthDate) return 'No especificado';
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return `${age} años`;
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-6 border w-full max-w-4xl shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="bg-medical-600 p-2 rounded-full">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">
                {patient.first_name} {patient.middle_name} {patient.last_name} {patient.last_name2}
              </h3>
              <p className="text-sm text-gray-500">
                {patient.identification_type}: {patient.identification_number}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Información Personal */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <User className="w-5 h-5 text-medical-600 mr-2" />
              <h4 className="font-semibold text-gray-900">Información Personal</h4>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Edad:</span>
                <span className="font-medium">{calculateAge(patient.date_of_birth)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Fecha de Nacimiento:</span>
                <span className="font-medium">{formatDate(patient.date_of_birth)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Género:</span>
                <span className="font-medium">{patient.gender || 'No especificado'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Estado Civil:</span>
                <span className="font-medium">{patient.civil_status || 'No especificado'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Nacionalidad:</span>
                <span className="font-medium">{patient.nationality || 'No especificado'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Ocupación:</span>
                <span className="font-medium">{patient.job || 'No especificado'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tipo de Sangre:</span>
                <span className="font-medium">{patient.blood_type || 'No especificado'}</span>
              </div>
            </div>
          </div>

          {/* Información de Contacto */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <Phone className="w-5 h-5 text-medical-600 mr-2" />
              <h4 className="font-semibold text-gray-900">Información de Contacto</h4>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-gray-400" />
                <span className="font-medium">{patient.email}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-gray-400" />
                <span className="font-medium">{patient.phone}</span>
              </div>
              <div className="flex items-start space-x-2">
                <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                <span className="font-medium">{patient.address}</span>
              </div>
            </div>
          </div>

          {/* Alergias */}
          <div className="bg-red-50 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
              <h4 className="font-semibold text-gray-900">Alergias</h4>
            </div>
            {patient.allergies && patient.allergies.length > 0 ? (
              <div className="space-y-2">
                {patient.allergies.map((allergy, index) => (
                  <div key={index} className="bg-red-100 px-3 py-2 rounded-md">
                    <span className="text-red-800 font-medium">{allergy.allergy}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No hay alergias registradas</p>
            )}
          </div>

          {/* Contactos de Emergencia */}
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <Users className="w-5 h-5 text-orange-600 mr-2" />
              <h4 className="font-semibold text-gray-900">Contactos de Emergencia</h4>
            </div>
            {patient.emergency_contacts && patient.emergency_contacts.length > 0 ? (
              <div className="space-y-3">
                {patient.emergency_contacts.map((contact, index) => (
                  <div key={index} className="bg-orange-100 px-3 py-2 rounded-md">
                    <div className="font-medium text-orange-800">{contact.full_name}</div>
                    <div className="text-sm text-orange-700">{contact.relationship}</div>
                    <div className="text-sm text-orange-600">
                      {contact.phone1}{contact.phone2 && ` / ${contact.phone2}`}
                    </div>
                    <div className="text-xs text-orange-600">{contact.address}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No hay contactos de emergencia registrados</p>
            )}
          </div>

          {/* Condiciones Preexistentes */}
          <div className="bg-yellow-50 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <Stethoscope className="w-5 h-5 text-yellow-600 mr-2" />
              <h4 className="font-semibold text-gray-900">Condiciones Preexistentes</h4>
            </div>
            {patient.pre_existing_conditions && patient.pre_existing_conditions.length > 0 ? (
              <div className="space-y-3">
                {patient.pre_existing_conditions.map((condition, index) => (
                  <div key={index} className="bg-yellow-100 px-3 py-2 rounded-md">
                    <div className="font-medium text-yellow-800">{condition.disease_name}</div>
                    {condition.time && (
                      <div className="text-sm text-yellow-700">Desde: {formatDate(condition.time)}</div>
                    )}
                    {condition.medicament && (
                      <div className="text-sm text-yellow-600">Medicamento: {condition.medicament}</div>
                    )}
                    {condition.treatment && (
                      <div className="text-sm text-yellow-600">Tratamiento: {condition.treatment}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No hay condiciones preexistentes registradas</p>
            )}
          </div>

          {/* Antecedentes Familiares */}
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <Heart className="w-5 h-5 text-blue-600 mr-2" />
              <h4 className="font-semibold text-gray-900">Antecedentes Familiares</h4>
            </div>
            {patient.family_backgrounds && patient.family_backgrounds.length > 0 ? (
              <div className="space-y-3">
                {patient.family_backgrounds.map((background, index) => (
                  <div key={index} className="bg-blue-100 px-3 py-2 rounded-md">
                    <div className="font-medium text-blue-800">{background.family_background}</div>
                    <div className="text-sm text-blue-700">
                      Grado: {background.degree_relationship}° grado
                    </div>
                    {background.time && (
                      <div className="text-sm text-blue-600">Fecha: {formatDate(background.time)}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No hay antecedentes familiares registrados</p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-gray-200 text-sm text-gray-500">
          <div className="flex justify-between">
            <span>Creado: {formatDate(patient.created_at)}</span>
            <span>Actualizado: {formatDate(patient.updated_at)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
