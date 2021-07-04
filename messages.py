from aiolinebot import AioLineBotApi
from linebot.models import (
    ButtonsTemplate, CarouselColumn, CarouselTemplate,
    PostbackAction, TextMessage, TemplateSendMessage, URIAction
)
import validators

from typing import List
import re
import os

from mongodb import Recipe, create_recipe, get_filtered_recipes, get_random_recipes, get_recipe, get_temporary_recipe, update_recipe
from utils import get_title_from_url, truncate

line_api = AioLineBotApi(channel_access_token=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))

async def handle_init(message: str, reply_token: str, user_id: str) -> str:
    if re.match(r'レシピを見る', message):
        recipes = get_random_recipes(user_id)

        if len(recipes) > 0:
            await line_api.reply_message_async(reply_token, get_recipes_carousel(recipes))
        else:
            await not_found_text(reply_token)
    elif re.match(r'.+で検索$', message):
        title = re.sub(r'で検索$', '', message)
        recipes = get_filtered_recipes(user_id, title)

        if len(recipes) > 0:
            await line_api.reply_message_async(reply_token, get_recipes_carousel(recipes, alt_text=f'で検索した結果'))
        else:
            await not_found_text(reply_token)
    elif re.match(r'レシピを登録', message):
        await line_api.reply_message_async(
            reply_token,
            TextMessage(text='URLを登録してね！')
        )

        return 'create/url'
    elif validators.url(message):
        return await handle_create_url(message, reply_token, user_id)
    elif re.match(r'id=[0-9a-f]+$', message):
        recipe = get_recipe(user_id, message.split('=')[-1])

        if recipe:
            await line_api.reply_message_async(
                reply_token,
                TextMessage(text=recipe.stringify())
            )
        else:
            await not_found_text(reply_token)
    else:
        await no_match_text(reply_token)

    return 'init'


async def handle_create_url(url: str, reply_token: str, user_id: str) -> str:
    if validators.url(url):
        title = get_title_from_url(url)
        recipe = create_recipe({ 'user_id': user_id, 'title': title, 'url': url, 'is_temporary': True })
        if not recipe:
            await not_found_text(reply_token)
            return 'init'
        update_recipe(recipe.id, { 'title': title, 'url': url })

        await line_api.reply_message_async(
            reply_token,
            [
                TextMessage(text=f'これが出てきたよ！\n{title}\n{url}'),
                TextMessage(text='メモを書いてね！')
            ])

        return 'create/note'
    else:
        await no_match_text(reply_token)

        return 'init'

async def handle_create_note(message: str, reply_token: str, user_id: str) -> str:
    recipe = get_temporary_recipe(user_id)
    if not recipe:
        await not_found_text(reply_token)
        return 'init'
    update_recipe(recipe.id, { 'note': message })

    await line_api.reply_message_async(
        reply_token,
        TextMessage(text='タグを改行区切りで登録してね！')
    )

    return 'create/tags'

async def handle_create_tags(message: str, reply_token: str, user_id: str) -> str:
    tags = message.split('\n')

    recipe = get_temporary_recipe(user_id)
    if not recipe:
        await not_found_text(reply_token)
        return 'init'
    update_recipe(recipe.id, { 'tags': tags })

    recipe = get_temporary_recipe(user_id)

    await line_api.reply_message_async(reply_token, [
        TextMessage(text=recipe.stringify()),
        get_confirmation_buttons('これでいい？', truncate(recipe.title, 30))
    ])

    return 'create/confirm'

async def handle_create_confirm(postback: str, reply_token: str, user_id: str) -> str:
    if postback == 'ok':
        recipe = get_temporary_recipe(user_id)
        if not recipe:
            await not_found_text(reply_token)
            return 'init'
        update_recipe(recipe.id, { 'is_temporary': False })

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

def get_confirmation_buttons(title: str, text: str = '') -> TemplateSendMessage:
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
            title=truncate(recipe.title, 37),
            text='、'.join(recipe.tags),
            actions=[
                PostbackAction(label='詳細', data=f'id={recipe.id}'),
                URIAction(label='レシピサイトへ', uri=recipe.url)
            ])
        for recipe in recipes]

    carousel_template = CarouselTemplate(columns=columns)
    return TemplateSendMessage(alt_text=alt_text, template=carousel_template)


def not_found_text(reply_token: str):
    return line_api.reply_message_async(
        reply_token,
        TextMessage(text='レシピが見つからなかったよ...')
    )


def no_match_text(reply_token: str):
    return line_api.reply_message_async(
        reply_token,
        TextMessage(text='すみません。よくわかりませんでした。')
    )
