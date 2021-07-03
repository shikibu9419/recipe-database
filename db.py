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

recipes = [
    Recipe(id: 'recipe1', name: 'レシピ1', note: 'hoge\nfuga', tags: ['tag1', 'tag2'], url: 'https://google.com'),
    Recipe(id: 'recipe2', name: 'レシピ2', note: 'hoge\nfuga', tags: ['tag3', 'tag4'], url: 'https://google.com'),
]
