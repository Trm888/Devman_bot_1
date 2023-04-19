import argparse
from pprint import pprint

import requests
import telegram
from environs import Env


def main():
    env = Env()
    env.read_env()
    api_key = env.str('API_KEY')
    bot_token = env.str('BOT_TOKEN')
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {api_key}'}
    params = {'timestamp': ''}
    chat_id = env.int('YOUR_ID')
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Укажите ваш id', type=int, default=chat_id)
    bot = telegram.Bot(token=bot_token)
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            serializable_response = response.json()
            params['timestamp'] = serializable_response['last_attempt_timestamp']
            pprint(response.json())

            if serializable_response['new_attempts'][0]['is_negative']:
                bot.send_message(
                    text=f'У вас проверили работу <b>"{serializable_response["new_attempts"][0]["lesson_title"]}"</b>\n'
                         f'К сожалению в работе нашлись ошибки. Ссылка на работу'
                         f' {serializable_response["new_attempts"][0]["lesson_url"]}',
                    chat_id=chat_id, parse_mode=telegram.ParseMode.HTML)
            else:
                bot.send_message(
                    text=f'У вас проверили работу <b>"{serializable_response["new_attempts"][0]["lesson_title"]}"</b>\n'
                         f'Работа принята! Ссылка на работу {serializable_response["new_attempts"][0]["lesson_url"]}',
                    chat_id=chat_id, parse_mode=telegram.ParseMode.HTML)
        except requests.exceptions.ReadTimeout:
            print('Превышено время ожидания ответа от сервера')
            continue
        except requests.exceptions.ConnectionError:
            print('Ошибка соединения с сервером')
            continue


if __name__ == '__main__':
    main()
