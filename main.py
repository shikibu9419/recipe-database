# -*- coding: utf-8 -*-
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import RedirectResponse
from linebot import WebhookParser
from linebot.models import Event, MessageEvent

from typing import List
import os

from linebot.models.events import PostbackEvent

from db.redis import r as redis
from messages import *

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
        (await request.body()).decode('utf-8'),
        signature
    )

    background_tasks.add_task(handle_events, events=events)

    return 'ok'

async def handle_events(events: List[Event]):
    for event in events:
        content = get_content_from_event(event)
        reply_token: str = event.reply_token
        user_id: str = event.source.user_id
        next_action: str = (redis.get(user_id) or b'init').decode()
        print(f'message from {user_id}')
        print(content, reply_token, next_action)

        if next_action == 'init':
            message = content.text if isinstance(event, MessageEvent) else content.data
            next_action = await handle_init(message, reply_token)
        elif next_action == 'create/url':
            next_action = await handle_create_url(content.text, reply_token)
        elif next_action == 'create/note':
            next_action = await handle_create_note(content.text, reply_token)
        elif next_action == 'create/tags':
            next_action = await handle_create_tags(content.text, reply_token)
        elif next_action == 'create/confirm':
            next_action = await handle_create_confirm(content.data, reply_token)
        else:
            await no_match_text(reply_token)

        redis.set(user_id, next_action)

def get_content_from_event(event: Event):
    if isinstance(event, MessageEvent):
        return event.message
    elif isinstance(event, PostbackEvent):
        return event.postback
