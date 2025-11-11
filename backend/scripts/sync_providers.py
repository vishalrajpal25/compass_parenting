"""
Sync providers from YAML configuration to database.

This script reads providers.yaml and creates/updates providers in the database.
Use this instead of seeding - it's configuration-driven and works across environments.

Usage:
    python scripts/sync_providers.py [--config path/to/providers.yaml] [--no-update]

Options:
    --config: Path to providers.yaml (default: app/config/providers.yaml)
    --no-update: Don't update existing providers, only create new ones
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import AsyncSessionLocal
from app.services.provider_config import sync_providers_from_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for provider sync script."""
    parser = argparse.ArgumentParser(description="Sync providers from YAML config to database")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to providers.yaml (default: app/config/providers.yaml)"
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Don't update existing providers, only create new ones"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Provider Configuration Sync")
    logger.info("=" * 60)
    
    config_path = args.config
    if config_path:
        logger.info(f"Using config file: {config_path}")
    else:
        logger.info("Using default config file: app/config/providers.yaml")
    
    update_existing = not args.no_update
    
    async with AsyncSessionLocal() as db:
        try:
            stats = await sync_providers_from_config(
                db=db,
                config_path=config_path,
                update_existing=update_existing,
            )
            
            logger.info("")
            logger.info("=" * 60)
            logger.info("✅ Sync complete!")
            logger.info(f"   Created: {stats['created']}")
            logger.info(f"   Updated: {stats['updated']}")
            logger.info(f"   Skipped: {stats['skipped']}")
            if stats['errors'] > 0:
                logger.warning(f"   Errors: {stats['errors']}")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Verify providers in database")
            logger.info("2. Run scrapers: python scripts/run_scrapers_dev.py")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error syncing providers: {str(e)}", exc_info=True)
            await db.rollback()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

