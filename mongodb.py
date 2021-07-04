from pymongo import MongoClient
import os
from typing import List

from models.recipe import Recipe

client = MongoClient(os.environ.get('MONGODB_HOST'), 27017)
client.admin.authenticate(os.environ.get('MONGODB_USER'), os.environ.get('MONGODB_PASSWORD'))
db = client.test

def list_recipes() -> List[Recipe]:
    return [Recipe(**recipe) for recipe in db.recipes.find()]

def create_recipe(recipe: Recipe) -> Recipe:
    if hasattr(recipe, 'id'):
        delattr(recipe, 'id')

    rst = db.recipes.insert_one(recipe.dict(by_alias=True))
    recipe.id = rst.inserted_id

    return recipe
