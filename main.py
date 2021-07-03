# -*- coding: utf-8 -*-
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException
from fastapi.responses import RedirectResponse
import json

REDIRECT_URL_ON_ROOT = 'https://google.com'

app = FastAPI()

@app.get('/')
def index():
    return RedirectResponse(REDIRECT_URL_ON_ROOT)
