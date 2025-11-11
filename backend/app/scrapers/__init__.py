"""
Scraper modules for ingesting activity data from various sources.
"""
from app.scrapers.base import BaseScraper
from app.scrapers.csv_scraper import CSVScraper
from app.scrapers.html_scraper import HTMLScraper
from app.scrapers.ics_scraper import ICScraper
from app.scrapers.json_scraper import JSONScraper
from app.scrapers.rss_scraper import RSSScraper

__all__ = [
    "BaseScraper",
    "CSVScraper",
    "HTMLScraper",
    "ICScraper",
    "JSONScraper",
    "RSSScraper",
]

