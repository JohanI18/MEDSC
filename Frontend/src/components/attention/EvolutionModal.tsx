'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { attentionService } from '@/services/attention';
import toast from 'react-hot-toast';

interface EvolutionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function EvolutionModal({ isOpen, onClose, onSuccess }: EvolutionModalProps) {
  const [evolution, setEvolution] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!evolution.trim()) {
      toast.error('La evolución es requerida');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await attentionService.addEvolution({ evolution });
      
      if (result.success) {
        toast.success('Evolución guardada exitosamente');
        onSuccess();
        onClose();
        setEvolution('');
      } else {
        toast.error(result.error || 'Error al guardar evolución');
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
            <h2 className="text-xl font-semibold text-gray-900">Evolución del Paciente</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Evolución <span className="text-red-500">*</span>
            </label>
            <textarea
              value={evolution}
              onChange={(e) => setEvolution(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describa la evolución del paciente, respuesta al tratamiento, pronóstico, recomendaciones..."
              required
            />
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
              disabled={isSubmitting || !evolution.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              {isSubmitting ? 'Guardando...' : 'Guardar Evolución'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
