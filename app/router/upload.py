from fastapi import APIRouter, status, Form, File, UploadFile, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Annotated
import uuid, os
import boto3

#router para subir archivos a localstack s3
router = APIRouter(prefix="/api/upload", tags=["subir archivo"])

#dotenv
from dotenv import load_dotenv
load_dotenv()

#cliente s3 apuntando a localstack
s3_client = boto3.client("s3", 
                  region_name=os.environ.get("AWS_REGION"), 
                  endpoint_url=os.environ.get("AWS_SECRET_ACCESS_URL"),
                  aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"))
#variables de entorno
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

@router.post("/")
async def upload(
    # Recibe el ID del negocio como un campo de formulario y el archivo como un archivo subido
    negocio_id: Annotated[int, Form()], 
    file: Annotated[UploadFile, File()]
): 
    # Validar el tipo de archivo
    extension = "0"
    if file.content_type=="image/jpeg":
        extension = "jpg"
    if file.content_type=="image/png":
        extension = "png"
    if file.content_type=="image/gif":
        extension = "gif"
    if extension=="0":
        return JSONResponse({"message": "Archivo no permitido"}, status_code=status.HTTP_400_BAD_REQUEST)    
    else:
        # Generar un nombre único para el archivo
        filename = f"{uuid.uuid4()}.{extension}"
        # Subir el archivo al bucket localstack
        try:
            s3_client.upload_fileobj(
                file.file,  
                S3_BUCKET_NAME, 
                f"archivos/{negocio_id}/{uuid.uuid4()}.{extension}", #ruta de destino
                ExtraArgs={
                    "ContentType": file.content_type #tipo de contenido
                }
            )
        except Exception as e:
            # Manejar errores de subida
            return JSONResponse({"message": f"Error al subir el archivo: {e}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Generar la URL del archivo subido
        file_url = "http://localhost:8000/{S3_BUCKET_NAME}/archivos/{filename}"
        # Confirmar que fast api recibio bien el ID del negocio y el archivo
        #retorno de la api
        return JSONResponse(
            {
                "message": "Archivo recibido",
                "negocio_id": negocio_id,
                "filename": filename,
                "content_type": file.content_type,
                "size": file.size,
                "file_url": file_url
            },
            status_code=status.HTTP_201_CREATED
        )

#eliminar archivo del bucket localstack
@router.delete("/delete/{negocio_id}/{filename}")
# funcion que recibe el ID del negocio y el nombre del archivo
async def delete(negocio_id: int, filename: str):
    #le paso el ID del negocio y el nombre del archivo
    key = f"archivos/{negocio_id}/{filename}"

    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
        )
    except Exception as e:
        return JSONResponse(
            {"message": f"Error al eliminar el archivo: {e}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        {"message": "Archivo eliminado", "key": key},
        status_code=status.HTTP_200_OK,
    )

#renderizacion dinamica de archivo con fileresponse y querystring
@router.get("/file")
async def file(id: str = Query(..., description="ID del negocio")):
    if not os.path.exists(os.path.join("uploads", id)):
        return JSONResponse({"message": "Archivo no encontrado"}, status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(os.path.join("uploads", id))