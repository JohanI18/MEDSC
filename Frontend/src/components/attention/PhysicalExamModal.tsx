'use client';

import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { attentionService } from '@/services/attention';
import toast from 'react-hot-toast';

interface PhysicalExamModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface PhysicalExamForm {
  typeExamination: string;
  examination: string;
}

interface PhysicalExam {
  typeExamination: string;
  examination: string;
}

export default function PhysicalExamModal({ isOpen, onClose, onSuccess }: PhysicalExamModalProps) {
  const [formData, setFormData] = useState<PhysicalExamForm>({
    typeExamination: '',
    examination: ''
  });
  
  const [exams, setExams] = useState<PhysicalExam[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const examTypes = [
    'Examen General',
    'Cabeza y Cuello',
    'Tórax',
    'Abdomen',
    'Extremidades',
    'Sistema Neurológico',
    'Sistema Cardiovascular',
    'Sistema Respiratorio',
    'Piel y Faneras',
    'Genitourinario',
    'Otros'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddExam = async () => {
    if (!formData.typeExamination.trim() || !formData.examination.trim()) {
      toast.error('Tipo de examen y hallazgos son requeridos');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await attentionService.addPhysicalExam(formData);
      
      if (result.success) {
        setExams(prev => [...prev, { ...formData }]);
        toast.success('Examen físico agregado');
        // Reset form
        setFormData({
          typeExamination: '',
          examination: ''
        });
      } else {
        toast.error(result.error || 'Error al agregar examen físico');
      }
    } catch (error) {
      toast.error('Error inesperado');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemoveExam = async (index: number) => {
    try {
      const result = await attentionService.removePhysicalExam(index);
      
      if (result.success) {
        setExams(prev => prev.filter((_, i) => i !== index));
        toast.success('Examen físico eliminado');
      } else {
        toast.error(result.error || 'Error al eliminar examen físico');
      }
    } catch (error) {
      toast.error('Error inesperado');
    }
  };

  const handleContinue = () => {
    onSuccess();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Examen Físico</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Add New Exam Form */}
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Agregar Examen Físico</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Examen
                </label>
                <select
                  name="typeExamination"
                  value={formData.typeExamination}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar tipo...</option>
                  {examTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hallazgos
                </label>
                <textarea
                  name="examination"
                  value={formData.examination}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describa los hallazgos del examen..."
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleAddExam}
                disabled={isSubmitting || !formData.typeExamination.trim() || !formData.examination.trim()}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
              >
                <Plus size={16} />
                {isSubmitting ? 'Agregando...' : 'Agregar Examen'}
              </button>
            </div>
          </div>

          {/* Exams List */}
          {exams.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Exámenes Agregados</h3>
              <div className="space-y-3">
                {exams.map((exam, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{exam.typeExamination}</h4>
                        <p className="text-gray-600 mt-1">{exam.examination}</p>
                      </div>
                      <button
                        onClick={() => handleRemoveExam(index)}
                        className="text-red-500 hover:text-red-700 ml-4"
                      >
                        <Trash2 size={18} />
                      </button>
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
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Continuar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
