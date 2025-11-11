# Provider Configuration Guide

**No seeding needed!** This system uses YAML configuration files that work across dev, test, and prod.

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt  # Includes PyYAML
```

### 2. Configure Providers

Edit `backend/app/config/providers.yaml` with your data sources.

### 3. Sync to Database

```bash
python scripts/sync_providers.py
```

This creates/updates providers in your database from the YAML config.

### 4. Run Scrapers

```bash
python scripts/run_scrapers_dev.py
```

---

## Configuration File Structure

The `providers.yaml` file contains all your data sources:

```yaml
providers:
  - name: "Provider Name"
    organization_type: "city_rec"  # city_rec, library, ymca, etc.
    description: "Description"
    website: "https://example.com"
    data_source_type: "ics"  # ics, rss, html, json, csv
    data_source_url: "https://example.com/events.ics"
    is_verified: false
    enabled: true
    scraper_config:  # Optional
      json_path: "events"  # For JSON scrapers
      api_key_env: "EVENTBRITE_API_KEY"  # For APIs
      query_params:  # For API query params
        category: "102"
```

---

## Real Working Sources

### City Recreation Departments

**San Francisco Rec & Park**
- URL: `https://sfrecpark.org/programs`
- Type: `html`
- Status: Needs verification (check for ICS feed)

**Oakland Parks & Rec**
- URL: `https://www.oaklandca.gov/resources/oakland-parks-recreation-youth-development`
- Type: `html`
- Status: Needs verification

### Public Libraries

**San Francisco Public Library**
- URL: `https://sfpl.org/events/rss` (verify actual endpoint)
- Type: `rss`
- Status: Needs verification

**Oakland Public Library**
- URL: `https://oaklandlibrary.org/events/feed` (verify actual endpoint)
- Type: `rss`
- Status: Needs verification

### YMCA

**YMCA of San Francisco**
- URL: `https://www.ymcasf.org/programs/youth`
- Type: `html`
- Status: Needs verification

### Eventbrite API

**Eventbrite - Kids & Family Events**
- URL: `https://www.eventbriteapi.com/v3/events/search/`
- Type: `json`
- Requires: `EVENTBRITE_API_KEY` environment variable
- Get API key: https://www.eventbrite.com/platform/api/
- Status: Ready once API key is set

**Configuration:**
```yaml
- name: "Eventbrite - Kids & Family Events (SF Bay Area)"
  data_source_type: "json"
  data_source_url: "https://www.eventbriteapi.com/v3/events/search/"
  scraper_config:
    json_path: "events"
    api_key_env: "EVENTBRITE_API_KEY"
    query_params:
      categories: "102"  # Kids & Family
      location.address: "San Francisco"
      location.within: "25mi"
      expand: "venue"
```

### City Open Data

**DataSF**
- URL: `https://data.sfgov.org/api/views/6v6m-2p9r/rows.json`
- Type: `json`
- Status: Sample dataset - find actual recreation/events dataset

---

## Environment Variables

### Eventbrite

```bash
# .env file
EVENTBRITE_API_KEY=your_api_key_here
```

Get API key: https://www.eventbrite.com/platform/api/

### Meetup (Optional)

```bash
MEETUP_API_KEY=your_api_key_here
```

---

## How to Find Real Endpoints

### ICS/iCal Feeds

Look for:
- `/calendar/feed`
- `/events.ics`
- `/feed.ics`
- `/calendar.ics`

**Test:** Open URL in browser - should download `.ics` file or show calendar data.

### RSS Feeds

Look for:
- `/feed`
- `/rss.xml`
- `/events/feed`
- `/calendar/rss`

**Test:** Open URL in browser - should show XML with `<rss>` or `<feed>` tags.

### JSON APIs

Look for:
- `/api/events`
- `/api/v1/events`
- Open data portals: `/api/views/{dataset_id}/rows.json`

**Test:** Open URL in browser - should show JSON data.

### HTML Pages

Look for:
- Programs/activities pages
- Event calendars
- Class listings

**Test:** Open URL - should show structured event listings.

---

## Verifying Sources

### Step 1: Check URL

