# Usar Node.js 18 como imagen base
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json (si existe)
COPY package*.json ./

# Instalar todas las dependencias (incluyendo devDependencies para la construcción)
RUN npm ci

# Copiar el código fuente
COPY . .

# Construir la aplicación
RUN npm run build

# Exponer el puerto 3000
EXPOSE 3000

# Variables de entorno
ENV NODE_ENV=production

# Comando para ejecutar la aplicación
CMD ["npm", "start"]
