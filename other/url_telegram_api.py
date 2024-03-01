import requests

telegram_token = ':token:'
my_telegram_id = 'chat_id'

telegram_url = "https://api.telegram.org/bot" + telegram_token + '/sendMessage' + '?chat_id=' + my_telegram_id + '&text='


def send_msg(text):
    url = telegram_url + text
    result = requests.get(url)
    print(result.json())


def test_get_updates_from_bot():
    url = "https://api.telegram.org/bot" + telegram_token + '/getUpdates'
    result = requests.get(url)
    print(result.json())


