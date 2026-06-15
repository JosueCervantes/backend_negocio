
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse

# Esquema de seguridad
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Descripción general de la API
DESCRIPTION = """
API Rest de testing para proyecto de josue
"""

# Información de contacto
CONTACT_INFO = {
    "name": "negocio.com",
    "url": "https://www.negocio-prueba.com", 
    "email": "contacto@negocio-prueba.com"
}

# Licencia
LICENSE_INFO = {
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html" 
}

# Términos de servicio
TERMS_OF_SERVICE = "https://www.negocio-prueba.com"

# Etiquetas de OpenAPI (tags)
OPENAPI_TAGS = [
    {"name": "Ejemplo", "description": "Ejemplo de API Rest"},
    {"name": "Subir archivos", "description": "Ejemplo upload de archivos, locales y S3"},
    {"name": "Estado", "description": "API Rest Estado"},
    {"name": "Categorías", "description": "API Rest Categorías"},
    {"name": "Negocios", "description": "API Rest Negocios"},
    {"name": "Negocios logo", "description": "Administrar logos de negocios"},
    {"name":"Negocio por Usuario",  "description":"Ver negocio por usuario"},
    {"name": "Platos Categorías", "description": "API Rest Platos Categorías"},
    {"name": "Platos", "description": "API Rest Platos"},
    {"name": "Carta", "description": "API Rest Carta por slug"},
    {"name": "Usuario", "description": "API Rest Usuarios"},
    {"name": "Login", "description": "API Rest Login"},
    {"name": "Perfil", "description": "API Rest Perfil"},
    {"name": "Recovery", "description": "API Rest Restablecer contraseña"}
]

# Función para generar el esquema OpenAPI personalizado
def custom_openapi(app):
    def generate_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="API Rest con FastAPI",
            version="0.0.1",
            description=DESCRIPTION,
            routes=app.routes,
            tags=OPENAPI_TAGS
        )

        # Añade info adicional
        openapi_schema["info"]["termsOfService"] = TERMS_OF_SERVICE
        openapi_schema["info"]["license"] = LICENSE_INFO
        openapi_schema["info"]["contact"] = CONTACT_INFO

        # Componentes de seguridad
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/auth/login",
                        "scopes": {}
                    }
                }
            }
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return generate_openapi


