from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional

client = MongoClient('localhost', 27017)
db = client.test

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')

class Recipe(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    name: str
    note: str
    tags: List[str]
    url: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

def list_recipes() -> List[Recipe]:
    return [Recipe(**recipe) for recipe in db.recipes.find()]

def create_recipe(recipe: Recipe) -> Recipe:
    if hasattr(recipe, 'id'):
        delattr(recipe, 'id')

    rst = db.recipes.insert_one(recipe.dict(by_alias=True))
    recipe.id = rst.inserted_id

    return recipe
