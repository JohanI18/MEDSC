'use client';

import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Plus, Trash2 } from 'lucide-react';
import { CreatePatientData } from '@/types';
import { patientService } from '@/services/patients';
import toast from 'react-hot-toast';

const patientSchema = z.object({
  first_name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  middle_name: z.string().optional(),
  last_name: z.string().min(2, 'El apellido debe tener al menos 2 caracteres'),
  last_name2: z.string().optional(),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
  address: z.string().min(5, 'La dirección debe tener al menos 5 caracteres'),
  date_of_birth: z.string().min(1, 'La fecha de nacimiento es requerida'),
  gender: z.enum(['Masculino', 'Femenino', 'No Binario', 'Otro', 'Prefiero no decir'], {
    required_error: 'Selecciona un género'
  }).optional(),
  sex: z.enum(['Masculino', 'Femenino', 'Prefiero no decir'], {
    required_error: 'Selecciona un sexo'
  }).optional(),
  civil_status: z.enum(['Soltero/a', 'UniónDeHecho', 'Casado/a', 'Divorciado/a', 'Viudo/a']).optional(),
  nationality: z.string().optional(),
  job: z.string().optional(),
  blood_type: z.enum(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']).optional(),
  identification_type: z.enum(['Cedula', 'Pasaporte', 'GeneratedIdentifier'], {
    required_error: 'Selecciona un tipo de identificación'
  }),
  identification_number: z.string().min(5, 'El número de identificación es requerido'),
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().optional(),
  allergies: z.array(z.object({
    allergy: z.string().min(1, 'Alergia requerida')
  })).optional(),
  emergency_contacts: z.array(z.object({
    first_name: z.string().min(1, 'Nombre requerido'),
    last_name: z.string().min(1, 'Apellido requerido'),
    relationship: z.string().min(1, 'Relación requerida'),
    phone1: z.string().min(1, 'Teléfono requerido'),
    phone2: z.string().optional(),
    address: z.string().min(1, 'Dirección requerida'),
  })).optional(),
  pre_existing_conditions: z.array(z.object({
    disease_name: z.string().min(1, 'Nombre de la enfermedad requerido'),
    time: z.string().optional(),
    medicament: z.string().optional(),
    treatment: z.string().optional(),
  })).optional(),
  family_backgrounds: z.array(z.object({
    family_background: z.string().min(1, 'Antecedente familiar requerido'),
    time: z.string().optional(),
    degree_relationship: z.enum(['1', '2', '3', '4'], {
      required_error: 'Grado de parentesco requerido'
    }),
  })).optional(),
});

interface AddPatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPatientAdded: () => void;
}

