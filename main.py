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
    CarouselColumn, CarouselTemplate, PostbackAction, TextMessage, TemplateSendMessage, URIAction
)
from aiolinebot import AioLineBotApi

from db import recipes

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
            columns = [
                CarouselColumn(
                    title=recipe.name,
                    text='、'.join(recipe.tags),
                    actions=[
                        URIAction(label='レシピサイトへ', uri=recipe.url),
                        PostbackAction(label='ping', data=f'id={recipe.id}')
                    ])
             for recipe in recipes]

            carousel_template = CarouselTemplate(columns=columns)
            template_message = TemplateSendMessage(alt_text='listed recipes', template=carousel_template)

            line_bot_api.reply_message(event.reply_token, template_message)
        else:
            await no_match_text(event.reply_token)

def no_match_text(reply_token: str):
    line_api.reply_message_async(
        reply_token,
        TextMessage(text='もう一度お願いします！')
    )
