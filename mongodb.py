from bson import ObjectId
from pymongo import MongoClient
import os
from typing import Any, Dict, List, Union

from models.recipe import Recipe

MAX_RECIPES_COUNT = 7

client = MongoClient(os.environ.get('MONGODB_HOST'), 27017)
client.admin.authenticate(os.environ.get('MONGODB_USER'), os.environ.get('MONGODB_PASSWORD'))
db = client.test

def get_recipe(user_id: str, oid: str) -> Union[Recipe, None]:
    recipe = db.recipes.find_one({ 'user_id': user_id, '_id': ObjectId(oid), 'is_temporary': False })

    if recipe:
        return Recipe(**recipe)
    else:
        return None

def get_random_recipes(user_id: str) -> List[Recipe]:
    return [Recipe(**recipe) for recipe in db.recipes.aggregate([{ '$match': { 'user_id': user_id, 'is_temporary': False } }, { '$sample': { 'size': MAX_RECIPES_COUNT } }])]

def get_filtered_recipes(user_id: str, name: str) -> List[Recipe]:
    return [Recipe(**recipe) for recipe in db.recipes.find({ 'user_id': user_id, 'name': { '$regex': name }, 'is_temporary': False }, limit = MAX_RECIPES_COUNT)]

def get_temporary_recipe(user_id: str) -> Union[Recipe, None]:
    recipe = db.recipes.find_one({ 'user_id': user_id, 'is_temporary': True })

    if recipe:
        return Recipe(**recipe)
    else:
        return None

def update_recipe(oid: Union[ObjectId, str], data: Dict[str, Any]):
    if isinstance(oid, str):
        oid = ObjectId(oid)

    db.recipes.update_one({ '_id': ObjectId(oid) }, { '$set': data })

def create_recipe(data: Dict[str, Any]) -> Recipe:
    if hasattr(data, 'id'):
        delattr(data, 'id')

    rst = db.recipes.insert_one(data)

    return Recipe(**data, **{ 'id': rst.inserted_id })
