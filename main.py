# -*- coding: utf-8 -*-
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import RedirectResponse
import os
import re
import validators
from typing import List

from linebot import WebhookParser
from linebot.models import (
    CarouselColumn, CarouselTemplate, Event, PostbackAction, TextMessage, TemplateSendMessage, URIAction
)
from aiolinebot import AioLineBotApi

from recipes import recipes

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
        (await request.body()).decode('utf-8'),
        signature
    )

    background_tasks.add_task(handle_events, events=events)

    return 'ok'

async def handle_events(events: List[Event]):
    for event in events:
        message: str = event.message.text
        reply_token: str = event.reply_token
        user_id: str = event.source.user_id

        if re.match(r'レシピを登録', message):
            await line_api.reply_message_async(
                reply_token,
                TextMessage(text='URLを登録してね！')
            )
        elif re.match(r'.+で検索$', message):
            # TODO: from mongodb
            columns = [
                CarouselColumn(
                    title=recipe.name,
                    text='、'.join(recipe.tags),
                    actions=[
                        PostbackAction(label='詳細', data=f'id={recipe.id}'),
                        URIAction(label='レシピサイトへ', uri=recipe.url)
                    ])
             for recipe in recipes]

            carousel_template = CarouselTemplate(columns=columns)
            template_message = TemplateSendMessage(alt_text='listed recipes', template=carousel_template)

            await line_api.reply_message_async(reply_token, template_message)
        else:
            await no_match_text(reply_token)

def no_match_text(reply_token: str):
    return line_api.reply_message_async(
        reply_token,
        TextMessage(text='もう一度お願いします！')
    )
