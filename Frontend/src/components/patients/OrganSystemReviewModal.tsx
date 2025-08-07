'use client'

import React, { useState } from 'react'
import { X, Plus, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface OrganSystemReview {
  typeReview: string
  review: string
}

interface OrganSystemReviewModalProps {
  isOpen: boolean
  onClose: () => void
  onNext: () => void
  organSystemReviews: OrganSystemReview[]
  onOrganSystemReviewsChange: (reviews: OrganSystemReview[]) => void
}

export default function OrganSystemReviewModal({ 
  isOpen, 
  onClose, 
  onNext, 
  organSystemReviews, 
  onOrganSystemReviewsChange 
}: OrganSystemReviewModalProps) {
  const [formData, setFormData] = useState<OrganSystemReview>({
    typeReview: '',
    review: ''
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!isOpen) return null

  const organSystems = [
    'Cardiovascular',
    'Respiratorio',
    'Gastrointestinal',
    'Genitourinario',
    'Neurológico',
    'Musculoesquelético',
    'Dermatológico',
    'Endocrino',
    'Hematológico',
    'Psiquiátrico',
    'Ojos, oídos, nariz, garganta',
    'Reproductivo'
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddReview = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.typeReview.trim() || !formData.review.trim()) {
      toast.error('Tipo de revisión y hallazgos son requeridos')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:5000/add-organ-system-review', {
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
        const newReviews = [...organSystemReviews, formData]
        onOrganSystemReviewsChange(newReviews)
        
        // Reset form
        setFormData({
          typeReview: '',
          review: ''
        })
      } else {
        toast.error(data.error || 'Error al agregar revisión de sistema')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemoveReview = async (index: number) => {
    try {
      const response = await fetch('http://localhost:5000/remove-organ-system-review', {
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
        const newReviews = organSystemReviews.filter((_, i) => i !== index)
        onOrganSystemReviewsChange(newReviews)
      } else {
        toast.error(data.error || 'Error al eliminar revisión')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    }
  }

  const handleNext = () => {
    onNext()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-800">
            Revisión de Órganos y Sistemas
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6">
          {/* Form to add new review */}
          <form onSubmit={handleAddReview} className="mb-6">
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sistema de Órganos *
                </label>
                <select
                  name="typeReview"
                  value={formData.typeReview}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar sistema</option>
                  {organSystems.map(system => (
                    <option key={system} value={system}>{system}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hallazgos y Observaciones *
                </label>
                <textarea
                  name="review"
                  value={formData.review}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Describa los hallazgos encontrados en la revisión del sistema seleccionado..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
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
                {isSubmitting ? 'Agregando...' : 'Agregar Revisión'}
              </button>
            </div>
          </form>

          {/* List of reviews */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800">
              Revisiones Agregadas ({organSystemReviews.length})
            </h3>
            
            {organSystemReviews.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No se han agregado revisiones de sistemas aún
              </p>
            ) : (
              organSystemReviews.map((review, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-2">
                        Sistema {review.typeReview}
                      </h4>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {review.review}
                      </p>
                    </div>
                    <button
                      onClick={() => handleRemoveReview(index)}
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
            Continuar con Diagnósticos
          </button>
        </div>
      </div>
    </div>
  )
}
