from aiolinebot import AioLineBotApi
from linebot.models import (
    ButtonsTemplate, CarouselColumn, CarouselTemplate,
    PostbackAction, TextMessage, TemplateSendMessage, URIAction
)
import validators

from typing import List
import re
import os

from mongodb import Recipe, list_recipes

line_api = AioLineBotApi(channel_access_token=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))

async def handle_init(message: str, reply_token: str) -> str:
    if re.match(r'レシピを登録', message):
        await line_api.reply_message_async(
            reply_token,
            TextMessage(text='URLを登録してね！')
        )

        return 'create/url'
    elif validators.url(message):
        await get_recipe_from_site(message, reply_token)

        return 'create/note'
    elif re.match(r'レシピを見る', message):
        recipes = list_recipes()

        if len(recipes) > 0:
            await line_api.reply_message_async(reply_token, get_recipes_carousel(recipes))
        else:
            await line_api.reply_message_async(reply_token, TextMessage(text='レシピが見つからなかったよ...'))
    elif re.match(r'.+で検索$', message):
        recipes = list_recipes()

        if len(recipes) > 0:
            await line_api.reply_message_async(reply_token, get_recipes_carousel(recipes, alt_text=f'で検索した結果'))

            return 'select'
        else:
            await line_api.reply_message_async(reply_token, TextMessage(text='レシピが見つからなかったよ...'))
    elif re.match(r'id=[0-9a-f]+$', message):
        await get_recipe(message, reply_token)
    else:
        await no_match_text(reply_token)

    return 'init'


async def handle_create_url(message: str, reply_token: str) -> str:
    if validators.url(message):
        await get_recipe_from_site(message, reply_token)

        return 'create/note'
    else:
        await no_match_text(reply_token)

        return 'init'

async def handle_create_note(message: str, reply_token: str) -> str:
    await line_api.reply_message_async(
        reply_token,
        TextMessage(text='タグを改行区切りで登録してね！')
    )

    return 'create/tags'

async def handle_create_tags(message: str, reply_token: str) -> str:
    tags = message.split('\n')

    title = 'レシピ名'
    note = 'メモ'
    url = 'メモ'
    text = f"{title}\n{'、'.join(tags)}\n{url}\n{note}"

    await line_api.reply_message_async(reply_token, get_confirmation_buttons('これでいい？', text))

    return 'create/confirm'

async def handle_create_confirm(postback: str, reply_token: str) -> str:
    if postback == 'ok':
        await line_api.reply_message_async(
            reply_token,
            TextMessage(text='レシピを登録したよ！')
        )
    else:
        await line_api.reply_message_async(
            reply_token,
            TextMessage(text='やっぱりやめたよ...')
        )

    return 'init'

async def get_recipe(recipe_id: str, reply_token: str):
    await line_api.reply_message_async(
        reply_token,
        TextMessage(text=recipe_id)
    )

async def get_recipe_from_site(url: str, reply_token: str) -> str:
    await line_api.reply_message_async(
        reply_token,
        [
            TextMessage(text='これが出てきたよ！'),
            TextMessage(text='メモを書いてね！')
        ])

    return 'create/note'

def get_confirmation_buttons(title: str, text: str) -> TemplateSendMessage:
    buttons_template = ButtonsTemplate(
        title=title,
        text=text,
        actions=[
            PostbackAction(label='OK', data='ok'),
            PostbackAction(label='NO', data='no'),
        ])

    return TemplateSendMessage(alt_text=title, template=buttons_template)

def get_recipes_carousel(recipes: List[Recipe], alt_text: str = 'レシピの一覧') -> TemplateSendMessage:
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
    return TemplateSendMessage(alt_text=alt_text, template=carousel_template)


def no_match_text(reply_token: str):
    return line_api.reply_message_async(
        reply_token,
        TextMessage(text='もう一度お願いします！')
    )
