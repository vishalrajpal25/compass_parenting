"""
Provider configuration loader and manager.

Loads provider configurations from YAML file and syncs with database.
Supports environment-specific configurations.
"""
import logging
import os
from pathlib import Path
from typing import Any, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider

logger = logging.getLogger(__name__)


class ProviderConfigLoader:
    """Load and manage provider configurations from YAML."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize provider config loader.

        Args:
            config_path: Path to providers.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Default to app/config/providers.yaml
            config_path = Path(__file__).parent.parent / "config" / "providers.yaml"
        
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        """
        Load provider configuration from YAML file.

        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            logger.warning(f"Provider config file not found: {self.config_path}")
            return {"providers": []}

        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f) or {"providers": []}

        logger.info(f"Loaded {len(self.config.get('providers', []))} providers from {self.config_path}")
        return self.config

    def get_providers(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        """
        Get provider configurations.

        Args:
            enabled_only: If True, only return enabled providers

        Returns:
            List of provider configurations
        """
        if not self.config:
            self.load()

        providers = self.config.get("providers", [])

        if enabled_only:
            providers = [p for p in providers if p.get("enabled", True)]

        return providers

    def resolve_env_vars(self, provider_config: dict[str, Any]) -> dict[str, Any]:
        """
        Resolve environment variables in provider configuration.

        Handles:
        - api_key_env: Reads from environment variable
        - query_params: Can reference env vars

        Args:
            provider_config: Provider configuration dictionary

        Returns:
            Provider configuration with env vars resolved
        """
        config = provider_config.copy()

        # Handle API key from environment
        scraper_config = config.get("scraper_config", {})
        api_key_env = scraper_config.get("api_key_env")
        
        if api_key_env:
            api_key = os.getenv(api_key_env)
            if api_key:
                scraper_config["api_key"] = api_key
                logger.debug(f"Resolved {api_key_env} for provider {config['name']}")
            else:
                logger.warning(
                    f"API key environment variable {api_key_env} not set for provider {config['name']}"
                )
                # Don't fail, just log warning - scraper will handle missing key

        # Resolve query params with env vars
        query_params = scraper_config.get("query_params", {})
        resolved_params = {}
        for key, value in query_params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Environment variable reference: ${VAR_NAME}
                env_var = value[2:-1]
                resolved_value = os.getenv(env_var, value)
                resolved_params[key] = resolved_value
            else:
                resolved_params[key] = value

        if resolved_params:
            scraper_config["query_params"] = resolved_params

        config["scraper_config"] = scraper_config
        return config

    def build_data_source_url(self, provider_config: dict[str, Any]) -> str:
        """
        Build full data source URL with query parameters if needed.

        Args:
            provider_config: Provider configuration

        Returns:
            Full URL with query parameters
        """
        base_url = provider_config["data_source_url"]
        scraper_config = provider_config.get("scraper_config", {})
        query_params = scraper_config.get("query_params", {})

        if not query_params:
            return base_url

        # Build query string
        from urllib.parse import urlencode, urlparse, urlunparse

        # Parse URL to handle existing query params properly
        parsed = urlparse(base_url)
        existing_params = {}
        
        # Parse existing query params if any
        if parsed.query:
            from urllib.parse import parse_qs
            existing_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
        
        # Merge with new params (new params override existing)
        merged_params = {**existing_params, **query_params}
        
        # Rebuild URL
        new_query = urlencode(merged_params)
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)


async def sync_providers_from_config(
    db: AsyncSession,
    config_path: Optional[Path] = None,
    update_existing: bool = True,
) -> dict[str, int]:
    """
    Sync providers from YAML configuration to database.

    Creates new providers or updates existing ones based on name matching.

    Args:
        db: Database session
        config_path: Path to providers.yaml. If None, uses default.
        update_existing: If True, update existing providers. If False, skip existing.

    Returns:
        Dictionary with counts: created, updated, skipped, errors
    """
    loader = ProviderConfigLoader(config_path)
    providers_config = loader.get_providers(enabled_only=True)

    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for provider_config in providers_config:
        try:
            # Resolve environment variables
            provider_config = loader.resolve_env_vars(provider_config)

            # Build full URL with query params if needed
            data_source_url = loader.build_data_source_url(provider_config)

            # Check if provider exists
            result = await db.execute(
                select(Provider).where(Provider.name == provider_config["name"])
            )
            existing = result.scalar_one_or_none()

            # Prepare provider data
            provider_data = {
                "name": provider_config["name"],
                "organization_type": provider_config.get("organization_type"),
                "description": provider_config.get("description"),
                "website": provider_config.get("website"),
                "data_source_type": provider_config.get("data_source_type"),
                "data_source_url": data_source_url,
                "is_verified": provider_config.get("is_verified", False),
            }

            if existing:
                if update_existing:
                    # Update existing provider
                    for key, value in provider_data.items():
                        setattr(existing, key, value)
                    stats["updated"] += 1
                    logger.info(f"Updated provider: {provider_config['name']}")
                else:
                    stats["skipped"] += 1
                    logger.debug(f"Skipped existing provider: {provider_config['name']}")
            else:
                # Create new provider
                provider = Provider(**provider_data)
                db.add(provider)
                stats["created"] += 1
                logger.info(f"Created provider: {provider_config['name']}")

        except Exception as e:
            stats["errors"] += 1
            logger.error(
                f"Error processing provider {provider_config.get('name', 'unknown')}: {str(e)}",
                exc_info=True,
            )

    await db.commit()
    return stats

