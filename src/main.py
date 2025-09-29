# main.py

import requests
import logging
from lxml import html
import re
import random
from apify import Actor
from apify_client import ApifyClient
import logging
from apify import Actor
from datetime import datetime, date

# Configure local logging
file_handler = logging.FileHandler("odds_grabber.log", mode="a", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

local_logger = logging.getLogger("OddsGrabberLocal")
local_logger.setLevel(logging.INFO)
local_logger.addHandler(file_handler)

def random_headers():
    return {"User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ])}

def valid_course(course_name):
    return "us-racing" not in course_name.lower()

def get_race_urls(session, racecard_url):
    r = session.get(racecard_url, headers=random_headers())
    doc = html.fromstring(r.content)
    race_urls = []

    for meeting in doc.xpath('//section[@data-accordion-row]'):
        course_elems = meeting.xpath(".//span[contains(@class, 'RC-accordion__courseName')]")
        if not course_elems:
            continue
        course_name = course_elems[0].text_content().strip().lower()
        if valid_course(course_name):
            for race in meeting.xpath(".//a[@class='RC-meetingItem__link js-navigate-url']"):
                href = race.attrib.get('href', '').strip()
                if href:
                    # Fix extra spaces in your original URL
                    race_urls.append('https://www.racingpost.com' + href)

    return sorted(set(race_urls))

def fractional_to_decimal(odds):
    if odds.lower() == "evens":
        return 2.0
    try:
        num, denom = map(int, odds.split("/"))
        return round(num / denom + 1, 2)
    except (ValueError, ZeroDivisionError):
        return None

def scrape_race_odds(session, input_url):
    race_id = input_url.rstrip('/').split("/")[-1]
    response = session.get(input_url, headers=random_headers())

    if response.status_code != 200:
        Actor.log.warning(f"Failed to retrieve {input_url} (status {response.status_code})")
        return []

    doc = html.fromstring(response.content)
    horses = []

    for group in doc.xpath("//span[@data-test-selector='RC-bettingForecast_group']"):
        text = group.text_content().strip()
        match = re.match(r"(\d+/\d+|evens)", text, re.IGNORECASE)
        if not match:
            continue
        odds = match.group(0)
        op_dec = fractional_to_decimal(odds)

        for link in group.xpath(".//a[@data-test-selector='RC-bettingForecast_link']"):
            horse_name = link.text_content().strip()
            href = link.attrib.get('href', '').split("#")[0].strip()
            if not href:
                continue
            full_horse_url = 'https://www.racingpost.com' + href
            horse_parts = href.split("/")
            horse_id = horse_parts[-2] if len(horse_parts) > 2 else ""
            horse_name_from_url = horse_parts[-1] if len(horse_parts) > 1 else ""

            horses.append({
                "race_id": race_id,
                "horse_id": horse_id,
                "horse_name": horse_name_from_url,
                "fodds": odds,
                "opDec": op_dec
            })

    return horses

async def main():
    async with Actor:
        Actor.log.info("Starting OddsGrabber actor...")

        # You can optionally accept input like date, but for now hardcode today
        racecard_url = "https://www.racingpost.com/racecards/"

        session = requests.Session()
        race_urls = get_race_urls(session, racecard_url)

        Actor.log.info(f"Found {len(race_urls)} valid race URLs.")

        for race_url in race_urls:
            Actor.log.info(f"Processing race: {race_url}")
            data = scrape_race_odds(session, race_url)
            for item in data:
                item["timestamp"] = datetime.utcnow().isoformat()
                local_logger.debug(f"Pushing item: {item}")
                await Actor.push_data(item)

                # Save meaningful JSON file in KV store
                filename = f"{date.today().isoformat()}_{item['race_id']}_{item['horse_id']}.json"
                await Actor.set_value(filename, item)

                # Also log locally
                local_logger.info(f"{race_url} -> {item}")



        Actor.log.info("All odds data pushed to dataset.")