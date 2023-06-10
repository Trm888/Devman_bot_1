import argparse
import logging
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from environs import Env

logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    env = Env()
    env.read_env()
    api_key = env.str('DEVMAN_API_KEY')
    bot_token = env.str('TELEGRAM_TOKEN')
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {api_key}'}
    params = {'timestamp': ''}
    chat_id = env.int('TELEGRAM_CHAT_ID')
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Укажите ваш id', type=int, default=chat_id)
    bot = telegram.Bot(token=bot_token)

    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler('bot.log', maxBytes=200000, backupCount=2)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    telegram_handler = TelegramLogsHandler(bot, chat_id)
    telegram_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(telegram_handler)

    logger.info('Бот запущен')

    while True:
        try:
            time.sleep(5)
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            review_information = response.json()
            if review_information['status'] == 'found':
                params['timestamp'] = review_information['last_attempt_timestamp']
                if review_information['new_attempts'][0]['is_negative']:
                    bot.send_message(
                        text=f'У вас проверили работу <b>"{review_information["new_attempts"][0]["lesson_title"]}"</b>\n'
                             f'К сожалению в работе нашлись ошибки. Ссылка на работу'
                             f' {review_information["new_attempts"][0]["lesson_url"]}',
                        chat_id=chat_id, parse_mode=telegram.ParseMode.HTML)
                else:
                    bot.send_message(
                        text=f'У вас проверили работу <b>"{review_information["new_attempts"][0]["lesson_title"]}"</b>\n'
                             f'Работа принята! Ссылка на работу {review_information["new_attempts"][0]["lesson_url"]}',
                        chat_id=chat_id, parse_mode=telegram.ParseMode.HTML)

        except requests.exceptions.ReadTimeout:
            logger.info('Превышено время ожидания ответа от сервера')
            continue
        except requests.exceptions.ConnectionError:
            logger.info('Ошибка соединения с сервером')
            time.sleep(5)
            continue
        except Exception as error:
            logger.exception(f'Бот упал с ошибкой: {error}')
            continue


if __name__ == '__main__':
    main()
