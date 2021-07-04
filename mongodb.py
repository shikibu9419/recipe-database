from bson import ObjectId
from pymongo import MongoClient
import os
from typing import List

from models.recipe import Recipe

MAX_RECIPES_COUNT = 7

client = MongoClient(os.environ.get('MONGODB_HOST'), 27017)
client.admin.authenticate(os.environ.get('MONGODB_USER'), os.environ.get('MONGODB_PASSWORD'))
db = client.test

def get_recipe(oid: str) -> Recipe:
    return Recipe(**db.recipes.find_one({'_id':ObjectId(oid)}))

def get_random_recipes() -> List[Recipe]:
    return [Recipe(**recipe) for recipe in db.recipes.aggregate([{ '$sample': { 'size': MAX_RECIPES_COUNT } }])]

def get_filtered_recipes(name: str) -> List[Recipe]:
    return [Recipe(**recipe) for recipe in db.recipes.find({ 'name': { '$regex': name } }, limit = MAX_RECIPES_COUNT)]

def create_recipe(recipe: Recipe) -> Recipe:
    if hasattr(recipe, 'id'):
        delattr(recipe, 'id')

    rst = db.recipes.insert_one(recipe.dict(by_alias=True))
    recipe.id = rst.inserted_id

    return recipe
