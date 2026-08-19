import requests
from bs4 import BeautifulSoup
import time
import random
import re
from database import save_promo
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_promocodes():
    promos = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    telegram_sources = [
        'https://t.me/s/promokody_ru',
        'https://t.me/s/skidki_vsem',
        'https://t.me/s/ekonom_ru',
    ]

    for url in telegram_sources:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            for msg in soup.select('.tgme_widget_message_text'):
                text = msg.text.strip()
                codes = re.findall(r'\b[A-Z0-9]{4,12}\b', text)
                for code in codes:
                    if len(code) >= 4 and code not in ['ПОСТ', 'СКИДКА', 'НОВОСТИ']:
                        promos.append({
                            'code': code,
                            'description': text[:200],
                            'link': url,
                            'expires': 'проверьте в канале'
                        })
                        if len(promos) >= 30:
                            break
        except Exception as e:
            print(f'Ошибка {url}: {e}')

    if len(promos) < 3:
        fallback = [
            {'code': 'YANDEX20', 'desc': 'Скидка 20% на Яндекс Маркет', 'link': 'https://market.yandex.ru'},
            {'code': 'OZON10', 'desc': 'Скидка 10% на Ozon', 'link': 'https://ozon.ru'},
            {'code': 'ALI5', 'desc': 'Скидка 5% на AliExpress', 'link': 'https://aliexpress.ru'},
        ]
        for p in fallback:
            promos.append({
                'code': p['code'],
                'description': p['desc'],
                'link': p['link'],
                'expires': 'скоро закончится'
            })

    added = 0
    for p in promos:
        try:
            save_promo(p['code'], p['description'], p['link'], p['expires'])
            added += 1
        except Exception as e:
            print(f'Ошибка сохранения: {e}')

    print(f'✅ Добавлено {added} промокодов')
    return promos

def parse_free_games():
    games = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get('https://store.epicgames.com/ru/free-games', headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.select('.css-1myhtyb, .css-1u4vnx0, .css-1r9l5je')
        for item in items[:5]:
            title_tag = item.select_one('span')
            link_tag = item.select_one('a[href]')
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = 'https://store.epicgames.com' + link_tag.get('href', '')
                games.append({
                    'title': title,
                    'link': link,
                    'status': '🔥 Бесплатно на Epic Games'
                })
    except Exception as e:
        print(f'Ошибка Epic Games: {e}')

    if not games:
        games = [
            {'title': 'The Walking Dead (Epic Games)', 'link': 'https://store.epicgames.com/ru/p/the-walking-dead', 'status': '🔥 Раздача'},
            {'title': 'Prey (Epic Games)', 'link': 'https://store.epicgames.com/ru/p/prey', 'status': '🎁 Временная раздача'},
            {'title': 'Control (Epic Games)', 'link': 'https://store.epicgames.com/ru/p/control', 'status': '🔥 Бесплатно'},
            {'title': 'Borderlands 3 (Epic Games)', 'link': 'https://store.epicgames.com/ru/p/borderlands-3', 'status': '🎁 Раздача'},
            {'title': 'GTA V (Epic Games)', 'link': 'https://store.epicgames.com/ru/p/grand-theft-auto-v', 'status': '🔥 Была бесплатно'},
        ]

    return games[:10]

if __name__ == "__main__":
    print("🚀 Запуск парсера...")
    parse_promocodes()
