
import os
import asyncio
import boto3
from botocore.exceptions import ClientError

# Importamos sendMail y modelos
from utils.utils import sendMail
from models.models import Usuario
from database import engine
from sqlmodel import Session, select

#funcion para iniciar el worker de la cola SQS
def iniciar_sqs_background_task(app):
    @app.on_event("startup")
    def worker_leer_sqs():
        async def tarea_de_fondo():
            print("Worker SQS iniciado: leyendo mensajes cada 5 segundos")
            while True:
                try:
                    # Configurar cliente SQS
                    if os.getenv('ENVIRONMENT') == "local":
                        sqs_client = boto3.client(
                            "sqs",
                            region_name=os.getenv("AWS_REGION", "us-west-2"),
                            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fake"),
                            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
                            endpoint_url=os.getenv("LOCALSTACK_ENDPOINT_URL")
                        )
                    else:
                        sqs_client = boto3.client(
                            "sqs",
                            region_name=os.getenv("AWS_REGION", "us-west-2"),
                            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fake"),
                            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake")
                        )
                    # Obtenemos la URL de la cola SQS
                    queue_url = os.getenv("SQS_ENVIO_CORREO")

                    # Leer mensajes de la cola
                    response = await asyncio.to_thread(
                        sqs_client.receive_message,
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=5,
                        WaitTimeSeconds=2,
                        MessageAttributeNames=["All"]
                    )
                    # Obtenemos los mensajes de la cola
                    messages = response.get("Messages", [])
                    if not messages:
                        # Esperamos 5 segundos antes de volver a leer
                        await asyncio.sleep(5)
                        continue
                    
                    # Iteramos sobre los mensajes
                    for message in messages:
                        mensaje_cuerpo = message["Body"]
                        atributos = message.get("MessageAttributes", {})
                        receipt_handle = message["ReceiptHandle"]
                        # Obtenemos el token y el nombre del usuario
                        print(f"Procesando mensaje con token: {atributos.get('Token', {}).get('StringValue', '')}")
                        print("Atributos:", atributos)

                        try:
                            # Extraer token desde los atributos del mensaje
                            token = atributos.get("Token", {}).get("StringValue", "")
                            nombre_usuario = atributos.get("Nombre", {}).get("StringValue", "Usuario")

                            # query de usuario por token
                            with Session(engine) as session:
                                usuario = session.exec(
                                    select(Usuario).where(Usuario.token == token, Usuario.estado_id == 1)
                                ).first()
                            # Validamos que exista el usuario
                            if not usuario:
                                print(f" No se encontró usuario con token '{token}' y estado_id = 1")
                                # borra el mensaje si no tiene sentido reintentarlo
                                await asyncio.to_thread(
                                    sqs_client.delete_message,
                                    QueueUrl=queue_url,
                                    ReceiptHandle=receipt_handle
                                )
                                print("Usuario no encontrado")
                                continue

                            #  Enviamos el correo usando sendMail()
                            html = f"""
                                <h2>Recuperación de contraseña</h2>
                                <p>Hola {usuario.nombre},</p>
                                <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
                                <a href="{mensaje_cuerpo}" target="_blank">Restablecer contraseña</a>
                                <br><br>
                                <small>Este enlace expira en 24 horas.</small>
                            """
                            sendMail(html=html, asunto="Restablece tu contraseña", para=usuario.correo)
                            #  Borramos el mensaje de la cola solo si todo fue bien
                            await asyncio.to_thread(
                                sqs_client.delete_message,
                                QueueUrl=queue_url,
                                ReceiptHandle=receipt_handle
                            )
                            print("Mensaje borrado de la cola")

                        except Exception as e:
                            print("Error al procesar mensaje:", e)

                    await asyncio.sleep(5)  # espera antes de volver a leer

                except ClientError as e:
                    print("Error en conexión SQS:", e)
                    await asyncio.sleep(10)

                except Exception as e:
                    print("Error general en worker:", e)
                    await asyncio.sleep(10)

        # Iniciar la tarea de fondo cuando arranque la app
        asyncio.create_task(tarea_de_fondo())

    return worker_leer_sqs