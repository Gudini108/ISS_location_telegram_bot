"""ISS location telegram bot."""

import os
import requests
import logging
from logging.handlers import RotatingFileHandler

from geopy.geocoders import Nominatim
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from dotenv import load_dotenv
from exceptions import ApiIsNotReachable, CoordsNotAwailable

load_dotenv()

ENDPOINT = 'http://api.open-notify.org/iss-now.json'

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
IMG_BB = os.getenv('IMG_BB')

geolocator = Nominatim(user_agent="geoapiExercises")

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'info.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='utf-8'
)
log.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
)

handler.setFormatter(formatter)


def get_api_response():
    """Запрос API МКС."""
    try:
        response = requests.get(ENDPOINT)
        response.raise_for_status()
    except Exception as error:
        log.error('Не можем достучаться до API MKC.')
        raise ApiIsNotReachable(f'API недоступен: "{error}"')
    return response.json()


def get_ISS_coordinates(api_response):
    """Get ISS position with json data."""
    try:
        ISS_coordinates = api_response.get('iss_position')
        ISS_latitude = ISS_coordinates.get('latitude')
        ISS_longitude = ISS_coordinates.get('longitude')
    except Exception as error:
        log.error(f'Не получается получить координаты МКС: "{error}"')
        raise CoordsNotAwailable('Не можем получить координаты МКС')

    return ISS_latitude, ISS_longitude


def get_location(ISS_latitude, ISS_longitude, user_language):
    """Get country and city with ISS coordinates."""
    location = geolocator.reverse(
        ISS_latitude+","+ISS_longitude,
        language=user_language if user_language else 'en'
    )
    if location:
        return location.address
    return 'Ph’nglui mglw’nafh Cthulhu R’lyeh wgah’nagl fhtagn'


def main(update, context):
    """Bot logic."""
    chat = update.effective_chat
    user = update.effective_user
    lang_code = user['language_code']

    try:
        response = get_api_response()
        ltd, lng = get_ISS_coordinates(response)
        address = get_location(ltd, lng, lang_code)

        message = (
            f"Right now ISS's coordinates are\n"
            f"{ltd}° N and {lng}° E. \n"
            f'{address}'
        )

        context.bot.send_message(
            chat.id,
            message,
            )
        context.bot.send_location(
            chat.id,
            latitude=ltd,
            longitude=lng
        )

    except Exception as error:
        log.error(error)


def start(update, context):
    """Welcome message when bot starts."""
    keyboard = [[KeyboardButton('So, where is ISS right now?')]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
    update.message.reply_text(
        'ISS coordinates tracker welcomes you!',
        reply_markup=reply_markup
    )


updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(
    Filters.regex(r'^So, where is ISS right now\?$'), main))

updater.start_polling()
