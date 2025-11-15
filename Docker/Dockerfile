# Etapa 1: Construcción con Node 14.21.3
FROM node:14.21.3 AS build

WORKDIR /app

# Copiar e instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar el resto del proyecto
COPY . .

# 🔧 Corregir permisos antes de construir
RUN chmod +x node_modules/.bin/vue-cli-service

# Ejecutar la compilación
RUN npm run build

# Etapa 2: Servidor Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

