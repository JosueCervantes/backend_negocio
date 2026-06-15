# Negocio Server

Backend API para una aplicación de negocios, construida con FastAPI, SQLModel, MySQL, Docker y LocalStack para simular servicios de AWS en local.

## Stack

- Python 3.12
- FastAPI
- SQLModel / SQLAlchemy
- Alembic
- MySQL 8
- Docker / Docker Compose
- LocalStack
- Boto3
- JWT Auth
- Pydantic v2

## Estructura General

```txt
negocio-server/
  app/
    dto/
    router/
  alembic/
  interfaces/
  localstack-data/
  localstack-init/
  models/
  swagger/
  utils/
  worker/
  .env
  .env.example
  .gitignore
  alembic.ini
  docker-compose.yml
  Dockerfile
  requirements.txt
  README.md
```

## Requerimientos
- Antes de levantar el proyecto necesitas tener instalado:
- Docker Desktop
- Python no es obligatorio localmente si todo se ejecuta con Docker
- MySQL Workbench opcional para revisar la base de datos
- Postman opcional para probar endpoints

## Comando de docker
- docker compose up --build -d -> construye y levanta contenedores
- docker compose down -> bajar contenedores
- docker system prune --all -> borra contenedores
- docker volume prune --all -> borra volumenes
- docker exec -it localstack bash -> ejecuta localstack que es simulador completo de aws
- docker exec -it negocio_backend alembic init alembic -> corre alembic en el contenedor
- docker exec -it negocio_backend alembic revision --autogenerate -m "Negocios" -> migracion de una tabla
- docker exec -it negocio_backend alembic upgrade head -> migracion de todas las tablas
- docker exec -it localstack awslocal sqs list -queues -> lista las colas de sqs aws que existen para correo
- docker exec -it localstack awslocal sqs create-queue --queue-name envio-correo -> creación de cola para correo
- docker compose logs -f backend -> ver logs de contenedores

## Comandos de LocalStack
- awslocal s3 ls -> lista los buckets del s3
- awslocal s3 mb s3://negocio -> crea bucket
- Listar recursivamente (todos los archivos y subcarpetas) -> docker exec -it negocio_localstack awslocal s3 ls s3://negocio/ --recursive
- borrar bucket -> docker exec -it localstack awslocal s3 rb s3://negocio --force

# Instalacion del proyecto

## Instalación Desde GitHub

1. Clonar el repositorio
2. Crear un archivo .env con las variables de entorno a partir de .env.example
3. Levantar los contenedores con docker compose: docker compose up -d --build
4. Aplicar migraciones de alembic: docker exec -it negocio_backend alembic upgrade head
5. Crear el bucket S3 en localstack: docker exec -it local_localstack awslocal s3 mb s3://negocio
6. Verificar bucket: docker compose exec localstack awslocal s3 ls
7. Probar api: http://localhost:8000

