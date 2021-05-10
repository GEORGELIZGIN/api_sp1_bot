import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG
)


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    STATUSES = {
        'approved': (
            'Ревьюеру всё понравилось, '
            'можно приступать к следующему уроку.'),
        'rejected': (
            'К сожалению в работе нашлись ошибки.'),
    }
    status = homework.get('status')
    verdict = STATUSES.get(status, 'Неизвестный статус работы')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {'Authorization': 'OAuth ' + PRAKTIKUM_TOKEN}
    params = {'from_date': current_timestamp}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(
            url,
            params=params,
            headers=headers
        )
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logging.error(e, exc_info=True)


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    logging.debug('Бот успешно запущен')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot)
                logging.info('Сообщение успешно отправлено')
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            logging.error(e, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
