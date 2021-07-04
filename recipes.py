from pydantic import BaseModel
from typing import List, Optional

class Recipe(BaseModel):
    id: str
    title: str
    note: str
    tags: List[str]
    url: Optional[str]

data = [
    {'id': 'recipe1', 'title': 'レシピ1', 'note': 'hoge\nfuga', 'tags': ['tag1', 'tag2'], 'url': 'https://google.com'},
    {'id': 'recipe2', 'title': 'レシピ2', 'note': 'hoge\nfuga', 'tags': ['tag3', 'tag4'], 'url': 'https://google.com'},
]
recipes = [Recipe(**d) for d in data]
