# -*- coding: utf-8 -*-
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import os
import re
import validators

from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from aiolinebot import AioLineBotApi

import logutil as logger

line_api = AioLineBotApi(channel_access_token=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
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
        message = event.message.text
        user_id = event.source.user_id

        if re.match(r'レシピを登録', message):
            await line_api.reply_message(
                event.reply_token,
                TextMessage(text='URLを登録してね！')
            )
        elif re.match(r'.+で検索$', message):
            # return searched recipes as carousel
        elif validators.url(message.strip()):
            # select yes or no
        else:
            await no_match_text(event.reply_token)

def second():
    await line_api.reply_message(
        event.reply_token,
        TextMessage(text='メモを登録してね！')
    )

def third():
    await line_api.reply_message(
        event.reply_token,
        TextMessage(text='タグをカンマ区切りで登録してね！')
    )

def confirm():
    # select yes or no

def no_match_text(reply_token: str):
    line_api.reply_message_async(
        reply_token,
        TextMessage(text='もう一度お願いします！')
    )
