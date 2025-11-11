# Quick Start: Provider Configuration

**No seeding!** Use YAML configuration files that work across dev, test, and prod.

---

## 3-Step Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt  # Includes PyYAML
```

### 2. Configure Providers

Edit `backend/app/config/providers.yaml` with your data sources.

**Example:**
```yaml
providers:
  - name: "San Francisco Recreation and Parks"
    organization_type: "city_rec"
    data_source_type: "html"
    data_source_url: "https://sfrecpark.org/programs"
    enabled: true
```

### 3. Sync to Database

```bash
python scripts/sync_providers.py
```

This creates/updates providers in your database from the YAML config.

---

## Run Scrapers

```bash
# Test one provider
python scripts/run_scrapers_dev.py [provider_id]

# Run all providers
python scripts/run_scrapers_dev.py
```

---

## Real Working Sources

### Eventbrite (Requires API Key)

1. Get API key: https://www.eventbrite.com/platform/api/
2. Add to `.env`:
   ```
   EVENTBRITE_API_KEY=your_key_here
   ```
3. Already configured in `providers.yaml` - just sync!

### Other Sources

Edit `providers.yaml` with actual URLs:
- **ICS feeds:** `/calendar/feed`, `/events.ics`
- **RSS feeds:** `/feed`, `/rss.xml`
- **JSON APIs:** `/api/events`
- **HTML pages:** Programs/activities pages

---

## Verify Sources

1. Test URL in browser
2. Update `data_source_url` in `providers.yaml`
3. Set `is_verified: true`
4. Run `python scripts/sync_providers.py`

---

## Files

- **Config:** `backend/app/config/providers.yaml`
- **Sync Script:** `backend/scripts/sync_providers.py`
- **Scrapers:** `backend/scripts/run_scrapers_dev.py`

---

## Full Documentation

See `docs/PROVIDER_CONFIGURATION.md` for complete guide.

