# Activity & Event Source Feasibility Analysis

**Purpose:** Comprehensive list of sources where parents search for children's activities and events, organized by feasibility for automated ingestion.

**Last Updated:** Based on PRD v4.1 and market research

---

## Feasibility Categories

- **🟢 High Feasibility:** Structured data, APIs, or consistent formats. Low maintenance.
- **🟡 Medium Feasibility:** Requires custom scraping, may need manual configuration per source.
- **🟠 Low Feasibility:** Unstructured, requires significant engineering, or legal/ToS concerns.
- **🔴 Very Low Feasibility:** Prohibited by ToS, requires authentication, or highly variable formats.

---

## 🟢 HIGH FEASIBILITY (Start Here)

### 1. **Public Institution Structured Feeds**
**Already in PRD - Tier 1 Sources**

#### City Recreation Departments
- **Format:** ICS/iCal, CSV, JSON APIs, HTML tables
- **Examples:** 
  - San Francisco Recreation & Parks
  - NYC Parks & Recreation
  - City of Seattle Parks & Recreation
- **Feasibility:** ⭐⭐⭐⭐⭐
- **Implementation:** ICS/RSS/JSON scrapers (already built)
- **Maintenance:** Low - structured, predictable updates

#### Public Library Systems
- **Format:** ICS/RSS feeds per branch, system-wide calendars
- **Examples:**
  - County library event calendars
  - Branch-specific youth programming feeds
- **Feasibility:** ⭐⭐⭐⭐⭐
- **Implementation:** ICS/RSS scrapers
- **Maintenance:** Low

#### YMCA Branches
- **Format:** JSON endpoints, structured HTML, some ICS
- **Examples:** YMCA of [Metro] - Programs pages
- **Feasibility:** ⭐⭐⭐⭐⭐
- **Implementation:** JSON/HTML scrapers (per-branch config)
- **Maintenance:** Medium - need per-branch selector configs

#### Community Centers (JCCs, Boys & Girls Clubs, etc.)
- **Format:** ICS/RSS, JSON calendars
- **Examples:**
  - JCC (Jewish Community Centers) program calendars
  - Boys & Girls Clubs event feeds
  - Parks Conservancies
  - Nature Centers
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** ICS/RSS/JSON scrapers
- **Maintenance:** Medium - multiple organizations, varied formats

### 2. **Youth Sports Organizations (National → Local)**
**Already in PRD**

#### National Organizations with Local Chapters
- **Format:** Chapter-level HTML pages, registration systems
- **Examples:**
  - AYSO (American Youth Soccer Organization) - region pages
  - Little League - local league websites
  - USSSA/Babe Ruth (baseball)
  - US Youth Soccer (clubs)
  - USA Swimming local clubs
  - Scouts (BSA/Girl Scouts) service units
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** HTML scraper with per-org templates
- **Maintenance:** Medium-High - many local chapters, varied structures

### 3. **Event Aggregator APIs**
**Global & Regional Platforms**

#### Eventbrite
- **Format:** Public API (requires API key), web scraping
- **Coverage:** Global, strong in US/UK
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** 
  - API integration (preferred, requires key)
  - HTML scraping (fallback, ToS considerations)
- **Maintenance:** Low-Medium
- **Note:** Filter by category "Kids & Family", location-based

#### Eventful / Songkick
- **Format:** API available (may require key)
- **Coverage:** Global
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** API integration
- **Maintenance:** Low

#### Meetup
- **Format:** Public API (requires OAuth for full access)
- **Coverage:** Global, strong local groups
- **Feasibility:** ⭐⭐⭐
- **Implementation:** API with OAuth, filter by "Family" groups
- **Maintenance:** Medium - API rate limits
- **Note:** Many family activity groups use Meetup

#### Facebook Events (Public)
- **Format:** Graph API (requires app approval), public event pages
- **Coverage:** Global, massive local coverage
- **Feasibility:** ⭐⭐⭐
- **Implementation:** 
  - Graph API (requires Facebook app, review process)
  - Public event page scraping (ToS gray area)
