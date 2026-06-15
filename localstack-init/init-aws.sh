#!/bin/sh
# Se ejecuta automáticamente al arrancar LocalStack (ready.d hook)
# Crea los recursos AWS que necesita el backend en local

set -e

echo "Inicializando recursos en LocalStack"

awslocal s3 mb s3://negocio || true
awslocal sqs create-queue --queue-name envio-correo || true

echo "Recursos de LocalStack listos."
