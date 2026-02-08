'use client';

import { useState, useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Plus, Trash2, Save } from 'lucide-react';
import { Patient, UpdatePatientData } from '@/types';
import { patientService } from '@/services/patients';
import toast from 'react-hot-toast';

// Schema de validación para edición (similar al de creación pero con campos opcionales)
const editPatientSchema = z.object({
  first_name: z.string().min(1, 'Nombre es requerido'),
  middle_name: z.string().optional(),
  last_name: z.string().min(1, 'Apellido es requerido'),
  last_name2: z.string().optional(),
  identification_type: z.string().min(1, 'Tipo de identificación es requerido'),
  identification_number: z.string().min(1, 'Número de identificación es requerido'),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
  address: z.string().min(1, 'Dirección es requerida'),
  date_of_birth: z.string().min(1, 'Fecha de nacimiento es requerida'),
  gender: z.string().optional(),
  sex: z.string().optional(),
  civil_status: z.string().optional(),
  nationality: z.string().optional(),
  job: z.string().optional(),
  blood_type: z.string().optional(),
  // Arrays para datos relacionados
  allergies: z.array(z.object({
    id: z.number().optional(),
    allergy: z.string().min(1, 'Alergia es requerida')
  })).optional(),
  emergency_contacts: z.array(z.object({
    id: z.number().optional(),
    first_name: z.string().min(1, 'Nombre es requerido'),
    last_name: z.string().min(1, 'Apellido es requerido'),
    relationship: z.string().min(1, 'Relación es requerida'),
    phone1: z.string().min(1, 'Teléfono principal es requerido'),
    phone2: z.string().optional(),
    address: z.string().min(1, 'Dirección es requerida')
  })).optional(),
  pre_existing_conditions: z.array(z.object({
    id: z.number().optional(),
    disease_name: z.string().min(1, 'Nombre de la enfermedad es requerido'),
    year: z.number().optional(),
    medicament: z.string().optional(),
    treatment: z.string().optional()
  })).optional(),
  surgical_backgrounds: z.array(z.object({
    id: z.number().optional(),
    surgery_name: z.string().min(1, 'Nombre de la cirugía es requerido'),
    year: z.number().optional(),
    complications: z.string().optional(),
    observations: z.string().optional()
  })).optional(),
  family_backgrounds: z.array(z.object({
    id: z.number().optional(),
    family_background: z.string().min(1, 'Antecedente familiar es requerido')
  })).optional(),
  gynecological_backgrounds: z.array(z.object({
    id: z.number().optional(),
    last_menstruation_date: z.string().optional(),
    num_gestas: z.number().optional(),
    num_partos: z.number().optional(),
    num_cesareas: z.number().optional(),
    num_abortions: z.number().optional(),
    num_live_children: z.number().optional(),
    num_dead_children: z.number().optional(),
    contraceptive_method: z.string().optional()
  })).optional(),
  prenatal_controls: z.array(z.object({
    id: z.number().optional(),
    expected_delivery_date: z.string().optional(),
    gestational_age: z.number().optional()
  })).optional()
});

type EditPatientFormData = z.infer<typeof editPatientSchema>;

interface EditPatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  patient: Patient | null;
  onPatientUpdated: () => void;
}