- **Maintenance:** Medium - API changes, rate limits
- **Note:** Filter by location, category "Family & Kids"

### 4. **Parenting Website Event Calendars**
**Structured, Family-Focused**

#### ParentMap (Seattle-based, expanding)
- **Format:** HTML calendar, may have RSS
- **Coverage:** Seattle metro, expanding
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** HTML/RSS scraper
- **Maintenance:** Low-Medium

#### Macaroni Kid (Franchise model, 500+ locations)
- **Format:** Local franchise websites, varied structures
- **Coverage:** 500+ US locations
- **Feasibility:** ⭐⭐⭐
- **Implementation:** HTML scraper with franchise-specific configs
- **Maintenance:** High - many franchises, varied formats
- **Note:** High value but requires per-location setup

#### Red Tricycle (Major metro areas)
- **Format:** HTML event listings
- **Coverage:** Major US metros (SF, LA, NYC, Seattle, etc.)
- **Feasibility:** ⭐⭐⭐
- **Implementation:** HTML scraper
- **Maintenance:** Medium

#### Mommy Poppins (NYC, LA, SF, Boston)
- **Format:** HTML event calendars
- **Coverage:** Major metros
- **Feasibility:** ⭐⭐⭐
- **Implementation:** HTML scraper
- **Maintenance:** Medium

### 5. **School District Extracurriculars**
**When Structured**

- **Format:** ICS/CSV athletic calendars, HTML (avoid PDFs per PRD)
- **Coverage:** Local school districts
- **Feasibility:** ⭐⭐⭐
- **Implementation:** ICS/CSV/HTML scrapers
- **Maintenance:** Medium-High - many districts, varied formats
- **Note:** PRD says auto-demote if validation <70%

### 6. **Civic Event Hubs & Open Data**
**Structured Public Data**

#### City/County Open Data Portals
- **Format:** JSON/CSV APIs, open data portals
- **Examples:**
  - DataSF (San Francisco)
  - NYC Open Data
  - Open Data DC
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** JSON/CSV API integration
- **Maintenance:** Low - standardized formats
- **Note:** Filter datasets tagged "youth", "family", "events"

#### Citywide Event APIs
- **Format:** JSON APIs
- **Examples:** City event calendars with public APIs
- **Feasibility:** ⭐⭐⭐⭐
- **Implementation:** JSON API integration
- **Maintenance:** Low

---

## 🟡 MEDIUM FEASIBILITY

### 7. **Regional Parenting Networks**
**Local, Varied Formats**

#### The Local Moms Network
- **Format:** HTML, varies by location
- **Coverage:** Nationwide network, local chapters
- **Feasibility:** ⭐⭐⭐
- **Implementation:** HTML scraper, per-location configs
- **Maintenance:** Medium-High

#### Upparent
- **Format:** HTML event calendar
- **Coverage:** Location-based
- **Feasibility:** ⭐⭐⭐
- **Implementation:** HTML scraper
- **Maintenance:** Medium

#### Local Moms Blogs/Networks
- **Format:** HTML, WordPress-based often
- **Examples:**
  - Triad Moms on Main (NC)
  - Denton County Moms (TX)
  - North Texas Family eGuide
- **Coverage:** Regional
- **Feasibility:** ⭐⭐⭐
- **Implementation:** HTML scraper, per-site configs
- **Maintenance:** High - many small sites

### 8. **Activity-Specific Aggregators**

#### ClassPass (Kids classes)
- **Format:** API (requires partnership), HTML
- **Coverage:** Major metros
- **Feasibility:** ⭐⭐
- **Implementation:** Partnership required for API
- **Maintenance:** Low (if API access)

#### Sawyer (Activity marketplace)
- **Format:** Provider marketplace, may have API
- **Coverage:** Major metros
- **Feasibility:** ⭐⭐
- **Implementation:** Partnership/API required
- **Maintenance:** Low (if API access)

