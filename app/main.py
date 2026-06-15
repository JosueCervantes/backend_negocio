from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from fastapi.middleware.cors import CORSMiddleware

#dotenv
from dotenv import load_dotenv
load_dotenv()

# Importa la tarea de SQS
from worker.sqs_worker import iniciar_sqs_background_task

app = FastAPI(docs_url=None)

# Inicia la tarea background
iniciar_sqs_background_task(app)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los encabezados
)

# Importamos la configuración de OpenAPI
from fastapi.openapi.docs import get_swagger_ui_html
from swagger.openapi import custom_openapi

#swagger
# Aplicamos la configuración de OpenAPI
app.openapi = custom_openapi(app)
# Middleware para servir la documentación de Swagger
@app.get("/documentacion", include_in_schema=False)
async def swagger_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="FastAPI - Documentación")

#Routes
from app.router.routes import router
from app.router.upload import router as upload_router
from app.router.estado import router as estado_router
from app.router.categoria import router as categoria_router
from app.router.negocio import router as negocio_router
from app.router.logo import router as logo_router
from app.router.negocio_by_user import router as negocio_by_user_router
from app.router.plato_categoria import router as plato_categoria_router
from app.router.platos import router as platos_router
from app.router.carta import router as carta
from app.router.perfil import router as perfil_router
from app.router.usuario import router as usuario_router
from app.router.recovery import router as recovery_router

app.include_router(estado_router)
app.include_router(router)
app.include_router(upload_router)
app.include_router(categoria_router)
app.include_router(negocio_router)
app.include_router(negocio_by_user_router)
app.include_router(logo_router)
app.include_router(plato_categoria_router)
app.include_router(platos_router)
app.include_router(carta)
app.include_router(perfil_router)
app.include_router(usuario_router)
app.include_router(recovery_router)

@app.get("/")
def root():
    return JSONResponse({"message": "API funcionando"})

@app.exception_handler(404)
def not_found(request, exc):
    return JSONResponse({"message": "Not found"}, status_code=404)