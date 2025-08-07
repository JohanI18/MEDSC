'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/layout/Layout';
import { Users, Stethoscope, Calendar, TrendingUp } from 'lucide-react';
import { dashboardService, DashboardStats } from '@/services/dashboard';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await dashboardService.getStats();
        if (response.success && response.data) {
          setStats(response.data);
        } else {
          setError(response.error || 'Error al cargar estadísticas');
        }
      } catch (err) {
        setError('Error al cargar estadísticas');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const dashboardCards = [
    {
      name: 'Total Pacientes',
      value: stats?.totalPatients || 0,
      icon: Users,
      color: 'text-blue-600'
    },
    {
      name: 'Atenciones Totales',
      value: stats?.totalAttentions || 0,
      icon: Stethoscope,
      color: 'text-green-600'
    },
    {
      name: 'Atenciones Hoy',
      value: stats?.attentionsToday || 0,
      icon: Calendar,
      color: 'text-purple-600'
    },
    {
      name: 'Atenciones Este Mes',
      value: stats?.attentionsThisMonth || 0,
      icon: TrendingUp,
      color: 'text-orange-600'
    }
  ];

  if (loading) {
    return (
      <Layout currentPath="/dashboard">
        <div className="flex justify-center items-center min-h-96">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout currentPath="/dashboard">
        <div className="text-center py-12">
          <div className="text-red-600 text-lg">{error}</div>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 btn-primary"
          >
            Reintentar
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPath="/dashboard">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Resumen general del sistema médico</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {dashboardCards.map((card) => {
            const Icon = card.icon;
            return (
              <div key={card.name} className="card">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Icon className={`h-8 w-8 ${card.color}`} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {card.name}
                      </dt>
                      <dd>
                        <div className="text-2xl font-semibold text-gray-900">
                          {card.value}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Acciones Rápidas</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <button 
              onClick={() => window.location.href = '/patients'}
              className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Users className="h-6 w-6 text-primary-600 mr-3" />
              <div className="text-left">
                <div className="font-medium text-gray-900">Gestionar Pacientes</div>
                <div className="text-sm text-gray-500">Ver y gestionar pacientes</div>
              </div>
            </button>
            
            <button 
              onClick={() => window.location.href = '/attention'}
              className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Stethoscope className="h-6 w-6 text-primary-600 mr-3" />
              <div className="text-left">
                <div className="font-medium text-gray-900">Nueva Atención</div>
                <div className="text-sm text-gray-500">Iniciar una nueva consulta</div>
              </div>
            </button>
            
            <button 
              onClick={() => window.location.href = '/chat'}
              className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Calendar className="h-6 w-6 text-primary-600 mr-3" />
              <div className="text-left">
                <div className="font-medium text-gray-900">Chat Médico</div>
                <div className="text-sm text-gray-500">Consultar con otros doctores</div>
              </div>
            </button>
          </div>
        </div>

        {/* Top Doctors */}
        {stats && stats.topDoctors && stats.topDoctors.length > 0 && (
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Doctores Más Activos</h2>
            <div className="space-y-3">
              {stats.topDoctors.slice(0, 5).map((doctor, index) => (
                <div key={doctor.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-primary-600">#{index + 1}</span>
                      </div>
                    </div>
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">{doctor.name}</div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {doctor.attentionCount} atenciones
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Diagnoses */}
        {stats && stats.topDiagnoses && stats.topDiagnoses.length > 0 && (
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Diagnósticos Más Comunes</h2>
            <div className="space-y-3">
              {stats.topDiagnoses.slice(0, 10).map((diagnosis, index) => (
                <div key={diagnosis.disease} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-medical-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-medical-600">#{index + 1}</span>
                      </div>
                    </div>
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">{diagnosis.disease}</div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {diagnosis.count} casos
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