#### KidPass (Activity marketplace)
- **Format:** Provider marketplace
- **Coverage:** Major metros
- **Feasibility:** ⭐⭐
- **Implementation:** Partnership required
- **Maintenance:** Low (if partnership)

### 9. **Aquatics & Recreation Facilities**
**Direct Providers**

- **Format:** ICS/CSV, HTML tables
- **Examples:** Public pools, swim schools, rec centers
- **Feasibility:** ⭐⭐⭐
- **Implementation:** ICS/CSV/HTML scrapers
- **Maintenance:** Medium - many individual facilities

### 10. **Museum & Cultural Institution Calendars**

#### Museum Event Calendars
- **Format:** ICS, HTML, some APIs
- **Examples:** Children's museums, science centers
- **Feasibility:** ⭐⭐⭐
- **Implementation:** ICS/HTML scrapers
- **Maintenance:** Medium - per-institution configs

#### Cultural Center Calendars
- **Format:** ICS, HTML
- **Examples:** Community cultural centers
- **Feasibility:** ⭐⭐⭐
- **Implementation:** ICS/HTML scrapers
- **Maintenance:** Medium

---

## 🟠 LOW FEASIBILITY

### 11. **Social Media Platforms (Public Groups)**

#### Facebook Groups (Public)
- **Format:** Graph API (limited), web scraping
- **Coverage:** Massive local coverage
- **Feasibility:** ⭐⭐
- **Implementation:**
  - Graph API (requires app, limited group access)
  - Web scraping (ToS violations, anti-bot measures)
- **Maintenance:** High - constant format changes, anti-scraping
- **Note:** High value but legally/technically challenging

#### Nextdoor Events
- **Format:** No public API, requires authentication
- **Coverage:** Hyper-local neighborhoods
- **Feasibility:** ⭐
- **Implementation:** Not feasible without partnership
- **Maintenance:** N/A
- **Note:** High value but requires partnership

#### Reddit (Local subreddits)
- **Format:** Reddit API (public), PRAW library
- **Coverage:** City/region subreddits
- **Feasibility:** ⭐⭐
- **Implementation:** Reddit API, filter by flair/tags
- **Maintenance:** Medium - need to identify relevant posts
- **Note:** Lower signal-to-noise, requires filtering

### 12. **Neighborhood Apps & Forums**

#### Nextdoor
- **Format:** No public API
- **Coverage:** Hyper-local
- **Feasibility:** ⭐
- **Implementation:** Partnership required
- **Note:** High value but no access

#### Local Community Forums
- **Format:** Various (phpBB, vBulletin, custom)
- **Coverage:** Neighborhood-specific
- **Feasibility:** ⭐⭐
- **Implementation:** Custom scrapers per forum
- **Maintenance:** Very High - many small forums, varied tech

### 13. **Email Newsletters & Listservs**

#### Parent Email Lists
- **Format:** Email parsing
- **Coverage:** Local (PTA lists, neighborhood lists)
- **Feasibility:** ⭐
- **Implementation:** Email parsing, NLP extraction
- **Maintenance:** Very High - privacy concerns, varied formats
- **Note:** Privacy/consent issues

### 14. **Word-of-Mouth / Community Chatter**

#### Neighborhood WhatsApp Groups
- **Format:** No API, requires member access
- **Coverage:** Hyper-local
- **Feasibility:** ⭐
- **Implementation:** Not feasible (privacy, ToS)
- **Note:** High value but inaccessible

#### Local Slack Communities
- **Format:** Slack API (requires workspace access)
- **Coverage:** Community-specific
- **Feasibility:** ⭐
- **Implementation:** Requires workspace membership
- **Note:** Privacy/access barriers

---

## 🔴 VERY LOW FEASIBILITY (Avoid in MVP)

### 15. **Private/Paid Platforms**

#### Peanut (Mom social app)
- **Format:** No public API, mobile app only
- **Feasibility:** ⭐
- **Note:** Requires partnership

