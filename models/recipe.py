from pydantic import BaseModel, Field
from typing import List, Optional

from models.base import ObjectId, PyObjectId
from utils import truncate

class Recipe(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    title: str
    url: str
    user_id: str
    is_temporary: bool
    tags: List[str] = []
    note: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    def stringify(self) -> str:
        return f"{self.title}\nタグ：{'、'.join(self.tags)}\n{self.note}"
