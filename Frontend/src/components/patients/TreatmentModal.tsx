'use client'

import React, { useState } from 'react'
import { X, Plus, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Treatment {
  medicament: string
  via: string
  dosage: string
  unity: string
  frequency: string
  indications: string
  warning?: string
}

interface TreatmentModalProps {
  isOpen: boolean
  onClose: () => void
  onNext: () => void
  treatments: Treatment[]
  onTreatmentsChange: (treatments: Treatment[]) => void
}

export default function TreatmentModal({ 
  isOpen, 
  onClose, 
  onNext, 
  treatments, 
  onTreatmentsChange 
}: TreatmentModalProps) {
  const [formData, setFormData] = useState<Treatment>({
    medicament: '',
    via: '',
    dosage: '',
    unity: '',
    frequency: '',
    indications: '',
    warning: ''
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!isOpen) return null

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddTreatment = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.medicament.trim() || !formData.via.trim() || !formData.dosage.trim() || 
        !formData.unity.trim() || !formData.frequency.trim() || !formData.indications.trim()) {
      toast.error('Todos los campos requeridos deben completarse')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:5000/add-treatment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (data.success) {
        toast.success(data.message)
        const newTreatments = [...treatments, formData]
        onTreatmentsChange(newTreatments)
        
        // Reset form
        setFormData({
          medicament: '',
          via: '',
          dosage: '',
          unity: '',
          frequency: '',
          indications: '',
          warning: ''
        })
      } else {
        toast.error(data.error || 'Error al agregar tratamiento')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemoveTreatment = async (index: number) => {
    try {
      const response = await fetch('http://localhost:5000/remove-treatment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify({ index })
      })

      const data = await response.json()

      if (data.success) {
        toast.success(data.message)
        const newTreatments = treatments.filter((_, i) => i !== index)
        onTreatmentsChange(newTreatments)
      } else {
        toast.error(data.error || 'Error al eliminar tratamiento')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    }
  }

  const handleNext = () => {
    if (treatments.length === 0) {
      toast.error('Debe agregar al menos un tratamiento antes de continuar')
      return
    }
    onNext()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-800">
            Tratamientos y Medicamentos
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6">
          {/* Form to add new treatment */}
          <form onSubmit={handleAddTreatment} className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Medicamento *
                </label>
                <input
                  type="text"
                  name="medicament"
                  value={formData.medicament}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Vía de Administración *
                </label>
                <select
                  name="via"
                  value={formData.via}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar vía</option>
                  <option value="oral">Oral</option>
                  <option value="intravenosa">Intravenosa</option>
                  <option value="intramuscular">Intramuscular</option>
                  <option value="subcutanea">Subcutánea</option>
                  <option value="topica">Tópica</option>
                  <option value="inhalatoria">Inhalatoria</option>
                  <option value="rectal">Rectal</option>
                  <option value="oftálmica">Oftálmica</option>
                  <option value="ótica">Ótica</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dosis *
                </label>
                <input
                  type="text"
                  name="dosage"
                  value={formData.dosage}
                  onChange={handleInputChange}
                  placeholder="Ej: 500"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unidad *
                </label>
                <select
                  name="unity"
                  value={formData.unity}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar unidad</option>
                  <option value="mg">mg</option>
                  <option value="g">g</option>
                  <option value="ml">ml</option>
                  <option value="mcg">mcg</option>
                  <option value="UI">UI</option>
                  <option value="comprimidos">comprimidos</option>
                  <option value="cápsulas">cápsulas</option>
                  <option value="gotas">gotas</option>
                  <option value="cucharadas">cucharadas</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Frecuencia *
                </label>
                <select
                  name="frequency"
                  value={formData.frequency}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar frecuencia</option>
                  <option value="cada 6 horas">Cada 6 horas</option>
                  <option value="cada 8 horas">Cada 8 horas</option>
                  <option value="cada 12 horas">Cada 12 horas</option>
                  <option value="cada 24 horas">Cada 24 horas</option>
                  <option value="1 vez al día">1 vez al día</option>
                  <option value="2 veces al día">2 veces al día</option>
                  <option value="3 veces al día">3 veces al día</option>
                  <option value="según necesidad">Según necesidad</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Indicaciones *
                </label>
                <textarea
                  name="indications"
                  value={formData.indications}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Advertencias
                </label>
                <textarea
                  name="warning"
                  value={formData.warning}
                  onChange={handleInputChange}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="mt-4">
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <Plus className="h-4 w-4 mr-2" />
                {isSubmitting ? 'Agregando...' : 'Agregar Tratamiento'}
              </button>
            </div>
          </form>

          {/* List of treatments */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800">
              Tratamientos Agregados ({treatments.length})
            </h3>
            
            {treatments.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No se han agregado tratamientos aún
              </p>
            ) : (
              treatments.map((treatment, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-2">
                        {treatment.medicament}
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Vía:</span> {treatment.via}
                        </div>
                        <div>
                          <span className="font-medium">Dosis:</span> {treatment.dosage} {treatment.unity}
                        </div>
                        <div>
                          <span className="font-medium">Frecuencia:</span> {treatment.frequency}
                        </div>
                        <div className="md:col-span-1">
                          <span className="font-medium">Indicaciones:</span> {treatment.indications}
                        </div>
                      </div>
                      {treatment.warning && (
                        <div className="mt-2 text-sm text-red-600">
                          <span className="font-medium">Advertencias:</span> {treatment.warning}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => handleRemoveTreatment(index)}
                      className="ml-4 text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center px-6 py-4 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-100 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleNext}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Continuar con Exámenes
          </button>
        </div>
      </div>
    </div>
  )
}