export default function AddPatientModal({ isOpen, onClose, onPatientAdded }: AddPatientModalProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [newAllergy, setNewAllergy] = useState('');
  
  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
    watch,
    trigger
  } = useForm<CreatePatientData>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      allergies: [],
      emergency_contacts: [],
      pre_existing_conditions: [],
      family_backgrounds: []
    }
  });

  const { fields: allergyFields, append: appendAllergy, remove: removeAllergy } = useFieldArray({
    control,
    name: 'allergies' as any
  });

  const { fields: emergencyContactFields, append: appendEmergencyContact, remove: removeEmergencyContact } = useFieldArray({
    control,
    name: 'emergency_contacts'
  });

  const { fields: conditionFields, append: appendCondition, remove: removeCondition } = useFieldArray({
    control,
    name: 'pre_existing_conditions'
  });

  const { fields: familyBackgroundFields, append: appendFamilyBackground, remove: removeFamilyBackground } = useFieldArray({
    control,
    name: 'family_backgrounds'
  });

  const addAllergy = () => {
    if (newAllergy.trim()) {
      appendAllergy({ allergy: newAllergy.trim() });
      setNewAllergy('');
    }
  };

  const steps = [
    'Información Personal',
    'Información Adicional',
    'Contactos de Emergencia',
    'Historial Médico'
  ];

  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (data: CreatePatientData) => {
    // Solo permitir envío si estamos en el último paso Y el usuario hizo click en "Crear Paciente"
    if (currentStep !== steps.length - 1) {
      return false;
    }
    
    setIsSubmitting(true);
    
    try {
      // Formatear los datos antes de enviarlos
      const formattedData = {
        ...data,
        // Convertir alergias de objetos a strings para la API actual
        allergies: data.allergies?.map(a => (a as any).allergy) || []
      };
      const result = await patientService.createPatient(formattedData);
      if (result.success) {
        toast.success('Paciente creado exitosamente');
        reset();
        setCurrentStep(0);
        setNewAllergy('');
        onPatientAdded();
        onClose();
      } else {
        toast.error(result.error || 'Error al crear paciente');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFormKeyDown = async (e: React.KeyboardEvent) => {
    // Prevenir envío del formulario con Enter
    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      
      // Solo permitir avanzar si no estamos en el último paso
      if (currentStep < steps.length - 1) {
        await nextStepWithValidation();
      }
    }
  };

  const validateCurrentStep = async () => {
    let fieldsToValidate: (keyof CreatePatientData)[] = [];
    
    switch (currentStep) {
      case 0: // Información Personal
        fieldsToValidate = ['first_name', 'last_name', 'identification_type', 'identification_number', 'date_of_birth', 'email', 'address'];
        break;
      case 1: // Información Adicional (opcional)
        return true;
      case 2: // Contactos de Emergencia (opcional)
        return true;
      case 3: // Historial Médico (opcional)
        return true;
      default:
        return true;
    }
    
    return await trigger(fieldsToValidate);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Solo permitir envío si estamos en el último paso Y el usuario hizo click explícito
    if (currentStep !== steps.length - 1) {
      return false;
    }
    
    // Obtener los datos del formulario manualmente
    const formData = watch();
    // Solo proceder si estamos realmente en el último paso
    await onSubmit(formData);
  };

  const nextStepWithValidation = async () => {
    const isStepValid = await validateCurrentStep();
    
    if (isStepValid && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else if (!isStepValid) {
      toast.error('Por favor completa los campos requeridos antes de continuar');
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

  // Limpiar el formulario cuando se cierre
  const handleClose = () => {
    reset();
    setCurrentStep(0);
    setNewAllergy('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-6 border w-full max-w-4xl shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Agregar Nuevo Paciente
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

        <form onSubmit={handleFormSubmit} onKeyDown={handleFormKeyDown} className="space-y-6">
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
                    className="input-field flex-1"
                    placeholder="Agregar alergia"
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
                  {allergyFields.map((field, index) => (
                    <div key={field.id} className="flex items-center justify-between bg-red-50 p-2 rounded">
                      <span className="text-red-800">{(field as any).allergy}</span>
                      <button
                        type="button"
                        onClick={() => removeAllergy(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
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
              
              {/* Condiciones Preexistentes */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h5 className="font-medium text-gray-800">Condiciones Preexistentes</h5>
                  <button
                    type="button"
                    onClick={() => appendCondition({
                      disease_name: '',
                      time: '',
                      medicament: '',
                      treatment: ''
                    })}
                    className="btn-secondary"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Condición
                  </button>
                </div>

                {conditionFields.map((field, index) => (
                  <div key={field.id} className="p-4 border rounded-lg bg-yellow-50 mb-3">
                    <div className="flex justify-between items-center mb-2">
                      <h6 className="font-medium text-yellow-800">Condición {index + 1}</h6>
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
                        {...register(`pre_existing_conditions.${index}.time`)}
                        type="date"
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

              {/* Antecedentes Familiares */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h5 className="font-medium text-gray-800">Antecedentes Familiares</h5>
                  <button
                    type="button"
                    onClick={() => appendFamilyBackground({
                      family_background: '',
                      time: '',
                      degree_relationship: '1'
                    })}
                    className="btn-secondary"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Antecedente
                  </button>
                </div>

                {familyBackgroundFields.map((field, index) => (
                  <div key={field.id} className="p-4 border rounded-lg bg-blue-50 mb-3">
                    <div className="flex justify-between items-center mb-2">
                      <h6 className="font-medium text-blue-800">Antecedente {index + 1}</h6>
                      <button
                        type="button"
                        onClick={() => removeFamilyBackground(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <input
                        {...register(`family_backgrounds.${index}.family_background`)}
                        placeholder="Condición o enfermedad familiar"
                        className="input-field sm:col-span-2"
                      />
                      <input
                        {...register(`family_backgrounds.${index}.time`)}
                        type="date"
                        className="input-field"
                      />
                      <select
                        {...register(`family_backgrounds.${index}.degree_relationship`)}
                        className="input-field"
                      >
                        <option value="1">1er Grado (Padres, Hijos)</option>
                        <option value="2">2do Grado (Hermanos, Abuelos)</option>
                        <option value="3">3er Grado (Tíos, Sobrinos)</option>
                        <option value="4">4to Grado (Primos)</option>
                      </select>
                    </div>
                  </div>
                ))}
              </div>
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
                  onClick={nextStepWithValidation}
                  className="px-4 py-2 text-sm font-medium text-white bg-medical-600 border border-transparent rounded-md hover:bg-medical-700"
                >
                  Siguiente
                </button>
              ) : (
                <button
                  type="button"
                  onClick={async () => {
                    const formData = watch();
                    await onSubmit(formData);
                  }}
                  disabled={isSubmitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-medical-600 border border-transparent rounded-md hover:bg-medical-700 disabled:opacity-50"
                >
                  {isSubmitting ? 'Creando...' : 'Crear Paciente'}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
