import argparse
import time

import requests
import telegram
from environs import Env


def main():
    env = Env()
    env.read_env()
    api_key = env.str('DEVMAN_API_KEY')
    bot_token = env.str('TELEGRAM_TOKEN')
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {api_key}'}
    params = {'timestamp': ''}
    chat_id = env.int('YOUR_TELEGRAM_ID')
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Укажите ваш id', type=int, default=chat_id)
    bot = telegram.Bot(token=bot_token)
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            decoded_response = response.json()
            if decoded_response['status'] == 'found':
                params['timestamp'] = decoded_response['last_attempt_timestamp']
            if decoded_response['new_attempts'][0]['is_negative']:
                bot.send_message(
                    text=f'У вас проверили работу <b>"{decoded_response["new_attempts"][0]["lesson_title"]}"</b>\n'
                         f'К сожалению в работе нашлись ошибки. Ссылка на работу'
                         f' {decoded_response["new_attempts"][0]["lesson_url"]}',
                    chat_id=chat_id, parse_mode=telegram.ParseMode.HTML)
            else:
                bot.send_message(
                    text=f'У вас проверили работу <b>"{decoded_response["new_attempts"][0]["lesson_title"]}"</b>\n'
                         f'Работа принята! Ссылка на работу {decoded_response["new_attempts"][0]["lesson_url"]}',
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
