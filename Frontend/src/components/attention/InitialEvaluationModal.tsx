'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { attentionService } from '@/services/attention';
import toast from 'react-hot-toast';

interface InitialEvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface EvaluationForm {
  reasonConsultation: string;
  currentIllness: string;
}

export default function InitialEvaluationModal({ isOpen, onClose, onSuccess }: InitialEvaluationModalProps) {
  const [formData, setFormData] = useState<EvaluationForm>({
    reasonConsultation: '',
    currentIllness: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.reasonConsultation.trim() || !formData.currentIllness.trim()) {
      toast.error('Motivo de consulta y enfermedad actual son requeridos');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await attentionService.addInitialEvaluation(formData);
      
      if (result.success) {
        toast.success('Evaluación inicial guardada exitosamente');
        onSuccess();
        onClose();
        // Reset form
        setFormData({
          reasonConsultation: '',
          currentIllness: ''
        });
      } else {
        toast.error(result.error || 'Error al guardar evaluación inicial');
      }
    } catch (error) {
      toast.error('Error inesperado');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Evaluación Inicial</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motivo de Consulta <span className="text-red-500">*</span>
              </label>
              <textarea
                name="reasonConsultation"
                value={formData.reasonConsultation}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describa el motivo principal de la consulta..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enfermedad Actual <span className="text-red-500">*</span>
              </label>
              <textarea
                name="currentIllness"
                value={formData.currentIllness}
                onChange={handleInputChange}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describa la historia de la enfermedad actual, síntomas, duración, etc..."
                required
              />
            </div>
          </div>

          <div className="mt-8 flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.reasonConsultation.trim() || !formData.currentIllness.trim()}
              className="px-6 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:bg-gray-400"
            >
              {isSubmitting ? 'Guardando...' : 'Guardar Evaluación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