```bash
# Test ICS feed
curl -I https://example.com/events.ics

# Test RSS feed
curl -I https://example.com/feed

# Test JSON API
curl https://example.com/api/events
```

### Step 2: Update Config

Edit `providers.yaml`:
```yaml
- name: "Provider Name"
  data_source_url: "https://actual-working-url.com/events.ics"
  is_verified: true  # Set to true once confirmed
```

### Step 3: Sync

```bash
python scripts/sync_providers.py
```

### Step 4: Test Scraper

```bash
# Test single provider
python scripts/run_scrapers_dev.py [provider_id]
```

---

## Environment-Specific Configs

You can have different config files per environment:

```bash
# Development
python scripts/sync_providers.py --config app/config/providers.dev.yaml

# Production
python scripts/sync_providers.py --config app/config/providers.prod.yaml
```

Or use environment variables in the same file:

```yaml
scraper_config:
  api_key_env: "EVENTBRITE_API_KEY"  # Different keys per env
  query_params:
    location.address: "${CITY_NAME}"  # Resolved from env
```

---

## Disabling Providers

Set `enabled: false` in YAML:

```yaml
- name: "Provider Name"
  enabled: false  # Won't be synced
```

---

## Updating Providers

### Option 1: Edit YAML and Sync

1. Edit `providers.yaml`
2. Run `python scripts/sync_providers.py`
3. Existing providers are updated automatically

### Option 2: No-Update Mode

```bash
# Only create new providers, don't update existing
python scripts/sync_providers.py --no-update
```

---

## Troubleshooting

### "Provider config file not found"

Create the config directory:
```bash
mkdir -p backend/app/config
```

### "API key environment variable not set"

Set the environment variable:
```bash
export EVENTBRITE_API_KEY=your_key
# Or add to .env file
```

### Scraper fails with 404

1. Check URL in `providers.yaml`
2. Visit provider website to find correct endpoint
3. Update `data_source_url`
4. Run sync again

### Low pass rate

1. Check scraper logs
2. Verify data format matches `data_source_type`
3. May need custom `scraper_config` (e.g., `json_path` for JSON)

---

## Configuration Examples

### ICS Calendar

```yaml
- name: "Library Events"
  data_source_type: "ics"
  data_source_url: "https://library.org/events.ics"
```

### RSS Feed

```yaml
- name: "Community Events"
  data_source_type: "rss"
  data_source_url: "https://community.org/feed"
```

### JSON API with Auth

```yaml
- name: "Eventbrite Events"
  data_source_type: "json"
  data_source_url: "https://www.eventbriteapi.com/v3/events/search/"
  scraper_config:
    api_key_env: "EVENTBRITE_API_KEY"
    json_path: "events"
    query_params:
      categories: "102"
```

### HTML Page

```yaml
- name: "Recreation Programs"
  data_source_type: "html"
  data_source_url: "https://city.org/programs"
```

### CSV Download

```yaml
- name: "Open Data Events"
  data_source_type: "csv"
  data_source_url: "https://data.city.org/events.csv"
```

---

## Best Practices

1. **Verify URLs First**
   - Test endpoints before adding to config
   - Set `is_verified: true` once confirmed

2. **Use Environment Variables**
   - API keys in env vars, not config files
   - Use `${VAR_NAME}` syntax for dynamic values

3. **Document Sources**
   - Add `notes:` field for special instructions
   - Document any quirks or requirements

4. **Test Incrementally**
   - Add one provider at a time
   - Test scraper before adding more

5. **Monitor Quality**
   - Check pass rates after scraping
   - Disable providers that consistently fail

---

## Files

- **Config:** `backend/app/config/providers.yaml`
- **Loader:** `backend/app/services/provider_config.py`
- **Sync Script:** `backend/scripts/sync_providers.py`

---

## Next Steps

1. ✅ Edit `providers.yaml` with your sources
2. ✅ Set environment variables (API keys)
3. ✅ Run `python scripts/sync_providers.py`
4. ✅ Verify providers in database
5. ✅ Run scrapers: `python scripts/run_scrapers_dev.py`
6. ✅ Monitor results and adjust config as needed