#### Local Facebook Groups (Private)
- **Format:** No API access, requires membership
- **Feasibility:** ⭐
- **Note:** Privacy violations, ToS violations

#### Instagram (Event posts)
- **Format:** Instagram Graph API (limited, requires business account)
- **Feasibility:** ⭐
- **Note:** Low structure, high noise

### 16. **PDF-Based Sources**
**Explicitly Out of Scope per PRD**

- School district PDFs
- City program brochures
- **Feasibility:** ⭐ (explicitly excluded)
- **Note:** PRD says "No PDFs in MVP"

---

## Implementation Priority Matrix

### Phase 1 (MVP - Weeks 1-2)
**Focus: Structured, high-value, low-maintenance**

1. ✅ City Recreation Departments (ICS/CSV/JSON)
2. ✅ Public Library Systems (ICS/RSS)
3. ✅ YMCA Branches (JSON/HTML)
4. ✅ Community Centers (JCCs, Boys & Girls Clubs) (ICS/RSS)
5. ✅ Eventbrite API (if API key available)
6. ✅ City Open Data Portals (JSON/CSV)

### Phase 2 (Post-MVP)
**Medium effort, good coverage**

7. Youth Sports Organizations (AYSO, Little League, etc.)
8. Parenting websites (ParentMap, Macaroni Kid franchises)
9. Museum & Cultural Institution calendars
10. Facebook Events API (if app approved)

### Phase 3 (Scale)
**Higher maintenance, but valuable**

11. Regional parenting networks (Local Moms Network, etc.)
12. School district extracurriculars (structured only)
13. Activity marketplaces (if partnerships available)

### Phase 4 (Advanced)
**High effort, experimental**

14. Reddit local subreddits (with heavy filtering)
15. Public Facebook Groups (if legal/ToS cleared)

---

## Key Considerations

### Legal & ToS
- **Respect robots.txt** (PRD requirement)
- **Rate limiting** (PRD requirement)
- **User-Agent with contact email** (PRD requirement)
- **Cease on request** (PRD requirement)
- **Facebook/Instagram:** Review ToS carefully, may require app approval
- **Email lists:** Privacy/consent issues

### Technical Challenges
- **Anti-bot measures:** Many sites use Cloudflare, CAPTCHA
- **JavaScript-heavy sites:** Require headless browsers (Selenium/Playwright)
- **Format variability:** Same org type, different structures
- **Maintenance burden:** PRD says <1 hr/week per feature

### Data Quality
- **Validation thresholds:** ≥85% pass rate, ≤5% broken links (PRD)
- **Auto-demote:** If thresholds not met for 2 consecutive runs
- **Deduplication:** Canon hash per PRD spec

### Coverage vs. Maintenance Trade-off
- **High coverage, low maintenance:** Public institution feeds (ICS/RSS/JSON)
- **Medium coverage, medium maintenance:** Parenting websites
- **High coverage, high maintenance:** Facebook Groups, local forums
- **Hyper-local, very high maintenance:** Neighborhood apps, WhatsApp groups

---

## Recommendations

1. **Start with Tier-1 structured sources** (already in PRD) - these are the foundation
2. **Add Eventbrite API** if possible - high coverage, structured data
3. **Consider Facebook Events API** post-MVP - massive coverage but requires app approval
4. **Avoid PDFs, private groups, email lists** - too high maintenance or legal risk
5. **Focus on one metro first** - validate approach before scaling
6. **Build flexible scraper framework** - handle ICS/RSS/JSON/HTML with configs
7. **Monitor maintenance burden** - deprecate sources that exceed 1 hr/week

---

## Source Count Summary

- **🟢 High Feasibility:** ~15-20 source types (hundreds of individual sources)
- **🟡 Medium Feasibility:** ~10 source types (dozens of individual sources)
- **🟠 Low Feasibility:** ~5 source types (many individual sources, high maintenance)
- **🔴 Very Low Feasibility:** ~5 source types (avoid in MVP)

**Total Potential Sources:** Hundreds of individual providers across all categories, but focus on structured, maintainable sources first.

