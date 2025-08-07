'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { attentionService } from '@/services/attention';
import toast from 'react-hot-toast';

interface CompleteAttentionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  patientName?: string;
}

export default function CompleteAttentionModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  patientName 
}: CompleteAttentionModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleComplete = async () => {
    setIsSubmitting(true);

    try {
      const result = await attentionService.completeAttention();
      
      if (result.success) {
        toast.success('¡Atención completada exitosamente!');
        onSuccess();
        onClose();
      } else {
        toast.error(result.error || 'Error al completar atención');
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
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Completar Atención</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="text-center mb-6">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ¿Finalizar la atención?
            </h3>
            <p className="text-gray-600">
              {patientName 
                ? `Está a punto de finalizar la atención médica para ${patientName}.`
                : 'Está a punto de finalizar la atención médica.'
              }
            </p>
            <p className="text-gray-600 mt-2">
              Una vez completada, no podrá hacer más modificaciones.
            </p>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleComplete}
              disabled={isSubmitting}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
            >
              {isSubmitting ? 'Finalizando...' : 'Finalizar Atención'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