export default function EditPatientModal({ isOpen, onClose, patient, onPatientUpdated }: EditPatientModalProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newAllergy, setNewAllergy] = useState('');

  const {
    register,
    reset,
    control,
    formState: { errors },
    watch,
    setValue
  } = useForm<EditPatientFormData>({
    resolver: zodResolver(editPatientSchema),
    defaultValues: {
      allergies: [],
      emergency_contacts: [],
      pre_existing_conditions: [],
      surgical_backgrounds: [],
      family_backgrounds: [],
      gynecological_backgrounds: [],
      prenatal_controls: []
    }
  });

  const watchedSex = watch('sex');

  // Field arrays para datos dinámicos
  const { fields: allergyFields, append: appendAllergy, remove: removeAllergy } = useFieldArray({
    control,
    name: 'allergies'
  });

  const { fields: emergencyContactFields, append: appendEmergencyContact, remove: removeEmergencyContact } = useFieldArray({
    control,
    name: 'emergency_contacts'
  });

  const { fields: conditionFields, append: appendCondition, remove: removeCondition } = useFieldArray({
    control,
    name: 'pre_existing_conditions'
  });

  const { fields: surgicalFields, append: appendSurgical, remove: removeSurgical } = useFieldArray({
    control,
    name: 'surgical_backgrounds'
  });

  const { fields: familyBgFields, append: appendFamilyBg, remove: removeFamilyBg } = useFieldArray({
    control,
    name: 'family_backgrounds'
  });

  const { fields: gynFields, append: appendGyn, remove: removeGyn } = useFieldArray({
    control,
    name: 'gynecological_backgrounds'
  });

  const { fields: prenatalFields, append: appendPrenatal, remove: removePrenatal } = useFieldArray({
    control,
    name: 'prenatal_controls'
  });

  // Cargar datos del paciente cuando el modal se abre
  useEffect(() => {
    if (isOpen && patient) {
      // Resetear el formulario con los datos del paciente
      reset({
        first_name: patient.first_name || '',
        middle_name: patient.middle_name || '',
        last_name: patient.last_name || '',
        last_name2: patient.last_name2 || '',
        identification_type: patient.identification_type || '',
        identification_number: patient.identification_number || '',
        email: patient.email || '',
        phone: patient.phone || '',
        address: patient.address || '',
        date_of_birth: patient.date_of_birth || '',
        gender: patient.gender || '',
        sex: patient.sex || '',
        civil_status: patient.civil_status || '',
        nationality: patient.nationality || '',
        job: patient.job || '',
        blood_type: patient.blood_type || '',
        allergies: patient.allergies?.map(a => ({ id: a.id, allergy: a.allergy })) || [],
        emergency_contacts: patient.emergency_contacts?.map(ec => ({
          id: ec.id,
          first_name: ec.first_name,
          last_name: ec.last_name,
          relationship: ec.relationship,
          phone1: ec.phone1,
          phone2: ec.phone2 || '',
          address: ec.address
        })) || [],
        pre_existing_conditions: patient.pre_existing_conditions?.map(pc => ({
          id: pc.id,
          disease_name: pc.disease_name,
          year: pc.year,
          medicament: pc.medicament || '',
          treatment: pc.treatment || ''
        })) || [],
        surgical_backgrounds: patient.surgical_backgrounds?.map(sb => ({
          id: sb.id,
          surgery_name: sb.surgery_name,
          year: sb.year,
          complications: sb.complications || '',
          observations: sb.observations || ''
        })) || [],
        family_backgrounds: patient.family_backgrounds?.map(fb => ({
          id: fb.id,
          family_background: fb.family_background
        })) || [],
        gynecological_backgrounds: patient.gynecological_backgrounds?.map(gb => ({
          id: gb.id,
          last_menstruation_date: gb.last_menstruation_date || '',
          num_gestas: gb.num_gestas,
          num_partos: gb.num_partos,
          num_cesareas: gb.num_cesareas,
          num_abortions: gb.num_abortions,
          num_live_children: gb.num_live_children,
          num_dead_children: gb.num_dead_children,
          contraceptive_method: gb.contraceptive_method || ''
        })) || [],
        prenatal_controls: patient.prenatal_controls?.map(pc => ({
          id: pc.id,
          expected_delivery_date: pc.expected_delivery_date || '',
          gestational_age: pc.gestational_age
        })) || []
      });
    }
  }, [isOpen, patient, reset]);

  const addAllergy = () => {
    if (newAllergy.trim()) {
      console.log('Adding allergy:', newAllergy.trim());
      appendAllergy({ allergy: newAllergy.trim() });
      setNewAllergy('');
      console.log('Current allergies after add:', watch('allergies'));
    }
  };

  const handleAllergyKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addAllergy();
    }
  };

  const steps = [
    'Información Personal',
    'Información Adicional',
    'Contactos de Emergencia',
    'Historial Médico'
  ];

  const onSubmit = async () => {
    if (!patient) return;

    setIsSubmitting(true);

    try {
      const formData = watch();
      const result = await patientService.updatePatient(patient.id, formData);
      if (result.success) {
        toast.success('Paciente actualizado exitosamente');
        onPatientUpdated();
        onClose();
      } else {
        toast.error(result.error || 'Error al actualizar paciente');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleClose = () => {
    setCurrentStep(0);
    setNewAllergy('');
    onClose();
  };

  if (!isOpen || !patient) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-6 border w-full max-w-4xl shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Editar Paciente: {patient.first_name} {patient.last_name}
          </h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center mb-8">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                  ${index <= currentStep 
                    ? 'bg-medical-600 text-white' 
                    : 'bg-gray-200 text-gray-400'
                  }`}
              >
                {index + 1}
              </div>
              <div
                className={`ml-2 text-sm font-medium
                  ${index <= currentStep ? 'text-medical-600' : 'text-gray-400'}
                `}
              >
                {step}
              </div>
              {index < steps.length - 1 && (
                <div className={`ml-4 w-16 h-0.5 ${index < currentStep ? 'bg-medical-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="space-y-6">
          {/* Step 0: Información Personal */}
          {currentStep === 0 && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Información Personal</h4>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Nombre *
                  </label>
                  <input
                    {...register('first_name')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Nombre"
                  />
                  {errors.first_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Segundo Nombre
                  </label>
                  <input
                    {...register('middle_name')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Segundo nombre"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Primer Apellido *
                  </label>
                  <input
                    {...register('last_name')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Primer apellido"
                  />
                  {errors.last_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Segundo Apellido
                  </label>
                  <input
                    {...register('last_name2')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Segundo apellido"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Tipo de Identificación *
                  </label>
                  <select
                    {...register('identification_type')}
                    className="input-field w-full"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="Cedula">Cédula</option>
                    <option value="Pasaporte">Pasaporte</option>
                    <option value="GeneratedIdentifier">Identificador Generado</option>
                  </select>
                  {errors.identification_type && (
                    <p className="mt-1 text-sm text-red-600">{errors.identification_type.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Número de Identificación *
                  </label>
                  <input
                    {...register('identification_number')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Número de identificación"
                  />
                  {errors.identification_number && (
                    <p className="mt-1 text-sm text-red-600">{errors.identification_number.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Fecha de Nacimiento *
                  </label>
                  <input
                    {...register('date_of_birth')}
                    type="date"
                    className="input-field w-full"
                  />
                  {errors.date_of_birth && (
                    <p className="mt-1 text-sm text-red-600">{errors.date_of_birth.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Email *
                  </label>
                  <input
                    {...register('email')}
                    type="email"
                    className="input-field w-full"
                    placeholder="Email"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Dirección *
                </label>
                <textarea
                  {...register('address')}
                  rows={3}
                  className="input-field w-full"
                  placeholder="Dirección completa"
                />
                {errors.address && (
                  <p className="mt-1 text-sm text-red-600">{errors.address.message}</p>
                )}
              </div>
            </div>
          )}

          {/* Step 1: Información Adicional */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Información Adicional</h4>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Teléfono
                  </label>
                  <input
                    {...register('phone')}
                    type="tel"
                    className="input-field w-full"
                    placeholder="Número de teléfono"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Género
                  </label>
                  <select
                    {...register('gender')}
                    className="input-field w-full"
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
                  <label className="block text-sm font-medium text-gray-700">
                    Sexo Biológico
                  </label>
                  <select
                    {...register('sex')}
                    className="input-field w-full"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="Masculino">Masculino</option>
                    <option value="Femenino">Femenino</option>
                    <option value="Prefiero no decir">Prefiero no decir</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Estado Civil
                  </label>
                  <select
                    {...register('civil_status')}
                    className="input-field w-full"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="Soltero/a">Soltero/a</option>
                    <option value="UniónDeHecho">Unión de Hecho</option>
                    <option value="Casado/a">Casado/a</option>
                    <option value="Divorciado/a">Divorciado/a</option>
                    <option value="Viudo/a">Viudo/a</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Nacionalidad
                  </label>
                  <input
                    {...register('nationality')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Nacionalidad"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Ocupación
                  </label>
                  <input
                    {...register('job')}
                    type="text"
                    className="input-field w-full"
                    placeholder="Ocupación"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Tipo de Sangre
                  </label>
                  <select
                    {...register('blood_type')}
                    className="input-field w-full"
                  >
                    <option value="">Seleccionar...</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
              </div>

              {/* Alergias */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Alergias
                </label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={newAllergy}
                    onChange={(e) => setNewAllergy(e.target.value)}
                    onKeyPress={handleAllergyKeyPress}
                    className="input-field flex-1"
                    placeholder="Agregar alergia (presiona Enter o +)"
                  />
                  <button
                    type="button"
                    onClick={addAllergy}
                    className="btn-secondary px-4 py-2"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
                <div className="space-y-2">
                  {allergyFields.map((field, index) => {
                    const allergyValue = watch(`allergies.${index}.allergy`);
                    return (
                      <div key={field.id} className="flex items-center justify-between bg-red-50 p-2 rounded">
                        <span className="text-red-800">{allergyValue || 'Sin nombre'}</span>
                        <button
                          type="button"
                          onClick={() => removeAllergy(index)}
                          className="text-red-600 hover:text-red-800"
                          title="Eliminar alergia"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    );
                  })}
                  {allergyFields.length === 0 && (
                    <p className="text-gray-500 text-sm">No hay alergias registradas.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Contactos de Emergencia */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-lg font-medium text-gray-900">Contactos de Emergencia</h4>
                <button
                  type="button"
                  onClick={() => appendEmergencyContact({
                    first_name: '',
                    last_name: '',
                    relationship: '',
                    phone1: '',
                    phone2: '',
                    address: ''
                  })}
                  className="btn-secondary"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Agregar Contacto
                </button>
              </div>

              {emergencyContactFields.map((field, index) => (
                <div key={field.id} className="p-4 border rounded-lg bg-orange-50">
                  <div className="flex justify-between items-center mb-2">
                    <h5 className="font-medium text-orange-800">Contacto {index + 1}</h5>
                    <button
                      type="button"
                      onClick={() => removeEmergencyContact(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <input
                      {...register(`emergency_contacts.${index}.first_name`)}
                      placeholder="Nombre"
                      className="input-field"
                    />
                    <input
                      {...register(`emergency_contacts.${index}.last_name`)}
                      placeholder="Apellido"
                      className="input-field"
                    />
                    <input
                      {...register(`emergency_contacts.${index}.relationship`)}
                      placeholder="Relación (ej: Madre, Hermano)"
                      className="input-field"
                    />
                    <input
                      {...register(`emergency_contacts.${index}.phone1`)}
                      placeholder="Teléfono principal"
                      className="input-field"
                    />
                    <input
                      {...register(`emergency_contacts.${index}.phone2`)}
                      placeholder="Teléfono secundario (opcional)"
                      className="input-field"
                    />
                    <input
                      {...register(`emergency_contacts.${index}.address`)}
                      placeholder="Dirección"
                      className="input-field sm:col-span-2"
                    />
                  </div>
                </div>
              ))}

              {emergencyContactFields.length === 0 && (
                <p className="text-gray-500 text-center py-8">
                  No hay contactos de emergencia. Haz clic en "Agregar Contacto" para añadir uno.
                </p>
              )}
            </div>
          )}

          {/* Step 3: Historial Médico */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <h4 className="text-lg font-medium text-gray-900">Historial Médico</h4>
              
              {/* Antecedentes Personales Patológicos */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h5 className="font-medium text-gray-800">Antecedentes Personales Patológicos</h5>
                  <button
                    type="button"
                    onClick={() => appendCondition({
                      disease_name: '',
                      year: undefined,
                      medicament: '',
                      treatment: ''
                    })}
                    className="btn-secondary"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Antecedente
                  </button>
                </div>

                {conditionFields.map((field, index) => (
                  <div key={field.id} className="p-4 border rounded-lg bg-yellow-50 mb-3">
                    <div className="flex justify-between items-center mb-2">
                      <h6 className="font-medium text-yellow-800">Antecedente {index + 1}</h6>
                      <button
                        type="button"
                        onClick={() => removeCondition(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <input
                        {...register(`pre_existing_conditions.${index}.disease_name`)}
                        placeholder="Nombre de la enfermedad"
                        className="input-field sm:col-span-2"
                      />
                      <input
                        {...register(`pre_existing_conditions.${index}.year`, { valueAsNumber: true })}
                        type="number"
                        placeholder="Año de diagnóstico"
                        min="1900"
                        max={new Date().getFullYear()}
                        className="input-field"
                      />
                      <input
                        {...register(`pre_existing_conditions.${index}.medicament`)}
                        placeholder="Medicamentos"
                        className="input-field"
                      />
                      <textarea
                        {...register(`pre_existing_conditions.${index}.treatment`)}
                        placeholder="Tratamiento"
                        rows={2}
                        className="input-field sm:col-span-2"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Antecedentes Personales Quirúrgicos */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h5 className="font-medium text-gray-800">Antecedentes Personales Quirúrgicos</h5>
                  <button
                    type="button"
                    onClick={() => appendSurgical({
                      surgery_name: '',
                      year: undefined,
                      complications: '',
                      observations: ''
                    })}
                    className="btn-secondary"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Cirugía
                  </button>
                </div>

                {surgicalFields.map((field, index) => (
                  <div key={field.id} className="p-4 border rounded-lg bg-purple-50 mb-3">
                    <div className="flex justify-between items-center mb-2">
                      <h6 className="font-medium text-purple-800">Cirugía {index + 1}</h6>
                      <button
                        type="button"
                        onClick={() => removeSurgical(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <input
                        {...register(`surgical_backgrounds.${index}.surgery_name`)}
                        placeholder="Nombre de la cirugía"
                        className="input-field sm:col-span-2"
                      />
                      <input
                        {...register(`surgical_backgrounds.${index}.year`, { valueAsNumber: true })}
                        type="number"
                        placeholder="Año"
                        min="1900"
                        max={new Date().getFullYear()}
                        className="input-field"
                      />
                      <input
                        {...register(`surgical_backgrounds.${index}.complications`)}
                        placeholder="Complicaciones"
                        className="input-field"
                      />
                      <textarea
                        {...register(`surgical_backgrounds.${index}.observations`)}
                        placeholder="Observaciones"
                        rows={2}
                        className="input-field sm:col-span-2"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Antecedentes Familiares */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h5 className="font-medium text-gray-800">Antecedentes Familiares</h5>
                  <button
                    type="button"
                    onClick={() => appendFamilyBg({
                      family_background: ''
                    })}
                    className="btn-secondary"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Antecedente
                  </button>
                </div>

                {familyBgFields.map((field, index) => (
                  <div key={field.id} className="p-4 border rounded-lg bg-blue-50 mb-3">
                    <div className="flex justify-between items-center mb-2">
                      <h6 className="font-medium text-blue-800">Antecedente {index + 1}</h6>
                      <button
                        type="button"
                        onClick={() => removeFamilyBg(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <textarea
                      {...register(`family_backgrounds.${index}.family_background`)}
                      placeholder="Describa el antecedente familiar (ej: diabetes en padre, hipertensión en madre, etc.)"
                      rows={2}
                      className="input-field w-full"
                    />
                  </div>
                ))}
              </div>

              {/* Antecedentes Ginecobstétricos - Solo para sexo femenino */}
              {watchedSex === 'Femenino' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h5 className="font-medium text-gray-800">Antecedentes Ginecobstétricos</h5>
                    {gynFields.length === 0 && (
                      <button
                        type="button"
                        onClick={() => appendGyn({
                          last_menstruation_date: '',
                          num_gestas: undefined,
                          num_partos: undefined,
                          num_cesareas: undefined,
                          num_abortions: undefined,
                          num_live_children: undefined,
                          num_dead_children: undefined,
                          contraceptive_method: ''
                        })}
                        className="btn-secondary"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Agregar Antecedente
                      </button>
                    )}
                  </div>

                  {gynFields.map((field, index) => (
                    <div key={field.id} className="p-4 border rounded-lg bg-pink-50 mb-3">
                      <div className="flex justify-between items-center mb-4">
                        <h6 className="font-medium text-pink-800">Antecedente Ginecobstétrico</h6>
                        <button
                          type="button"
                          onClick={() => removeGyn(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Fecha Última Menstruación
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.last_menstruation_date`)}
                            type="date"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Gestas (G)
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.num_gestas`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Partos (P)
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.num_partos`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Cesáreas (C)
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.num_cesareas`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Abortos (A)
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.num_abortions`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Hijos Vivos
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.num_live_children`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Hijos Fallecidos
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.num_dead_children`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Método Anticonceptivo
                          </label>
                          <input
                            {...register(`gynecological_backgrounds.${index}.contraceptive_method`)}
                            placeholder="Ej: DIU, Pastillas, etc."
                            className="input-field w-full"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Control Prenatal - Solo para sexo femenino */}
              {watchedSex === 'Femenino' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h5 className="font-medium text-gray-800">Control Prenatal</h5>
                    {prenatalFields.length === 0 && (
                      <button
                        type="button"
                        onClick={() => appendPrenatal({
                          expected_delivery_date: '',
                          gestational_age: undefined
                        })}
                        className="btn-secondary"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Agregar Control
                      </button>
                    )}
                  </div>

                  {prenatalFields.map((field, index) => (
                    <div key={field.id} className="p-4 border rounded-lg bg-pink-50 mb-3">
                      <div className="flex justify-between items-center mb-4">
                        <h6 className="font-medium text-pink-800">Control Prenatal</h6>
                        <button
                          type="button"
                          onClick={() => removePrenatal(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Fecha Probable de Parto (FPP)
                          </label>
                          <input
                            {...register(`prenatal_controls.${index}.expected_delivery_date`)}
                            type="date"
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Edad Gestacional (semanas)
                          </label>
                          <input
                            {...register(`prenatal_controls.${index}.gestational_age`, { valueAsNumber: true })}
                            type="number"
                            min="0"
                            max="45"
                            placeholder="0"
                            className="input-field w-full"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-6 border-t">
            <button
              type="button"
              onClick={prevStep}
              disabled={currentStep === 0}
              className={`px-4 py-2 text-sm font-medium rounded-md ${
                currentStep === 0
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
              }`}
            >
              Anterior
            </button>

            <div className="space-x-3">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancelar
              </button>

              {currentStep < steps.length - 1 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="px-4 py-2 text-sm font-medium text-white bg-medical-600 border border-transparent rounded-md hover:bg-medical-700"
                >
                  Siguiente
                </button>
              ) : (
                <button
                  type="button"
                  onClick={onSubmit}
                  disabled={isSubmitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {isSubmitting ? 'Actualizando...' : 'Actualizar Paciente'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
