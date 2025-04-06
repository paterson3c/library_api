# API REST para Gestión de Usuarios y Archivos

Este proyecto consiste en dos microservicios desarrollados en Python para la gestión de usuarios y bibliotecas de archivos, con autenticación personalizada y despliegue mediante Docker.

## 🔧 Tecnologías
- Python 3
- Quart
- Docker
- Autenticación con tokens propios

## 🚀 Funcionalidades
- Microservicio de usuarios:
  - Registro y login
  - Generación y validación de tokens personalizados
- Microservicio de archivos:
  - Gestión de bibliotecas de archivos por usuario
  - Rutas protegidas mediante verificación de tokens
- Contenedores independientes para cada servicio

## 📁 Estructura
```
library_api/
├── users_service/
│   ├── main.py
│   └── auth.py
├── test/
│   └── client.py
├── files_service/
│   ├── main.py
│   └── files.py
├── docker-compose.yml
└── requirements.txt
```

## ▶️ Ejecución con Docker
```bash
docker-compose up --build
```

## 📌 Notas
Este proyecto demuestra cómo implementar una arquitectura de microservicios sencilla, enfocada en la separación de responsabilidades y la seguridad mediante tokens propios.

## 👤 Autor
Miguel Jesús Paterson González – [GitHub](https://github.com/paterson3c)
