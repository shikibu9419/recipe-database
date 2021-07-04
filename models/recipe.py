from pydantic import BaseModel, Field
from typing import List, Optional

from models.base import ObjectId, PyObjectId

class Recipe(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    name: str
    note: str
    tags: List[str]
    url: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    def stringify(self) -> str:
        return f"{self.name}\n{self.url}\nタグ：{'、'.join(self.tags)}\n\n{self.note}"
