'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Search, FileText, User, Calendar, CheckCircle, Circle } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import { attentionService } from '@/services/attention';
import { patientService } from '@/services/patients';
import { Patient } from '@/types';
import toast from 'react-hot-toast';

// Import modals
import VitalSignsModal from '@/components/attention/VitalSignsModal';
import InitialEvaluationModal from '@/components/attention/InitialEvaluationModal';
import PhysicalExamModal from '@/components/attention/PhysicalExamModal';
import OrganSystemReviewModal from '@/components/patients/OrganSystemReviewModal';
import DiagnosticModal from '@/components/attention/DiagnosticModal';
import TreatmentModal from '@/components/patients/TreatmentModal';
import AdditionalExamsModal from '@/components/patients/AdditionalExamsModal';
import EvolutionModal from '@/components/attention/EvolutionModal';
import CompleteAttentionModal from '@/components/attention/CompleteAttentionModal';

interface AttentionStep {
  id: string;
  name: string;
  completed: boolean;
  current: boolean;
}

// Define interfaces for the data structures
interface Treatment {
  medicament: string;
  via: string;
  dosage: string;
  unity: string;
  frequency: string;
  indications: string;
  warning?: string;
}

interface OrganSystemReview {
  typeReview: string;
  review: string;
}

interface Histopathology {
  histopathology: string;
}

interface Imaging {
  typeImaging: string;
  imaging: string;
}

interface Laboratory {
  typeExam: string;
  exam: string;
}

