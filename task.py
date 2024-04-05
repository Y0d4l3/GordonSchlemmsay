import argparse
import datetime
from enum import Enum
from typing import List

import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

LOCATION = 27
BASE_URL = "https://sw-koeln.maxmanager.xyz/"
MENU_URL = f"{BASE_URL}index.php"


class DishStyle(Enum):
    HEIMSPIEL = ("C92423", "🍖")
    QUERBEET = ("429E12", "🌿")
    STREETFOOD = ("E36B0D", "🌭")
    WORLDWIDE = ("0A82A8", "🗺️")
    MEISTERWERK = ("7D7869", "👑")

    def get_color(self):
        return self.value[0]

    def get_icon(self):
        return self.value[1]


class Dish:
    def __init__(self, name: str, description: str, image_url: str, color: str):
        self.name = name
        self.description = description
        self.image_url = image_url
        self.color = color

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def fetch_dishes(url, location) -> List[Dish]:
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    today = datetime.date.today().strftime("%Y-%m-%d")
    menu = soup.find("div", {"class": "container-fluid einrichtungsblock p-0 hide", "data-einrichtung": location})

    dishes = []
    for dish_type in DishStyle.__members__:
        for dish in menu.find_all("div", {"data-menuelinie": dish_type, "data-essensdatum": today}):
            new_dish = Dish(
                name=f"{DishStyle[dish_type].get_icon()} {dish.find('div', {'class': 'essenstext ubuntu-bold'}).get_text(strip=True)}",
                description=dish.find("div", {"class": "beschreibungtext"}).get_text(strip=True),
                image_url= f"{BASE_URL}{dish.find_all('img')[1]['src']}",
                color=DishStyle[dish_type].get_color(),
            )
            dishes.append(new_dish)

    return list(set(dishes))


def send_webhook(webhook_url):
    webhook = DiscordWebhook(url=webhook_url)

    try:
        embeds = []
        for dish in fetch_dishes(url=MENU_URL, location=LOCATION):
            embed = DiscordEmbed(title=dish.name, description=dish.description, color=dish.color)
            embed.set_image(dish.image_url) if dish.image_url else None
            embeds.append(embed)

        for embed in embeds:
            webhook.add_embed(embed)

    except Exception as e:
        print(e)
        webhook.content = "Heude jibbet noeschts :("

    res = webhook.execute()
    res.raise_for_status()
    print(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gordon Schlemmsay Canteen Bot")
    parser.add_argument("--webhook", type=str, required=True, help="Sets the webhook path")
    args = parser.parse_args()
    send_webhook(args.webhook)
