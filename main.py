import argparse
import logging
import time

import requests
import telegram
from environs import Env


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='/opt/Devman_bot_1/bot.log')
    logger = logging.getLogger(__name__)
    logger.info('INFO')
    logger.debug('DEBUG')
    logger.warning('WARNING')
    logger.error('ERROR')
    logger.critical('CRITICAL')

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
    while True:
        try:
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
            print('Превышено время ожидания ответа от сервера')
            continue
        except requests.exceptions.ConnectionError:
            print('Ошибка соединения с сервером')
            time.sleep(3)
            continue


if __name__ == '__main__':
    main()