export default function AttentionPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showPatientSelector, setShowPatientSelector] = useState(false);
  
  // Modal states
  const [showVitalSigns, setShowVitalSigns] = useState(false);
  const [showInitialEvaluation, setShowInitialEvaluation] = useState(false);
  const [showPhysicalExam, setShowPhysicalExam] = useState(false);
  const [showOrganSystemReview, setShowOrganSystemReview] = useState(false);
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const [showTreatment, setShowTreatment] = useState(false);
  const [showAdditionalExams, setShowAdditionalExams] = useState(false);
  const [showEvolution, setShowEvolution] = useState(false);
  const [showComplete, setShowComplete] = useState(false);
  
  // Data states for the new modals
  const [treatments, setTreatments] = useState<Treatment[]>([]);
  const [organSystemReviews, setOrganSystemReviews] = useState<OrganSystemReview[]>([]);
  const [histopathologies, setHistopathologies] = useState<Histopathology[]>([]);
  const [imagings, setImagings] = useState<Imaging[]>([]);
  const [laboratories, setLaboratories] = useState<Laboratory[]>([]);
  
  // Step tracking - updated with new steps
  const [attentionSteps, setAttentionSteps] = useState<AttentionStep[]>([
    { id: 'patient', name: 'Seleccionar Paciente', completed: false, current: true },
    { id: 'vitals', name: 'Signos Vitales', completed: false, current: false },
    { id: 'evaluation', name: 'Evaluación Inicial', completed: false, current: false },
    { id: 'physical', name: 'Examen Físico', completed: false, current: false },
    { id: 'organReview', name: 'Revisión de Sistemas', completed: false, current: false },
    { id: 'diagnostic', name: 'Diagnósticos', completed: false, current: false },
    { id: 'treatment', name: 'Tratamientos', completed: false, current: false },
    { id: 'additionalExams', name: 'Exámenes Adicionales', completed: false, current: false },
    { id: 'evolution', name: 'Evolución', completed: false, current: false },
    { id: 'complete', name: 'Finalizar', completed: false, current: false }
  ]);

  // Obtener lista de pacientes para selección
  const { data: patients = [], isLoading: isLoadingPatients } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const result = await patientService.getPatients();
      if (!result.success) {
        throw new Error(result.error);
      }
      return Array.isArray(result.data) ? result.data : [];
    },
    enabled: showPatientSelector
  });

  const updateStepStatus = (stepId: string, completed: boolean, setCurrent?: boolean) => {
    setAttentionSteps(prev => prev.map(step => {
      if (step.id === stepId) {
        return { ...step, completed, current: setCurrent || false };
      } else if (setCurrent) {
        return { ...step, current: false };
      }
      return step;
    }));
  };

  const moveToNextStep = (currentStepId: string) => {
    const stepIndex = attentionSteps.findIndex(step => step.id === currentStepId);
    if (stepIndex !== -1 && stepIndex < attentionSteps.length - 1) {
      const nextStep = attentionSteps[stepIndex + 1];
      updateStepStatus(currentStepId, true);
      updateStepStatus(nextStep.id, false, true);
    }
  };

  const handleSelectPatient = async (patient: Patient) => {
    try {
      const result = await attentionService.selectPatientForAttention(patient.id);
      if (result.success) {
        setSelectedPatient(patient);
        setShowPatientSelector(false);
        moveToNextStep('patient');
        toast.success('Paciente seleccionado para atención');
      } else {
        toast.error(result.error || 'Error al seleccionar paciente');
      }
    } catch (error) {
      toast.error('Error inesperado al seleccionar paciente');
    }
  };

  const handleStepSuccess = (stepId: string) => {
    moveToNextStep(stepId);
  };

  const handleCompleteAttention = async () => {
    try {
      // Reset attention session and redirect or refresh
      await attentionService.resetAttentionSession();
      setSelectedPatient(null);
      setTreatments([]);
      setOrganSystemReviews([]);
      setHistopathologies([]);
      setImagings([]);
      setLaboratories([]);
      setAttentionSteps(prev => prev.map(step => ({ 
        ...step, 
        completed: false, 
        current: step.id === 'patient' 
      })));
      toast.success('Nueva atención lista para comenzar');
    } catch (error) {
      toast.error('Error al reiniciar sesión');
    }
  };

  const handleResetSession = async () => {
    try {
      await attentionService.resetAttentionSession();
      setSelectedPatient(null);
      setTreatments([]);
      setOrganSystemReviews([]);
      setHistopathologies([]);
      setImagings([]);
      setLaboratories([]);
      setAttentionSteps(prev => prev.map(step => ({ 
        ...step, 
        completed: false, 
        current: step.id === 'patient' 
      })));
      toast.success('Sesión de atención reiniciada');
    } catch (error) {
      toast.error('Error al reiniciar sesión');
    }
  };

  const filteredPatients = patients.filter(patient =>
    patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.identification_number.includes(searchTerm)
  );

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Atenciones Médicas</h1>
            <p className="text-gray-600 mt-2">
              Gestiona las atenciones médicas de los pacientes
            </p>
          </div>
          <div className="flex gap-2">
            {selectedPatient && (
              <button
                onClick={handleResetSession}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
              >
                Reiniciar Sesión
              </button>
            )}
            <button
              onClick={() => setShowPatientSelector(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus size={20} />
              Nueva Atención
            </button>
          </div>
        </div>

        {/* Progress Steps */}
        {selectedPatient && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Progreso de la Atención</h3>
            <div className="flex items-center space-x-4 overflow-x-auto">
              {attentionSteps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg min-w-max ${
                    step.completed 
                      ? 'bg-green-100 text-green-800' 
                      : step.current 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-gray-100 text-gray-600'
                  }`}>
                    {step.completed ? (
                      <CheckCircle size={16} />
                    ) : (
                      <Circle size={16} />
                    )}
                    <span className="text-sm font-medium">{step.name}</span>
                  </div>
                  {index < attentionSteps.length - 1 && (
                    <div className="w-8 h-px bg-gray-300 mx-2" />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Patient Selection Modal */}
        {showPatientSelector && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Seleccionar Paciente
                  </h2>
                  <button
                    onClick={() => setShowPatientSelector(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </button>
                </div>
                
                {/* Search */}
                <div className="mt-4 relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    placeholder="Buscar paciente por nombre o número de identificación..."
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {isLoadingPatients ? (
                  <div className="p-6 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Cargando pacientes...</p>
                  </div>
                ) : filteredPatients.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">
                    No se encontraron pacientes
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {filteredPatients.map((patient) => (
                      <div
                        key={patient.id}
                        onClick={() => handleSelectPatient(patient)}
                        className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {patient.first_name} {patient.last_name}
                            </h3>
                            <p className="text-sm text-gray-600">ID: {patient.identification_number}</p>
                            <p className="text-sm text-gray-600">
                              {patient.date_of_birth} • {patient.gender}
                            </p>
                          </div>
                          <User className="h-5 w-5 text-gray-400" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Current Patient Info */}
        {selectedPatient && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-blue-100 p-3 rounded-full">
                  <User className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {selectedPatient.first_name} {selectedPatient.last_name}
                  </h2>
                  <p className="text-gray-600">ID: {selectedPatient.identification_number}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Fecha de nacimiento</p>
                <p className="font-medium">{selectedPatient.date_of_birth}</p>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Signos Vitales */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-green-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Signos Vitales</h3>
              {attentionSteps.find(s => s.id === 'vitals')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Registrar signos vitales del paciente
            </p>
            <button
              onClick={() => setShowVitalSigns(true)}
              disabled={!selectedPatient}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {attentionSteps.find(s => s.id === 'vitals')?.completed ? 'Modificar' : 'Agregar'} Signos Vitales
            </button>
          </div>

          {/* Evaluación Inicial */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-yellow-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-yellow-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Evaluación Inicial</h3>
              {attentionSteps.find(s => s.id === 'evaluation')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Realizar evaluación inicial del paciente
            </p>
            <button
              onClick={() => setShowInitialEvaluation(true)}
              disabled={!selectedPatient}
              className="w-full bg-yellow-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-yellow-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {attentionSteps.find(s => s.id === 'evaluation')?.completed ? 'Modificar' : 'Agregar'} Evaluación
            </button>
          </div>

          {/* Examen Físico */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-purple-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Examen Físico</h3>
              {attentionSteps.find(s => s.id === 'physical')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Registrar examen físico del paciente
            </p>
            <button
              onClick={() => setShowPhysicalExam(true)}
              disabled={!selectedPatient}
              className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {attentionSteps.find(s => s.id === 'physical')?.completed ? 'Modificar' : 'Agregar'} Examen Físico
            </button>
          </div>

          {/* Revisión de Órganos y Sistemas */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-cyan-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-cyan-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Revisión de Sistemas</h3>
              {attentionSteps.find(s => s.id === 'organReview')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Revisión de órganos y sistemas ({organSystemReviews.length} registrados)
            </p>
            <button
              onClick={() => setShowOrganSystemReview(true)}
              disabled={!selectedPatient}
              className="w-full bg-cyan-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-cyan-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {organSystemReviews.length > 0 ? 'Modificar' : 'Agregar'} Revisiones
            </button>
          </div>

          {/* Diagnósticos */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-red-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Diagnósticos</h3>
              {attentionSteps.find(s => s.id === 'diagnostic')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Registrar diagnósticos médicos
            </p>
            <button
              onClick={() => setShowDiagnostic(true)}
              disabled={!selectedPatient}
              className="w-full bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {attentionSteps.find(s => s.id === 'diagnostic')?.completed ? 'Modificar' : 'Agregar'} Diagnósticos
            </button>
          </div>

          {/* Tratamientos */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-blue-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Tratamientos</h3>
              {attentionSteps.find(s => s.id === 'treatment')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Prescribir tratamientos y medicamentos ({treatments.length} registrados)
            </p>
            <button
              onClick={() => setShowTreatment(true)}
              disabled={!selectedPatient}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {treatments.length > 0 ? 'Modificar' : 'Agregar'} Tratamientos
            </button>
          </div>

          {/* Exámenes Adicionales */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-teal-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-teal-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Exámenes Adicionales</h3>
              {attentionSteps.find(s => s.id === 'additionalExams')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Histopatología, imagenología y laboratorio ({histopathologies.length + imagings.length + laboratories.length} registrados)
            </p>
            <button
              onClick={() => setShowAdditionalExams(true)}
              disabled={!selectedPatient}
              className="w-full bg-teal-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-teal-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {(histopathologies.length + imagings.length + laboratories.length) > 0 ? 'Modificar' : 'Agregar'} Exámenes
            </button>
          </div>

          {/* Evolución */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-indigo-100 p-2 rounded-lg">
                <FileText className="h-5 w-5 text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Evolución</h3>
              {attentionSteps.find(s => s.id === 'evolution')?.completed && (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <p className="text-gray-600 mb-4">
              Registrar evolución del paciente
            </p>
            <button
              onClick={() => setShowEvolution(true)}
              disabled={!selectedPatient}
              className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {attentionSteps.find(s => s.id === 'evolution')?.completed ? 'Modificar' : 'Agregar'} Evolución
            </button>
          </div>

          {/* Finalizar Atención */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-green-100 p-2 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Finalizar Atención</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Completar y guardar la atención médica
            </p>
            <button
              onClick={() => setShowComplete(true)}
              disabled={!selectedPatient || !attentionSteps.find(s => s.id === 'evolution')?.completed}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Completar Atención
            </button>
          </div>
        </div>

        {/* No Patient Selected State */}
        {!selectedPatient && (
          <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No hay paciente seleccionado
            </h3>
            <p className="text-gray-600 mb-6">
              Selecciona un paciente para comenzar una nueva atención médica
            </p>
            <button
              onClick={() => setShowPatientSelector(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
            >
              <Plus size={20} />
              Seleccionar Paciente
            </button>
          </div>
        )}

        {/* Modals */}
        <VitalSignsModal
          isOpen={showVitalSigns}
          onClose={() => setShowVitalSigns(false)}
          onSuccess={() => handleStepSuccess('vitals')}
        />

        <InitialEvaluationModal
          isOpen={showInitialEvaluation}
          onClose={() => setShowInitialEvaluation(false)}
          onSuccess={() => handleStepSuccess('evaluation')}
        />

        <PhysicalExamModal
          isOpen={showPhysicalExam}
          onClose={() => setShowPhysicalExam(false)}
          onSuccess={() => handleStepSuccess('physical')}
        />

        <OrganSystemReviewModal
          isOpen={showOrganSystemReview}
          onClose={() => setShowOrganSystemReview(false)}
          onNext={() => {
            setShowOrganSystemReview(false);
            handleStepSuccess('organReview');
          }}
          organSystemReviews={organSystemReviews}
          onOrganSystemReviewsChange={setOrganSystemReviews}
        />

        <DiagnosticModal
          isOpen={showDiagnostic}
          onClose={() => setShowDiagnostic(false)}
          onSuccess={() => handleStepSuccess('diagnostic')}
        />

        <TreatmentModal
          isOpen={showTreatment}
          onClose={() => setShowTreatment(false)}
          onNext={() => {
            setShowTreatment(false);
            handleStepSuccess('treatment');
          }}
          treatments={treatments}
          onTreatmentsChange={setTreatments}
        />

        <AdditionalExamsModal
          isOpen={showAdditionalExams}
          onClose={() => setShowAdditionalExams(false)}
          onNext={() => {
            setShowAdditionalExams(false);
            handleStepSuccess('additionalExams');
          }}
          histopathologies={histopathologies}
          imagings={imagings}
          laboratories={laboratories}
          onHistopathologiesChange={setHistopathologies}
          onImagingsChange={setImagings}
          onLaboratoriesChange={setLaboratories}
        />

        <EvolutionModal
          isOpen={showEvolution}
          onClose={() => setShowEvolution(false)}
          onSuccess={() => handleStepSuccess('evolution')}
        />

        <CompleteAttentionModal
          isOpen={showComplete}
          onClose={() => setShowComplete(false)}
          onSuccess={handleCompleteAttention}
          patientName={selectedPatient ? `${selectedPatient.first_name} ${selectedPatient.last_name}` : undefined}
        />
      </div>
    </Layout>
  );
}
