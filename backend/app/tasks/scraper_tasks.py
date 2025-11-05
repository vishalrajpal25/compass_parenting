"""
Celery tasks for background scraping.
"""
import logging
from typing import Any

from celery import Celery
from sqlalchemy import select

from app.core.config import settings
from app.db.base import AsyncSessionLocal
from app.models.provider import Provider
from app.scrapers.html_scraper import HTMLScraper
from app.scrapers.ics_scraper import ICScraper
from app.scrapers.rss_scraper import RSSScraper

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "compass",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="scrape_provider")
async def scrape_provider_task(provider_id: int, scraper_config: dict[str, Any] | None = None) -> dict[str, Any]:
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


@celery_app.task(name="scrape_all_providers")
async def scrape_all_providers_task() -> dict[str, Any]:
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
                result = await scrape_provider_task(provider.id)
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
