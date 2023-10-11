import argparse
from enum import Enum
from typing import List

import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

LOCATION = 22
URL = "https://www.kstw.de/speiseplan/?l=22"


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
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    dishes = []
    location = soup.find("div", {"class": "tx-epwerkmenu-menu-location-wrapper", "data-location": location})
    for menu_tile in location.find_all("div", {"class": "col-12 col-lg-6 mb-4 menue-tile"}):
        plate = menu_tile.find("div", {"class": "plate"})
        category = menu_tile['data-category']
        dishes.append(Dish(
            name=f'{DishStyle[category].get_icon()} {menu_tile.find("div", {"class": "tx-epwerkmenu-menu-meal-title"}).get_text(strip=True)}',
            description=menu_tile.find("div", {"class": "tx-epwerkmenu-menu-meal-description"}).get_text(strip=True),
            image_url=plate.find("img")["src"] if plate else None,
            color=DishStyle[category].get_color()
        ))
    return list(set(dishes))


def send_webhook(webhook_url):
    dishes = fetch_dishes(url=URL, location=LOCATION)
    if not dishes:
        return
    embeds = []
    for dish in dishes:
        embed = DiscordEmbed(title=dish.name, description=dish.description, color=dish.color)
        if dish.image_url:
            embed.set_image(dish.image_url)
        embeds.append(embed)
    webhook = DiscordWebhook(url=webhook_url)
    for embed in embeds:
        webhook.add_embed(embed)
    res = webhook.execute()
    res.raise_for_status()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gordon Schlemmsay Canteen Bot")
    parser.add_argument("--webhook", type=str, required=True, help="Sets the webhook path")
    args = parser.parse_args()
    send_webhook(args.webhook)
