Proyecto Vue – Instalación Local (PC)

Este proyecto usa Vue 2, Vue CLI 4, Node 14, Firebase 8 y otros módulos.
Estas instrucciones son para correrlo en Windows o PC local sin Docker.

Requisitos

Node.js 14.21.3 (IMPORTANTE para evitar errores con vue-cli-service)

npm (incluido con Node)

Git (opcional)

Instalación
Instalar Node 14

Descargar desde:
https://nodejs.org/dist/latest-v14.x/

Verificar instalación:

node -v
npm -v

Descargar el proyecto

Opciones:

Clonar desde Git:

git clone https://tu-repo.git proyecto
cd proyecto


O copiar los archivos manualmente.

Instalar dependencias
npm install

Ejecutar el proyecto en modo desarrollo
npm run serve


Se abrirá en:

http://localhost:8080

Compilar para producción
npm run build


Los archivos finales quedan en:

/dist


Puedes servirlos con cualquier hosting (Netlify, Render, Apache, XAMPP, Nginx, etc).

-------------------------------------------------------------------------------------

Proyecto Vue – Despliegue en Servidor Linux con Docker

Este README explica cómo construir y ejecutar este proyecto en un servidor Linux usando Docker.

Requisitos

Servidor Linux con:

Docker instalado

(Opcional) Docker Compose

Puerto 80 libre

Para instalar Docker:

curl -fsSL https://get.docker.com | sudo bash

Estructura del Dockerfile

El proyecto usa un build multietapa:

Node 14.21.3 → Construye el proyecto

Nginx Alpine → Sirve la app en producción

Construir la imagen

En la raíz del proyecto:

sudo docker build -t proyecto-vue .

Ejecutar el contenedor
sudo docker run -d -p 80:80 --name proyecto-vue proyecto-vue