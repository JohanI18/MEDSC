'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { attentionService } from '@/services/attention';
import toast from 'react-hot-toast';

interface VitalSignsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface VitalSignsForm {
  weight: string;
  height: string;
  temperature: string;
  bloodPressure: string;
  heartRate: string;
  oxygenSaturation: string;
  breathingFrequency: string;
  glucose: string;
  hemoglobin: string;
}

export default function VitalSignsModal({ isOpen, onClose, onSuccess }: VitalSignsModalProps) {
  const [formData, setFormData] = useState<VitalSignsForm>({
    weight: '',
    height: '',
    temperature: '',
    bloodPressure: '',
    heartRate: '',
    oxygenSaturation: '',
    breathingFrequency: '',
    glucose: '',
    hemoglobin: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Filter out empty values
      const cleanedData = Object.fromEntries(
        Object.entries(formData).filter(([_, value]) => value.trim() !== '')
      );

      const result = await attentionService.addVitalSigns(cleanedData);
      
      if (result.success) {
        toast.success('Signos vitales guardados exitosamente');
        onSuccess();
        onClose();
        // Reset form
        setFormData({
          weight: '',
          height: '',
          temperature: '',
          bloodPressure: '',
          heartRate: '',
          oxygenSaturation: '',
          breathingFrequency: '',
          glucose: '',
          hemoglobin: ''
        });
      } else {
        toast.error(result.error || 'Error al guardar signos vitales');
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
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Signos Vitales</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Peso (kg)
              </label>
              <input
                type="number"
                name="weight"
                value={formData.weight}
                onChange={handleInputChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="70.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Altura (cm)
              </label>
              <input
                type="number"
                name="height"
                value={formData.height}
                onChange={handleInputChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="170"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperatura (°C)
              </label>
              <input
                type="number"
                name="temperature"
                value={formData.temperature}
                onChange={handleInputChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="36.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Presión Arterial (mmHg)
              </label>
              <input
                type="text"
                name="bloodPressure"
                value={formData.bloodPressure}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="120/80"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Frecuencia Cardíaca (lpm)
              </label>
              <input
                type="number"
                name="heartRate"
                value={formData.heartRate}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="72"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Saturación de Oxígeno (%)
              </label>
              <input
                type="number"
                name="oxygenSaturation"
                value={formData.oxygenSaturation}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="98"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Frecuencia Respiratoria (rpm)
              </label>
              <input
                type="number"
                name="breathingFrequency"
                value={formData.breathingFrequency}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="16"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Glucosa (mg/dL)
              </label>
              <input
                type="number"
                name="glucose"
                value={formData.glucose}
                onChange={handleInputChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hemoglobina (g/dL)
              </label>
              <input
                type="number"
                name="hemoglobin"
                value={formData.hemoglobin}
                onChange={handleInputChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="14.5"
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
              disabled={isSubmitting}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
            >
              {isSubmitting ? 'Guardando...' : 'Guardar Signos Vitales'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
