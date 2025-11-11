"""
Celery tasks for background scraping.

Celery tasks must be synchronous functions. These tasks wrap async scraper functions.
"""
import asyncio
import logging
from typing import Any, Optional

from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.models.provider import Provider
from app.scrapers.csv_scraper import CSVScraper
from app.scrapers.html_scraper import HTMLScraper
from app.scrapers.ics_scraper import ICScraper
from app.scrapers.json_scraper import JSONScraper
from app.scrapers.rss_scraper import RSSScraper
from app.services.provider_config import ProviderConfigLoader

logger = logging.getLogger(__name__)


async def _scrape_provider_async(provider_id: int, scraper_config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Scrape a single provider.

    Args:
        provider_id: Provider ID to scrape
        scraper_config: Optional scraper configuration (e.g., table_selector for HTML)

    Returns:
        Dictionary with scrape results and metrics
    """
    logger.info(f"Starting scraper task for provider_id={provider_id}")

    async with AsyncSessionLocal() as db:
        # Get provider
        result = await db.execute(
            select(Provider).where(Provider.id == provider_id)
        )
        provider = result.scalar_one_or_none()

        if not provider:
            logger.error(f"Provider {provider_id} not found")
            return {"error": "Provider not found"}

        # Determine scraper type
        scraper_type = provider.data_source_type

        if not scraper_type:
            logger.error(f"Provider {provider.name} has no data_source_type")
            return {"error": "No scraper type configured"}

        # Load scraper_config from YAML if not provided
        if scraper_config is None:
            try:
                loader = ProviderConfigLoader()
                providers_config = loader.get_providers(enabled_only=False)
                provider_config = next(
                    (p for p in providers_config if p["name"] == provider.name),
                    None
                )
                if provider_config:
                    # Resolve env vars and get scraper_config
                    provider_config = loader.resolve_env_vars(provider_config)
                    scraper_config = provider_config.get("scraper_config", {})
            except Exception as e:
                logger.warning(f"Could not load scraper_config from YAML: {str(e)}")
                scraper_config = {}

        # Create appropriate scraper
        scraper = None
        try:
            if scraper_type == "ics":
                scraper = ICScraper(db, provider)
            elif scraper_type == "rss":
                scraper = RSSScraper(db, provider)
            elif scraper_type == "html":
                table_selector = scraper_config.get("table_selector", "table") if scraper_config else "table"
                scraper = HTMLScraper(db, provider, table_selector=table_selector)
            elif scraper_type == "json":
                json_path = scraper_config.get("json_path") if scraper_config else None
                api_key = scraper_config.get("api_key") if scraper_config else None
                scraper = JSONScraper(db, provider, json_path=json_path, api_key=api_key)
            elif scraper_type == "csv":
                encoding = scraper_config.get("encoding", "utf-8") if scraper_config else "utf-8"
                delimiter = scraper_config.get("delimiter", ",") if scraper_config else ","
                scraper = CSVScraper(db, provider, encoding=encoding, delimiter=delimiter)
            else:
                logger.error(f"Unknown scraper type: {scraper_type}")
                return {"error": f"Unknown scraper type: {scraper_type}"}

            # Run scraper
            log = await scraper.run()

            logger.info(
                f"Scraper task completed: provider={provider.name}, "
                f"status={log.status}, pass_rate={log.pass_rate}"
            )

            return {
                "provider_id": provider_id,
                "provider_name": provider.name,
                "status": log.status,
                "activities_found": log.activities_found,
                "activities_passed": log.activities_passed,
                "activities_failed": log.activities_failed,
                "duplicates_found": log.duplicates_found,
                "pass_rate": log.pass_rate,
            }

        except Exception as e:
            logger.error(f"Scraper task failed: {str(e)}", exc_info=True)
            return {
                "provider_id": provider_id,
                "error": str(e),
            }


async def _scrape_all_providers_async() -> dict[str, Any]:
    """
    Scrape all active providers.

    Returns:
        Dictionary with overall results
    """
    logger.info("Starting scrape_all_providers task")

    async with AsyncSessionLocal() as db:
        # Get all providers with data sources
        result = await db.execute(
            select(Provider).where(Provider.data_source_url.isnot(None))
        )
        providers = result.scalars().all()

        logger.info(f"Found {len(providers)} providers to scrape")

        results = []
        for provider in providers:
            try:
                result = await _scrape_provider_async(provider.id)
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Failed to scrape provider {provider.name}: {str(e)}",
                    exc_info=True,
                )
                results.append({
                    "provider_id": provider.id,
                    "provider_name": provider.name,
                    "error": str(e),
                })

        # Summary
        total_providers = len(results)
        successful = sum(1 for r in results if r.get("status") == "success")
        partial = sum(1 for r in results if r.get("status") == "partial")
        failed = sum(1 for r in results if r.get("error") or r.get("status") == "failed")

        logger.info(
            f"scrape_all_providers completed: total={total_providers}, "
            f"successful={successful}, partial={partial}, failed={failed}"
        )

        return {
            "total_providers": total_providers,
            "successful": successful,
            "partial": partial,
            "failed": failed,
            "results": results,
        }


# Sync wrapper functions for Celery (Celery tasks must be synchronous)
def scrape_provider_task(provider_id: int, scraper_config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Celery task to scrape a single provider.
    
    This is a synchronous wrapper around the async scraper function.
    Uses asyncio.run() to execute the async function in a new event loop.
    
    Args:
        provider_id: Provider ID to scrape
        scraper_config: Optional scraper configuration
        
    Returns:
        Dictionary with scrape results and metrics
    """
    try:
        # Use asyncio.run() which creates a new event loop and runs until complete
        return asyncio.run(_scrape_provider_async(provider_id, scraper_config))
    except Exception as e:
        logger.error(f"Error in scrape_provider_task wrapper: {str(e)}", exc_info=True)
        return {
            "provider_id": provider_id,
            "error": str(e),
        }


def scrape_all_providers_task() -> dict[str, Any]:
    """
    Celery task to scrape all active providers.
    
    This is a synchronous wrapper around the async scraper function.
    Uses asyncio.run() to execute the async function in a new event loop.
    
    Returns:
        Dictionary with overall results
    """
    try:
        # Use asyncio.run() which creates a new event loop and runs until complete
        return asyncio.run(_scrape_all_providers_async())
    except Exception as e:
        logger.error(f"Error in scrape_all_providers_task wrapper: {str(e)}", exc_info=True)
        return {
            "error": str(e),
        }
