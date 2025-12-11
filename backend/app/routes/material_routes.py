from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialResponse, MaterialUpdate
from app.utils.jwt import get_current_user
from app.config import settings

router = APIRouter(prefix="/materials", tags=["Materials"])

# Создаем директорию для материалов, если она не существует
MATERIALS_DIR = Path("static/materials")
MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=List[MaterialResponse])
def get_materials(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    materials = db.query(Material).offset(skip).limit(limit).all()
    return materials

@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    return material

@router.post("/upload/", response_model=MaterialResponse)
async def upload_material(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию и роль
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут загружать материалы")
    
    # Проверяем тип файла
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Поддерживается только PDF формат")
    
    # Генерируем уникальное имя файла
    file_name = f"{current_user.user_id}_{file.filename}"
    file_path = MATERIALS_DIR / file_name
    
    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    
    # Создаем запись в БД
    db_material = Material(
        file_path=f"/static/materials/{file_name}"
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    print(f"Материал загружен: ID={db_material.material_id}, File={file_name}")
    
    return db_material

@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут обновлять материалы")
    
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    # Обновляем данные
    if material_data.file_path is not None:
        material.file_path = material_data.file_path
    
    db.commit()
    db.refresh(material)
    
    print(f"Материал обновлен: ID={material.material_id}")
    return material

@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут удалять материалы")
    
    # Находим материал
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    # Удаляем файл с диска, если он существует
    file_path = material.file_path.lstrip('/')
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Файл удален с диска: {file_path}")
        except Exception as e:
            print(f"Не удалось удалить файл: {e}")
    
    # Логируем перед удалением
    print(f"🗑️ Удаление материала: ID={material.material_id}, File={material.file_path}")
    
    # Удаляем материал из БД
    db.delete(material)
    db.commit()
    
    return {"message": "Материал успешно удален", "material_id": material_id}

@router.get("/search/", response_model=List[MaterialResponse])
def search_materials(
    filename: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    query = db.query(Material)
    
    if filename:
        query = query.filter(Material.file_path.ilike(f"%{filename}%"))
    
    materials = query.order_by(Material.material_id).all()
    return materials