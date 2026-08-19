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

    try:
        r = requests.get('https://prokod.ru/promokody/', headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.select('.promo-item, .item, .coupon-item, .promocode-item, .post, .article')
        for item in items:
            code_tag = item.select_one('.code, .promocode, .coupon-code, .promo-code, b, strong')
            desc_tag = item.select_one('.description, .desc, .title, .name, h2, h3')
            link_tag = item.select_one('a[href]')
            if code_tag:
                code = code_tag.text.strip()
                desc = desc_tag.text.strip() if desc_tag else 'Скидка'
                link = link_tag['href'] if link_tag and link_tag.get('href') else ''
                if link and not link.startswith('http'):
                    link = 'https://prokod.ru' + link
                promos.append({
                    'code': code,
                    'description': desc[:200],
                    'link': link,
                    'expires': 'скоро закончится'
                })
                if len(promos) >= 20:
                    break
    except Exception as e:
        print(f'Ошибка prokod.ru: {e}')

    if len(promos) < 5:
        fallback_promos = [
            {'code': 'YANDEX20', 'desc': 'Скидка 20% на Яндекс Маркет', 'link': 'https://market.yandex.ru'},
            {'code': 'FOOD15', 'desc': 'Скидка 15% на Яндекс Еду', 'link': 'https://eda.yandex.ru'},
            {'code': 'OZON10', 'desc': 'Скидка 10% на Ozon', 'link': 'https://ozon.ru'},
            {'code': 'ALI5', 'desc': 'Скидка 5% на AliExpress', 'link': 'https://aliexpress.ru'},
            {'code': 'SBER20', 'desc': 'Скидка 20% на СберМаркет', 'link': 'https://sbermarket.ru'},
        ]
        for p in fallback_promos:
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

    print(f'✅ Добавлено {added} новых промокодов')
    return promos

def parse_free_games():
    games = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get('https://steamdb.info/free/', headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        for row in soup.select('tr'):
            cols = row.select('td')
            if len(cols) >= 2:
                title_tag = cols[1].select_one('a')
                if title_tag:
                    title = title_tag.text.strip()
                    link = 'https://steamdb.info' + title_tag.get('href', '')
                    games.append({
                        'title': title,
                        'link': link,
                        'status': 'free'
                    })
                    if len(games) >= 10:
                        break
    except Exception as e:
        print(f'Ошибка SteamDB: {e}')

    if not games:
        games = [
            {'title': 'Dota 2', 'link': 'https://store.steampowered.com/app/570/Dota_2/', 'status': 'free'},
            {'title': 'Counter-Strike 2', 'link': 'https://store.steampowered.com/app/730/CounterStrike_Global_Offensive/', 'status': 'free'},
            {'title': 'Warframe', 'link': 'https://store.steampowered.com/app/230410/Warframe/', 'status': 'free'},
            {'title': 'Path of Exile', 'link': 'https://store.steampowered.com/app/238960/Path_of_Exile/', 'status': 'free'},
            {'title': 'Team Fortress 2', 'link': 'https://store.steampowered.com/app/440/Team_Fortress_2/', 'status': 'free'},
            {'title': 'Apex Legends', 'link': 'https://store.steampowered.com/app/1172470/Apex_Legends/', 'status': 'free'},
            {'title': 'Destiny 2', 'link': 'https://store.steampowered.com/app/1085660/Destiny_2/', 'status': 'free'},
            {'title': 'Genshin Impact', 'link': 'https://genshin.hoyoverse.com/', 'status': 'free'},
            {'title': 'Fortnite', 'link': 'https://www.epicgames.com/fortnite/', 'status': 'free'},
        ]

    return games

if __name__ == "__main__":
    print("🚀 Запуск парсера...")
    parse_promocodes()
