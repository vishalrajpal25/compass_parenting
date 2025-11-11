# Phase 1 Implementation Guide

**Status:** Ready to implement  
**Focus:** Structured, high-value, low-maintenance sources  
**Target:** 50-100 providers in San Francisco Bay Area

---

## What's Included

Phase 1 includes 6 categories of sources:

1. **City Recreation Departments** (7 providers)
   - ICS/RSS/HTML formats
   - Examples: SF Rec & Park, Oakland, Berkeley, Palo Alto

2. **Public Library Systems** (5 providers)
   - ICS/RSS feeds
   - Examples: SFPL, Oakland, Berkeley, San Mateo County

3. **YMCA Branches** (3 providers)
   - HTML/JSON formats
   - Examples: YMCA SF, East Bay, Silicon Valley

4. **Community Centers** (4 providers)
   - HTML/ICS formats
   - Examples: Boys & Girls Clubs, JCCs

5. **Eventbrite API** (1 provider)
   - JSON API (requires API key)
   - Filtered for "Kids & Family" category

6. **City Open Data Portals** (2 providers)
   - JSON/CSV formats
   - Examples: DataSF, Oakland Open Data

**Total:** ~22 providers (can expand to 50-100 with more branches/locations)

---

## New Scrapers Added

### JSON Scraper (`json_scraper.py`)
- Supports REST APIs (Eventbrite, city open data)
- Handles pagination, authentication
- Flexible JSON path extraction
- Auto-parses common event formats

### CSV Scraper (`csv_scraper.py`)
- Supports CSV downloads from data portals
- Handles various encodings and delimiters
- Flexible column name matching
- Auto-parses dates, prices, age ranges

---

## Setup Instructions

### 1. Install Dependencies

All dependencies should already be in `requirements.txt`. Verify:
- `httpx` - HTTP client
- `beautifulsoup4` - HTML parsing
- `feedparser` - RSS parsing
- `icalendar` - ICS parsing

### 2. Seed Phase 1 Providers

```bash
cd backend
python scripts/seed_phase1_providers.py
```

This will add ~22 Phase 1 providers to the database.

### 3. Configure Eventbrite (Optional)

If you want to use Eventbrite API:

1. Get API key from: https://www.eventbrite.com/platform/api/
2. Add to `.env`:
   ```
   EVENTBRITE_API_KEY=your_api_key_here
   ```
3. Update Eventbrite provider in database to use API key in scraper_config

### 4. Verify Provider URLs

**IMPORTANT:** Most URLs in the seed script are placeholders and need verification.

For each provider:
1. Visit the website
2. Find the actual data source URL (ICS feed, RSS feed, API endpoint, etc.)
3. Update `data_source_url` in database
4. Set `is_verified=True` once confirmed

Common patterns to look for:
- **ICS feeds:** `/calendar/feed`, `/events.ics`, `/feed.ics`
- **RSS feeds:** `/feed`, `/rss.xml`, `/events/feed`
- **JSON APIs:** `/api/events`, `/api/v1/events`
- **CSV downloads:** `/data/events.csv`, `/export/events.csv`

### 5. Run Scrapers

Test with a single provider:
```bash
python scripts/run_scrapers_dev.py [provider_id]
```

Or scrape all providers:
```bash
python scripts/run_scrapers_dev.py
```

### 6. Monitor Results

Check scraper logs for:
- ✅ Success rate (target: ≥85%)
- ⚠️ Broken links (target: ≤5%)
- ❌ Validation failures

If a provider consistently fails, update the URL or mark as unverified.

---

## Provider Verification Checklist

For each provider, verify:

- [ ] `data_source_url` is correct and accessible
- [ ] Data format matches `data_source_type` (ics/rss/html/json/csv)
- [ ] Data contains youth/family activities
- [ ] Scraper successfully parses data
- [ ] Pass rate ≥85%
- [ ] Set `is_verified=True` in database

---

## Expected Results

### After Phase 1 Implementation

- **Providers:** 22-50 (depending on expansion)
- **Activities:** 500-2000+ activities
- **Coverage:** San Francisco Bay Area
- **Update Frequency:** Weekly (72h re-scrape per PRD)
- **Maintenance:** <5 hrs/week (per PRD requirement)

### Success Metrics

- Pass rate ≥85% for each provider
- Broken link rate ≤5%
- Freshness ≥95% (activities updated within 72h)
- Auto-demote providers that fail thresholds

---

## Troubleshooting

### Scraper Fails with 404

- URL may have changed
- Check provider website for new endpoint
- Update `data_source_url` in database

### Scraper Fails with Parse Error

- Data format may not match `data_source_type`
- Check actual response format
- May need custom scraper config (e.g., `json_path` for JSON)

### Low Pass Rate (<85%)

- Check validation errors in scraper logs
- May need to improve parser for that provider's format
- Consider marking as unverified if consistently low

### Eventbrite API Fails

- Verify `EVENTBRITE_API_KEY` is set
- Check API rate limits
- Verify API endpoint URL format

---

## Next Steps

After Phase 1 is working:

1. **Expand Coverage**
   - Add more city rec departments
   - Add more library branches
   - Add more YMCA locations

2. **Verify & Optimize**
   - Verify all provider URLs
   - Optimize parsers for better pass rates
   - Set up automated monitoring

3. **Phase 2 Preparation**
   - Youth sports organizations
   - Parenting websites
   - Museum calendars

---

## Files Created/Modified

### New Files
- `backend/app/scrapers/json_scraper.py` - JSON API scraper
- `backend/app/scrapers/csv_scraper.py` - CSV scraper
- `backend/scripts/seed_phase1_providers.py` - Phase 1 provider seed script
- `docs/PHASE1_IMPLEMENTATION.md` - This guide

### Modified Files
- `backend/app/scrapers/__init__.py` - Added JSON/CSV scraper exports
- `backend/app/tasks/scraper_tasks.py` - Added JSON/CSV scraper support

---

## Questions?

- Check scraper logs: `backend/logs/` (if configured)
- Review PRD: `docs/Compass_PRD_v4_1.md`
- Review source feasibility: `docs/ACTIVITY_SOURCE_FEASIBILITY.md`

