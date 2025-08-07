# MEDSC Frontend

Frontend moderno desarrollado con Next.js y TypeScript para la aplicación médica MEDSC.

## 🚀 Características

- **Next.js 14** con App Router
- **TypeScript** para type safety
- **TailwindCSS** para estilos
- **React Query** para manejo de estado del servidor
- **React Hook Form** para formularios
- **Axios** para llamadas HTTP
- **Lucide React** para iconos
- **React Hot Toast** para notificaciones

## 📋 Prerequisitos

- Node.js 18.0 o superior
- npm o yarn
- El backend de Flask ejecutándose en `http://localhost:5000`

## 🛠️ Instalación

1. Navega a la carpeta del frontend:
```bash
cd Frontend
```

2. Instala las dependencias:
```bash
npm install
```

3. Configura las variables de entorno (opcional):
```bash
# Crear archivo .env.local
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. Ejecuta el servidor de desarrollo:
```bash
npm run dev
```

5. Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## 🏗️ Estructura del Proyecto

```
Frontend/
├── src/
│   ├── app/                 # App Router pages
│   │   ├── dashboard/       # Dashboard page
│   │   ├── patients/        # Patients management
│   │   ├── login/          # Login page
│   │   └── layout.tsx      # Root layout
│   ├── components/         # Reusable components
│   │   ├── layout/         # Layout components
│   │   └── providers.tsx   # App providers
│   ├── services/          # API services
│   │   ├── auth.ts        # Authentication
│   │   ├── patients.ts    # Patient management
│   │   └── attention.ts   # Medical attention
│   ├── lib/               # Utilities
│   │   └── api.ts         # Axios configuration
│   ├── types/             # TypeScript types
│   │   └── index.ts       # Type definitions
│   └── styles/            # Global styles
│       └── globals.css    # Tailwind CSS
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## 🌐 API Endpoints Integrados

### Autenticación
- `POST /login` - Iniciar sesión
- `POST /register` - Registro de usuario
- `POST /logout` - Cerrar sesión

### Pacientes
- `GET /patients` - Obtener todos los pacientes
- `POST /add-patients` - Crear nuevo paciente
- `GET /get-patient-details/:id` - Obtener detalles del paciente
- `POST /update-patient/:id` - Actualizar paciente
- `POST /patient/:id/delete` - Eliminar paciente

### Gestión de Pacientes
- `POST /patient/:id/add-allergy` - Agregar alergia
- `DELETE /patient/allergy/:id` - Eliminar alergia
- `POST /patient/:id/add-contact` - Agregar contacto de emergencia
- `DELETE /patient/contact/:id` - Eliminar contacto
- `POST /patient/:id/add-condition` - Agregar condición preexistente
- `DELETE /patient/condition/:id` - Eliminar condición
- `POST /patient/:id/add-family-background` - Agregar antecedente familiar
- `DELETE /patient/family-background/:id` - Eliminar antecedente

### Atención Médica
- `POST /select-patient-for-attention` - Seleccionar paciente para atención
- `POST /add-vital-signs` - Agregar signos vitales
- `POST /add-initial-evaluation` - Agregar evaluación inicial
- `POST /add-physical-exam` - Agregar examen físico
- `POST /add-diagnostic` - Agregar diagnóstico
- `POST /add-treatment` - Agregar tratamiento
- `POST /add-laboratory` - Agregar examen de laboratorio
- `POST /add-imaging` - Agregar estudio de imagen
- `POST /complete-attention` - Completar atención

## 📱 Funcionalidades Implementadas

### ✅ Completadas
- Sistema de autenticación
- Dashboard con estadísticas
- Listado de pacientes con búsqueda
- Estructura de servicios para todas las APIs
- Layout responsivo con navegación
- Manejo de errores y notificaciones
- Configuración de TypeScript y TailwindCSS

### 🚧 En Desarrollo
- Formularios de creación/edición de pacientes
- Módulo de atención médica completo
- Chat médico
- Historial de pacientes
- Reportes y estadísticas avanzadas
- Validaciones de formularios
- Paginación en listados

## 🎨 Diseño

El frontend utiliza un diseño limpio y moderno con:
- Paleta de colores médicos (azules y verdes)
- Componentes reutilizables
- Diseño responsive
- Iconos de Lucide React
- Animaciones suaves

## 🔧 Comandos Disponibles

```bash
# Desarrollo
npm run dev

# Compilar para producción
npm run build

# Ejecutar en producción
npm start

# Linting
npm run lint
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
