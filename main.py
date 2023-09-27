import argparse
from typing import List

import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed


class Dish:
    def __init__(self, name: str, description: str, image_url: str):
        self.name = name
        self.description = description
        self.image_url = image_url

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def fetch_dishes() -> List[Dish]:
    url = "https://www.kstw.de/speiseplan?l=22"
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    dishes = []
    location = soup.find("div", {"class": "tx-epwerkmenu-menu-location-wrapper", "data-location": 22})
    for menu_tile in location.find_all("div", {"class": "col-12 col-lg-6 mb-4 menue-tile"}):
        plate = menu_tile.find("div", {"class": "plate"})
        dishes.append(Dish(
            name=menu_tile.find("div", {"class": "tx-epwerkmenu-menu-meal-title"}).get_text(strip=True),
            description=menu_tile.find("div", {"class": "tx-epwerkmenu-menu-meal-description"}).get_text(strip=True),
            image_url=plate.find("img")["src"]
        ))
    return list(set(dishes))


def send_webhook(webhook_url):
    dishes = fetch_dishes()
    if not dishes:
        return
    kinds = ["VEGAN", "VEGETARISCH"]
    embeds = []
    for dish in dishes:
        color = "429E12" if any([x in dish.name for x in kinds]) else "C92423"
        embed = DiscordEmbed(title=dish.name, description=dish.description, color=color)
        embed.set_image(dish.image_url)
        embeds.append(embed)
    webhook = DiscordWebhook(url=webhook_url)
    for embed in embeds:
        webhook.add_embed(embed)
    res = webhook.execute()
    res.raise_for_status()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gordon Schlemmsay Canteen Bot")
    parser.add_argument("--webhook", type=str, default="", help="Sets the webhook path")
    args = parser.parse_args()
    send_webhook(args.webhook)
