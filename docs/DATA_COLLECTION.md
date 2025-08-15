# Data collection (Vahan) — how to refresh the data

> This project includes a reproducible (documented) web-scraping flow that targets the public Vahan dashboard pages.

## What it collects
- Vehicle category totals (2W, 3W, 4W)
- Manufacturer-wise monthly registrations

## Tools
- Selenium WebDriver (Chrome)
- BeautifulSoup (backup for static sections)
- SQLite for local storage (`data/vehicle_registrations.db`)

## Running the scraper
1. Install deps: `pip install -r requirements.txt`
2. Ensure Chrome + chromedriver (or use `webdriver-manager` if preferred).
3. Run: `python data_collection.py --refresh`
4. On success you’ll see new rows in the `registrations` table and a CSV snapshot in `data/`.

## Notes
- The dashboard is dynamic. The scraper waits for specific selectors before reading tables.
- If the site layout changes, update the CSS/XPath selectors at the top of `data_collection.py`.
- If scraping fails (connectivity or structure change), the app falls back to a bundled sample dataset so the dashboard still works.
