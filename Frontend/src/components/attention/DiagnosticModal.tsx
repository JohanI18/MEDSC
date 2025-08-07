'use client';

import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { attentionService } from '@/services/attention';
import toast from 'react-hot-toast';

interface DiagnosticModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface DiagnosticForm {
  cie10Code: string;
  disease: string;
  observations: string;
  diagnosticCondition: string;
  chronology: string;
}

interface Diagnostic {
  cie10Code: string;
  disease: string;
  observations: string;
  diagnosticCondition: string;
  chronology: string;
}

export default function DiagnosticModal({ isOpen, onClose, onSuccess }: DiagnosticModalProps) {
  const [formData, setFormData] = useState<DiagnosticForm>({
    cie10Code: '',
    disease: '',
    observations: '',
    diagnosticCondition: '',
    chronology: ''
  });
  
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const diagnosticConditions = [
    'Definitivo',
    'Presuntivo',
    'Diferencial'
  ];

  const chronologies = [
    'Agudo',
    'Crónico',
    'Subagudo'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddDiagnostic = async () => {
    if (!formData.cie10Code.trim() || !formData.disease.trim() || !formData.observations.trim() || 
        !formData.diagnosticCondition || !formData.chronology) {
      toast.error('Todos los campos del diagnóstico son requeridos');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await attentionService.addDiagnostic(formData);
      
      if (result.success) {
        setDiagnostics(prev => [...prev, { ...formData }]);
        toast.success('Diagnóstico agregado');
        // Reset form
        setFormData({
          cie10Code: '',
          disease: '',
          observations: '',
          diagnosticCondition: '',
          chronology: ''
        });
      } else {
        toast.error(result.error || 'Error al agregar diagnóstico');
      }
    } catch (error) {
      toast.error('Error inesperado');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleContinue = () => {
    if (diagnostics.length === 0) {
      toast.error('Debe agregar al menos un diagnóstico');
      return;
    }
    onSuccess();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Diagnósticos</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Add New Diagnostic Form */}
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Agregar Diagnóstico</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Código CIE-10 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="cie10Code"
                  value={formData.cie10Code}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: J06.9"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enfermedad <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="disease"
                  value={formData.disease}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nombre de la enfermedad o condición"
                />
              </div>

              <div className="md:col-span-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Observaciones <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="observations"
                  value={formData.observations}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Observaciones adicionales sobre el diagnóstico..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Condición Diagnóstica <span className="text-red-500">*</span>
                </label>
                <select
                  name="diagnosticCondition"
                  value={formData.diagnosticCondition}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar...</option>
                  {diagnosticConditions.map(condition => (
                    <option key={condition} value={condition}>{condition}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cronología <span className="text-red-500">*</span>
                </label>
                <select
                  name="chronology"
                  value={formData.chronology}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar...</option>
                  {chronologies.map(chronology => (
                    <option key={chronology} value={chronology}>{chronology}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleAddDiagnostic}
                disabled={isSubmitting}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
              >
                <Plus size={16} />
                {isSubmitting ? 'Agregando...' : 'Agregar Diagnóstico'}
              </button>
            </div>
          </div>

          {/* Diagnostics List */}
          {diagnostics.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Diagnósticos Agregados</h3>
              <div className="space-y-3">
                {diagnostics.map((diagnostic, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            {diagnostic.cie10Code}
                          </span>
                          <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            {diagnostic.diagnosticCondition}
                          </span>
                          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            {diagnostic.chronology}
                          </span>
                        </div>
                        <h4 className="font-medium text-gray-900">{diagnostic.disease}</h4>
                        <p className="text-gray-600 mt-1">{diagnostic.observations}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleContinue}
              disabled={diagnostics.length === 0}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400"
            >
              Continuar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
