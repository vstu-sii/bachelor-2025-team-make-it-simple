from pydantic import BaseModel
from typing import Optional

class MaterialBase(BaseModel):
    file_path: str

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    file_path: Optional[str] = None

class MaterialResponse(MaterialBase):
    material_id: int
    
    class Config:
        from_attributes = True