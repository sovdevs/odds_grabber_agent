# Odds Grabber Actor

## Overview

The **Odds Grabber Actor** is an Apify Actor designed to scrape horse racing odds data from Racing Post. It navigates racecard pages, extracts URLs for individual races, and then scrapes detailed odds information for each horse in those races. The extracted data, including fractional and decimal odds, horse IDs, and race IDs, is then stored in an Apify Dataset and Key-Value Store.

This actor is particularly useful for:
- Researchers analyzing horse racing trends.
- Developers building applications that require real-time or historical odds data.
- Anyone interested in automated data collection from racingpost.com.

## Features

- **Automated Racecard Navigation**: Automatically finds and processes all valid race URLs from the Racing Post racecards.
- **Odds Extraction**: Scrapes fractional and calculated decimal odds for each horse.
- **Data Storage**: Stores structured data in Apify Datasets for easy access and download (JSON, CSV, Excel).
- **Key-Value Store Output**: Saves individual race/horse data as JSON files in the Key-Value Store for quick lookup.
- **Robust Logging**: Provides detailed logs for monitoring the scraping process and debugging.
- **User-Agent Rotation**: Uses a random User-Agent to mimic browser behavior and reduce the chance of being blocked.

## How it Works

The actor performs the following steps:

1.  **Initialization**: Starts an Apify Actor instance and logs the input.
2.  **Racecard Fetching**: Fetches the main Racing Post racecards page.
3.  **Race URL Discovery**: Parses the racecards page to identify and extract URLs for individual races, filtering out irrelevant courses (e.g., "us-racing").
4.  **Race Data Scraping**: For each discovered race URL:
    *   Navigates to the race page.
    *   Extracts horse names, IDs, fractional odds, and calculates decimal odds.
    *   Adds a timestamp to each data item.
5.  **Data Output**:
    *   Pushes each extracted horse's odds data as a separate record to the **default Apify Dataset**.
    *   Saves each horse's odds data as a JSON file in the **default Apify Key-Value Store**, using a filename format like `YYYY-MM-DD_raceid_horseid.json`.

## Input

The actor currently accepts a simple JSON input. While the `racecard_url` is hardcoded in the current version, future enhancements could allow it to be configurable via input.

**Example Input (JSON):**

```json
{
  "helloWorld": 123
}