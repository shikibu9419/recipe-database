# -*- coding: utf-8 -*-
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException
from fastapi.responses import RedirectResponse
import os
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from aiolinebot import AioLineBotApi

line_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
parser = WebhookParser(channel_secret=os.environ.get('LINE_CHANNEL_SECRET'))

app = FastAPI()
REDIRECT_URL_ON_ROOT = 'https://google.com'

@app.get('/')
def index():
    return RedirectResponse(REDIRECT_URL_ON_ROOT)

@app.post('/callback')
async def callback(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers['X-Line-Signature']

    events = parser.parse(
        (await request.body()).decode("utf-8"),
        signature
    )

    background_tasks.add_task(handle_events, events=events)

    return 'ok'

async def handle_events(events):
    for event in events:
        try:
            await line_api.reply_message_async(
                event.reply_token,
                TextMessage(text=f"You said: {ev.message.text}"))
        except Exception:
            pass
