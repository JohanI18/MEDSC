# 🚀 Guía de Inicio Rápido - MEDSC Frontend

## 📋 Resumen

He creado un frontend completo en Next.js con TypeScript que consume todas las APIs de tu aplicación Flask MEDSC. El frontend incluye:

### ✅ Funcionalidades Implementadas

1. **Sistema de Autenticación**
   - Login con validación
   - Integración con APIs de Flask

2. **Dashboard**
   - Estadísticas generales
   - Acciones rápidas
   - Actividad reciente

3. **Gestión de Pacientes**
   - Listado con búsqueda
   - Formulario completo para agregar pacientes
   - Eliminación de pacientes
   - Validaciones con Zod

4. **Arquitectura Moderna**
   - Next.js 14 con App Router
   - TypeScript para type safety
   - TailwindCSS para estilos
   - React Query para estado del servidor
   - Servicios organizados por módulos

## 🛠️ Cómo Ejecutar

### Método 1: Script Automático (Recomendado)
```bash
# Navegar a la carpeta Frontend
cd "Frontend"

# Ejecutar el script de instalación
setup.bat
```

### Método 2: Manual
```bash
# Navegar a la carpeta Frontend
cd "Frontend"

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### Requisitos Previos
- ✅ Node.js 18+ instalado
- ✅ Backend Flask ejecutándose en `http://localhost:5000`

## 📁 Estructura del Frontend

```
Frontend/
├── src/
│   ├── app/                    # Páginas (App Router)
│   │   ├── dashboard/          # Dashboard principal
│   │   ├── patients/           # Gestión de pacientes
│   │   └── login/              # Autenticación
│   ├── components/             # Componentes reutilizables
│   │   ├── layout/             # Layout y navegación
│   │   └── patients/           # Componentes específicos
│   ├── services/               # Servicios API
│   │   ├── auth.ts             # Autenticación
│   │   ├── patients.ts         # Pacientes
│   │   └── attention.ts        # Atención médica
│   ├── lib/                    # Configuraciones
│   ├── types/                  # Tipos TypeScript
│   └── styles/                 # Estilos globales
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## 🌐 URLs del Frontend

Después de ejecutar `npm run dev`, tendrás disponible:

- **Frontend**: http://localhost:3000
- **Login**: http://localhost:3000/login
- **Dashboard**: http://localhost:3000/dashboard
- **Pacientes**: http://localhost:3000/patients

## 🔗 APIs Integradas

### Autenticación
- ✅ `POST /login` - Iniciar sesión
- ✅ `POST /register` - Registro
- ✅ `POST /logout` - Cerrar sesión

### Pacientes
- ✅ `GET /patients` - Listar pacientes
- ✅ `POST /add-patients` - Crear paciente
- ✅ `GET /get-patient-details/:id` - Detalles
- ✅ `POST /update-patient/:id` - Actualizar
- ✅ `POST /patient/:id/delete` - Eliminar
- ✅ `POST /patient/:id/add-allergy` - Agregar alergia
- ✅ `DELETE /patient/allergy/:id` - Eliminar alergia
- ✅ `POST /patient/:id/add-contact` - Contacto emergencia
- ✅ Y más...

### Atención Médica
- ✅ `POST /select-patient-for-attention` - Seleccionar paciente
- ✅ `POST /add-vital-signs` - Signos vitales
- ✅ `POST /add-initial-evaluation` - Evaluación inicial
- ✅ `POST /add-physical-exam` - Examen físico
- ✅ Y muchas más APIs de atención...

## 🎨 Características del Diseño

- **Responsive**: Funciona en desktop, tablet y móvil
- **Tema Médico**: Colores azules y verdes profesionales
- **Componentes Reutilizables**: Botones, formularios, cards
- **Navegación Intuitiva**: Sidebar con iconos
- **Notificaciones**: Toast messages para feedback
- **Loading States**: Indicadores de carga
- **Error Handling**: Manejo elegante de errores

## 🔄 Próximos Pasos

### Para Completar (Fácil de Implementar)

1. **Módulo de Atención**
   - Formulario de signos vitales
   - Evaluación inicial
   - Examen físico
   - Diagnósticos

2. **Chat Médico**
   - Interfaz de chat
   - WebSocket integration

3. **Historial de Pacientes**
   - Vista detallada
   - Timeline de atenciones

4. **Reportes**
   - Dashboard con gráficos
   - Exportación de datos

## 🚨 Solución de Problemas

### Error: "Cannot find module 'react'"
```bash
npm install
```

### Error de conexión API
- Verifica que Flask esté en `http://localhost:5000`
- Revisa el archivo `.env.local` para cambiar la URL

### Puerto 3000 ocupado
```bash
# Usar otro puerto
npm run dev -- --port 3001
```

## 📝 Notas Importantes

1. **CORS**: El backend ya tiene CORS configurado para `localhost:3000`
2. **Proxy**: Next.js está configurado para proxy a Flask
3. **TypeScript**: Todos los tipos están definidos
4. **Validaciones**: Zod para validación de formularios
5. **Estado**: React Query para cache y sincronización

## 💡 Comandos Útiles

```bash
# Desarrollo
npm run dev

# Construcción
npm run build

# Producción
npm start

# Linting
npm run lint
```

¡Tu frontend está listo para usar! 🎉
