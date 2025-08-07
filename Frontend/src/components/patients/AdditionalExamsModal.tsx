'use client'

import React, { useState } from 'react'
import { X, Plus, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Histopathology {
  histopathology: string
}

interface Imaging {
  typeImaging: string
  imaging: string
}

interface Laboratory {
  typeExam: string
  exam: string
}

interface AdditionalExamsModalProps {
  isOpen: boolean
  onClose: () => void
  onNext: () => void
  histopathologies: Histopathology[]
  imagings: Imaging[]
  laboratories: Laboratory[]
  onHistopathologiesChange: (histos: Histopathology[]) => void
  onImagingsChange: (imagings: Imaging[]) => void
  onLaboratoriesChange: (labs: Laboratory[]) => void
}

export default function AdditionalExamsModal({ 
  isOpen, 
  onClose, 
  onNext, 
  histopathologies,
  imagings,
  laboratories,
  onHistopathologiesChange,
  onImagingsChange,
  onLaboratoriesChange
}: AdditionalExamsModalProps) {
  const [activeTab, setActiveTab] = useState<'histopathology' | 'imaging' | 'laboratory'>('histopathology')
  const [formData, setFormData] = useState({
    histopathology: {
      histopathology: ''
    },
    imaging: {
      typeImaging: '',
      imaging: ''
    },
    laboratory: {
      typeExam: '',
      exam: ''
    }
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!isOpen) return null

  const imagingTypes = [
    'Radiografía',
    'TAC (Tomografía)',
    'Resonancia Magnética',
    'Ecografía',
    'Mamografía',
    'Densitometría',
    'Angiografía',
    'Endoscopía',
    'Colonoscopía',
    'Ecocardiograma'
  ]

  const laboratoryTypes = [
    'Hemograma Completo',
    'Química Sanguínea',
    'Perfil Lipídico',
    'Función Hepática',
    'Función Renal',
    'Electrolitos',
    'Hormonas Tiroideas',
    'Marcadores Cardíacos',
    'Coagulación',
    'Examen de Orina',
    'Cultivos',
    'Serología'
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [activeTab]: {
        ...prev[activeTab],
        [name]: value
      }
    }))
  }

  const handleAddHistopathology = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.histopathology.histopathology.trim()) {
      toast.error('El resultado histopatológico es requerido')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:5000/add-histopathology', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify(formData.histopathology)
      })

      const data = await response.json()

      if (data.success) {
        toast.success(data.message)
        const newHistopathologies = [...histopathologies, formData.histopathology]
        onHistopathologiesChange(newHistopathologies)
        
        // Reset form
        setFormData(prev => ({
          ...prev,
          histopathology: { histopathology: '' }
        }))
      } else {
        toast.error(data.error || 'Error al agregar histopatología')
      }
    } catch (error) {
      toast.error('Error de conexión al servidor')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleAddImaging = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.imaging.typeImaging.trim() || !formData.imaging.imaging.trim()) {
      toast.error('Tipo de imagen y resultado son requeridos')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:5000/add-imaging', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify(formData.imaging)
      })

      const data = await response.json()

      if (data.success) {
        toast.success(data.message)
        const newImagings = [...imagings, formData.imaging]
        onImagingsChange(newImagings)
        
        // Reset form
        setFormData(prev => ({
          ...prev,
          imaging: { typeImaging: '', imaging: '' }
        }))
      } else {
        toast.error(data.error || 'Error al agregar imagen')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleAddLaboratory = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.laboratory.typeExam.trim() || !formData.laboratory.exam.trim()) {
      toast.error('Tipo de examen y resultado son requeridos')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:5000/add-laboratory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify(formData.laboratory)
      })

      const data = await response.json()

      if (data.success) {
        toast.success(data.message)
        const newLaboratories = [...laboratories, formData.laboratory]
        onLaboratoriesChange(newLaboratories)
        
        // Reset form
        setFormData(prev => ({
          ...prev,
          laboratory: { typeExam: '', exam: '' }
        }))
      } else {
        toast.error(data.error || 'Error al agregar laboratorio')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemoveHistopathology = async (index: number) => {
    try {
      const response = await fetch('http://localhost:5000/remove-histopathology', {
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
        const newHistopathologies = histopathologies.filter((_, i) => i !== index)
        onHistopathologiesChange(newHistopathologies)
      } else {
        toast.error(data.error || 'Error al eliminar histopatología')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    }
  }

  const handleRemoveImaging = async (index: number) => {
    try {
      const response = await fetch('http://localhost:5000/remove-imaging', {
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
        const newImagings = imagings.filter((_, i) => i !== index)
        onImagingsChange(newImagings)
      } else {
        toast.error(data.error || 'Error al eliminar imagen')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    }
  }

  const handleRemoveLaboratory = async (index: number) => {
    try {
      const response = await fetch('http://localhost:5000/remove-laboratory', {
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
        const newLaboratories = laboratories.filter((_, i) => i !== index)
        onLaboratoriesChange(newLaboratories)
      } else {
        toast.error(data.error || 'Error al eliminar laboratorio')
      }
    } catch (error) {      toast.error('Error de conexión al servidor')
    }
  }

  const renderHistopathologyTab = () => (
    <div>
      <form onSubmit={handleAddHistopathology} className="mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Resultado Histopatológico *
          </label>
          <textarea
            name="histopathology"
            value={formData.histopathology.histopathology}
            onChange={handleInputChange}
            rows={4}
            placeholder="Describa los resultados del examen histopatológico..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="mt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <Plus className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Agregando...' : 'Agregar Histopatología'}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        <h4 className="font-medium text-gray-800">
          Histopatologías Agregadas ({histopathologies.length})
        </h4>
        
        {histopathologies.length === 0 ? (
          <p className="text-gray-500 text-center py-4">
            No se han agregado histopatologías aún
          </p>
        ) : (
          histopathologies.map((histo, index) => (
            <div key={index} className="bg-gray-50 p-4 rounded-lg border">
              <div className="flex justify-between items-start">
                <p className="text-sm text-gray-600 flex-1">
                  {histo.histopathology}
                </p>
                <button
                  onClick={() => handleRemoveHistopathology(index)}
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
  )

  const renderImagingTab = () => (
    <div>
      <form onSubmit={handleAddImaging} className="mb-6">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Estudio *
            </label>
            <select
              name="typeImaging"
              value={formData.imaging.typeImaging}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Seleccionar tipo de estudio</option>
              {imagingTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resultado del Estudio *
            </label>
            <textarea
              name="imaging"
              value={formData.imaging.imaging}
              onChange={handleInputChange}
              rows={4}
              placeholder="Describa los hallazgos del estudio de imagen..."
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
            {isSubmitting ? 'Agregando...' : 'Agregar Imagen'}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        <h4 className="font-medium text-gray-800">
          Estudios de Imagen Agregados ({imagings.length})
        </h4>
        
        {imagings.length === 0 ? (
          <p className="text-gray-500 text-center py-4">
            No se han agregado estudios de imagen aún
          </p>
        ) : (
          imagings.map((imaging, index) => (
            <div key={index} className="bg-gray-50 p-4 rounded-lg border">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h5 className="font-medium text-gray-900 mb-1">
                    {imaging.typeImaging}
                  </h5>
                  <p className="text-sm text-gray-600">
                    {imaging.imaging}
                  </p>
                </div>
                <button
                  onClick={() => handleRemoveImaging(index)}
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
  )

  const renderLaboratoryTab = () => (
    <div>
      <form onSubmit={handleAddLaboratory} className="mb-6">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Examen *
            </label>
            <select
              name="typeExam"
              value={formData.laboratory.typeExam}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Seleccionar tipo de examen</option>
              {laboratoryTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resultado del Examen *
            </label>
            <textarea
              name="exam"
              value={formData.laboratory.exam}
              onChange={handleInputChange}
              rows={4}
              placeholder="Describa los resultados del examen de laboratorio..."
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
            {isSubmitting ? 'Agregando...' : 'Agregar Laboratorio'}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        <h4 className="font-medium text-gray-800">
          Exámenes de Laboratorio Agregados ({laboratories.length})
        </h4>
        
        {laboratories.length === 0 ? (
          <p className="text-gray-500 text-center py-4">
            No se han agregado exámenes de laboratorio aún
          </p>
        ) : (
          laboratories.map((lab, index) => (
            <div key={index} className="bg-gray-50 p-4 rounded-lg border">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h5 className="font-medium text-gray-900 mb-1">
                    {lab.typeExam}
                  </h5>
                  <p className="text-sm text-gray-600">
                    {lab.exam}
                  </p>
                </div>
                <button
                  onClick={() => handleRemoveLaboratory(index)}
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
  )

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-800">
            Exámenes Adicionales
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6">
          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('histopathology')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'histopathology'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Histopatología
              </button>
              <button
                onClick={() => setActiveTab('imaging')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'imaging'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Imagenología
              </button>
              <button
                onClick={() => setActiveTab('laboratory')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'laboratory'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Laboratorio
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'histopathology' && renderHistopathologyTab()}
          {activeTab === 'imaging' && renderImagingTab()}
          {activeTab === 'laboratory' && renderLaboratoryTab()}
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
            onClick={onNext}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Continuar con Evolución
          </button>
        </div>
      </div>
    </div>
  )
}
