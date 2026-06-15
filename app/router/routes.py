from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.dto.dtos import UserCreate

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/")
async def get():
    return JSONResponse({"message": "Metodo GET"}, status_code=status.HTTP_200_OK)

@router.get("/{id}")
async def show(id: str):
    return JSONResponse({"message": f"Metodo GET {id}"}, status_code=status.HTTP_200_OK)

@router.post("/")
async def post():
    return JSONResponse({"message": "Metodo POST"}, status_code=status.HTTP_200_OK)

@router.post("/create")
async def create(user: UserCreate):
    return JSONResponse({"message": f"Usuario {user.name} creado"}, status_code=status.HTTP_201_CREATED)

@router.put("/{id}")
async def put(id: str):
    return JSONResponse({"message": f"Metodo PUT {id}"}, status_code=status.HTTP_200_OK)

@router.delete("/{id}")
async def delete(id: str):
    return JSONResponse({"message": f"Metodo DELETE {id}"}, status_code=status.HTTP_200_OK)
