# Compass Technical Specification v1.0

**Document Type:** Technical Specification  
**Version:** 1.0  
**Date:** November 04, 2025  
**Status:** Implementation Ready  
**Based on:** PRD v4.2

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Data Models & Schema](#3-data-models--schema)
4. [API Specifications](#4-api-specifications)
5. [Catalog Ingestion Pipeline](#5-catalog-ingestion-pipeline)
6. [Recommendation Engine](#6-recommendation-engine)
7. [Constraint Solver](#7-constraint-solver)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Deployment & Infrastructure](#9-deployment--infrastructure)
10. [Implementation Phases](#10-implementation-phases)

---

## 1. Architecture Overview

### System Components

```
┌─────────────────────────────────────────────┐
│   Client: React PWA (Vite + Tailwind)      │
│   - Mobile-first responsive design          │
│   - Offline capability (service worker)     │
└─────────────────────────────────────────────┘
                    ↓ HTTPS
┌─────────────────────────────────────────────┐
│   API Gateway (FastAPI)                     │
│   - Authentication (JWT)                    │
│   - Rate limiting                           │
│   - Request validation                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Core Services (Python)                    │
│   - Profile Service                         │
│   - Catalog Service                         │
│   - Recommender Service                     │
│   - Solver Service (OR-Tools CP-SAT)        │
│   - LLM Service (OpenAI/Anthropic)          │
│   - Radar/Alerts Service                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Background Workers (Celery)               │
│   - Catalog scrapers (72hr cycle)           │
│   - De-duplication                          │
│   - Quality validation                      │
│   - Radar digest generation                 │
│   - Email dispatch                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Data Layer                                │
│   - PostgreSQL (primary data)               │
│   - Redis (caching, job queue)              │
│   - S3/R2 (file storage)                    │
│   - Qdrant (vector DB for LLM)              │
└─────────────────────────────────────────────┘
```

### Design Principles

1. **API-First**: All functionality exposed via REST APIs
2. **Stateless Services**: Horizontal scaling capability
3. **Asynchronous Processing**: Long-running tasks in background workers
4. **Fail-Safe Defaults**: Degrade gracefully when services unavailable
5. **Observable**: Logging, metrics, tracing throughout

---

## 2. Technology Stack

### Backend

- **Framework**: FastAPI 0.104+ (Python 3.11+)
- **ORM**: SQLAlchemy 2.0+ with Alembic migrations
- **Database**: PostgreSQL 16+
- **Cache**: Redis 7+
- **Task Queue**: Celery 5+ with Redis broker
- **Constraint Solver**: OR-Tools (CP-SAT solver)
- **Scheduling**: APScheduler for cron jobs
- **LLM Integration**: OpenAI Python SDK / Anthropic SDK
- **Vector DB**: Qdrant (self-hosted)
- **Email**: SendGrid or Mailgun SDK

### Frontend

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite 5+
- **Styling**: Tailwind CSS 3+
- **State Management**: Zustand (lightweight)
- **Routing**: React Router 6+
- **HTTP Client**: Axios with interceptors
- **Forms**: React Hook Form + Zod validation
- **Calendar**: ics.js for .ics generation/parsing
- **PWA**: Vite PWA plugin

### DevOps & Infrastructure

- **Hosting**: Railway.app or Fly.io (backend), Vercel (frontend)
- **Object Storage**: Cloudflare R2 or AWS S3
- **Monitoring**: Sentry (errors), Plausible (analytics)
- **Email**: SendGrid or Mailgun
- **DNS/CDN**: Cloudflare
- **Version Control**: Git + GitHub

### Development Tools

- **Package Management**: 
  - Backend: Poetry or pip-tools
  - Frontend: pnpm
- **Linting/Formatting**:
  - Backend: ruff, black, mypy
  - Frontend: ESLint, Prettier
- **Testing**:
  - Backend: pytest, pytest-asyncio
  - Frontend: Vitest, React Testing Library
- **CI/CD**: GitHub Actions

---

## 3. Data Models & Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
```

#### families
```sql
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    geo_block_centroid GEOGRAPHY(POINT),  -- PostGIS
    partner_emails TEXT[],
    languages TEXT[] DEFAULT ARRAY['en'],
    imported_calendar_ics BYTEA,  -- Stored .ics file
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_families_user_id ON families(user_id);
CREATE INDEX idx_families_geo ON families USING GIST(geo_block_centroid);
```

#### child_profiles
```sql
CREATE TABLE child_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 2 AND age <= 18),
    grade VARCHAR(20),
    
    -- Temperament (JSONB for flexibility)
    temperament JSONB NOT NULL,  
    -- Example: {"social": "moderate", "sensory_tolerance": "low", "energy": "high", 
    --           "team_preference": "solo", "competitive_comfort": "low",
    --           "neurodiversity_flags": ["low_sensory", "small_group"]}
    
    -- Goals (ranked array)
    goals TEXT[] NOT NULL,  -- ["fitness", "social", "creative"]
    
    -- Constraints
    budget_per_month DECIMAL(10, 2),
    driving_radius_km DECIMAL(5, 2),
    car_light_preference BOOLEAN DEFAULT FALSE,
    
    -- Schedule windows (JSONB array of time blocks)
    schedule_windows JSONB NOT NULL,
    -- Example: [{"day": "TU", "start": "16:00", "end": "18:00"}, ...]
    
    -- Current activities
    current_activities JSONB DEFAULT '[]',
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_child_profiles_family_id ON child_profiles(family_id);
CREATE INDEX idx_child_profiles_age ON child_profiles(age);
CREATE INDEX idx_child_profiles_temperament ON child_profiles USING GIN(temperament);
```

#### venues
```sql
CREATE TABLE venues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip VARCHAR(10) NOT NULL,
    
    -- Geocoding
    location GEOGRAPHY(POINT) NOT NULL,  -- PostGIS
    geohash VARCHAR(12) NOT NULL,  -- Geohash for proximity
    timezone VARCHAR(50) NOT NULL,  -- IANA timezone
    
    -- Attributes
    transit_accessible BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(address, city, state, zip)
);

CREATE INDEX idx_venues_location ON venues USING GIST(location);
CREATE INDEX idx_venues_geohash ON venues(geohash);
CREATE INDEX idx_venues_city_state ON venues(city, state);
```

#### providers
```sql
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- city_rec, library, ymca, etc.
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    website_url VARCHAR(500),
    safety_policies_url VARCHAR(500),
    
    -- Reliability
    source_reliability_score DECIMAL(3, 2) DEFAULT 1.0,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_providers_type ON providers(type);
```

#### activities
```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id),
    venue_id UUID NOT NULL REFERENCES venues(id),
    
    -- Basic info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,  -- soccer, swim, theater, etc.
    subcategory VARCHAR(50),
    
    -- Age/prerequisites
    age_min INTEGER NOT NULL CHECK (age_min >= 2),
    age_max INTEGER NOT NULL CHECK (age_max <= 18),
    prerequisites TEXT,
    
    -- Attributes (JSONB for flexibility)
    attributes JSONB NOT NULL,
    -- Example: {"intensity": "medium", "sensory_load": "low", 
    --           "competitive_pressure": "none", "team_vs_solo": "team",
    --           "indoor_outdoor": "outdoor", "group_size": "small",
    --           "neurodiversity_friendly": ["low_sensory", "predictable"]}
    
    -- Pricing
    money JSONB NOT NULL,  -- {"amount": 120, "currency": "USD", "period": "season"}
    scholarships_available BOOLEAN DEFAULT FALSE,
    
    -- Schedule
    schedule_rrule TEXT NOT NULL,  -- RFC 5545 RRULE
    -- Example: "DTSTART:20250915T160000\nRRULE:FREQ=WEEKLY;BYDAY=TU,TH"
    
    seasonality VARCHAR(20),  -- fall, winter, spring, summer, year-round
    signup_deadline TIMESTAMP,
    
    -- Source tracking
    source_item_id VARCHAR(255),
    source_url VARCHAR(500) NOT NULL,
    scraper_id VARCHAR(100) NOT NULL,
    canon_hash VARCHAR(64) NOT NULL,  -- For de-duplication
    
    -- Quality
    last_verified TIMESTAMP NOT NULL,
    is_recommendable BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activities_provider_id ON activities(provider_id);
CREATE INDEX idx_activities_venue_id ON activities(venue_id);
CREATE INDEX idx_activities_category ON activities(category);
CREATE INDEX idx_activities_age_range ON activities(age_min, age_max);
CREATE INDEX idx_activities_canon_hash ON activities(canon_hash);
CREATE INDEX idx_activities_recommendable ON activities(is_recommendable) WHERE is_recommendable = TRUE;
CREATE INDEX idx_activities_attributes ON activities USING GIN(attributes);
```

#### scraper_logs
```sql
CREATE TABLE scraper_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scraper_id VARCHAR(100) NOT NULL,
    source_url VARCHAR(500) NOT NULL,
    run_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Results
    items_found INTEGER NOT NULL DEFAULT 0,
    items_created INTEGER NOT NULL DEFAULT 0,
    items_updated INTEGER NOT NULL DEFAULT 0,
    items_flagged INTEGER NOT NULL DEFAULT 0,
    
    -- Quality metrics
    pass_rate DECIMAL(5, 2),  -- Percentage
    broken_link_rate DECIMAL(5, 2),
    
    -- Errors
    errors JSONB DEFAULT '[]',
    
    status VARCHAR(20) NOT NULL DEFAULT 'success',  -- success, partial, failed
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scraper_logs_scraper_id ON scraper_logs(scraper_id);
CREATE INDEX idx_scraper_logs_run_timestamp ON scraper_logs(run_timestamp DESC);
```

#### event_telemetry
```sql
CREATE TABLE event_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_profile_id UUID REFERENCES child_profiles(id) ON DELETE SET NULL,
    activity_id UUID REFERENCES activities(id) ON DELETE SET NULL,
    
    event_type VARCHAR(50) NOT NULL,  
    -- recommendation_shown, accepted_clicked, contacted, calendar_exported, 
    -- continue_30, continue_60, satisfaction_rating, reported
    
    event_data JSONB,  -- Flexible storage for event-specific data
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_telemetry_child_profile ON event_telemetry(child_profile_id);
CREATE INDEX idx_telemetry_activity ON event_telemetry(activity_id);
CREATE INDEX idx_telemetry_event_type ON event_telemetry(event_type);
CREATE INDEX idx_telemetry_created_at ON event_telemetry(created_at DESC);
```

#### partner_shares
```sql
CREATE TABLE partner_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    share_token VARCHAR(255) UNIQUE NOT NULL,
    
    -- Recommendations snapshot (JSONB)
    recommendations JSONB NOT NULL,
    
    -- Partner input
    partner_votes JSONB DEFAULT '{}',  -- {"activity_id": "up" | "down"}
    partner_notes TEXT,
    partner_constraints JSONB DEFAULT '{}',
    
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_partner_shares_token ON partner_shares(share_token);
CREATE INDEX idx_partner_shares_family_id ON partner_shares(family_id);
CREATE INDEX idx_partner_shares_expires ON partner_shares(expires_at);
```

### Indexes Strategy

- **Primary keys**: All UUIDs for better distribution
- **Foreign keys**: Always indexed for join performance
- **JSONB columns**: GIN indexes for flexible queries
- **Geospatial**: PostGIS GIST indexes for proximity
- **Time-series**: DESC indexes on timestamp columns
- **Partial indexes**: On boolean flags for filtered queries

---

## 4. API Specifications

### Authentication

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/verify-email
POST /api/auth/forgot-password
POST /api/auth/reset-password
```

### Profiles

```http
POST   /api/profiles              # Create child profile
GET    /api/profiles              # List family's profiles
GET    /api/profiles/:id          # Get specific profile
PUT    /api/profiles/:id          # Update profile
DELETE /api/profiles/:id          # Delete profile

POST   /api/families              # Create family
GET    /api/families/me           # Get current user's family
PUT    /api/families/:id          # Update family
POST   /api/families/:id/ics      # Upload ICS calendar
```

### Catalog

```http
GET /api/catalog/activities
  ?category=soccer
  &ageMin=6
  &ageMax=8
  &lat=37.7749
  &lon=-122.4194
  &radius=10
  &page=1
  &limit=20

GET /api/catalog/coverage
  ?category=soccer
  &lat=37.7749
  &lon=-122.4194
  &radius=10
  
Response: {
  "count": 47,
  "last_refresh": "2025-11-03T09:00:00Z",
  "freshness_rate": 0.96
}

GET /api/catalog/categories
Response: ["soccer", "swim", "theater", ...]
```

### Recommendations

```http
GET /api/recommendations
  ?profileId=uuid
  &options=3
  
Response: {
  "primary": { activity_id, score, explanation, ... },
  "budget_saver": { ... },
  "stretch": { ... }
}

POST /api/recommendations/feedback
Body: {
  "profile_id": "uuid",
  "activity_id": "uuid",
  "feedback_type": "thumbs_up" | "thumbs_down" | "contacted",
  "note": "optional text"
}
```

### Constraint Solver

```http
POST /api/solve
Body: {
  "family_id": "uuid",
  "child_ids": ["uuid1", "uuid2"],
  "constraints": {
    "max_budget_monthly": 300,
    "max_activities_per_child": 2
  }
}

Response: {
  "feasible": true | false,
  "plan": {
    "child_id_1": ["activity_id_1", "activity_id_2"],
    "child_id_2": ["activity_id_3"]
  },
  "total_cost_monthly": 275.50,
  "relaxation_suggestions": null | [
    {"type": "increase_budget", "to": 350, "enables": ["activity_id"]},
    {"type": "expand_radius", "to": 15, "enables": ["activity_id"]}
  ]
}
```

### LLM Q&A (Beta)

```http
POST /api/llm/ask
Body: {
  "profile_id": "uuid",
  "question": "Is this good for shy kids?",
  "context": {
    "activity_ids": ["uuid1", "uuid2"]
  }
}

Response: {
  "answer": "Based on the activities...",
  "citations": ["uuid1"],
  "helpful": null  # User feedback later
}

POST /api/llm/feedback
Body: {
  "question_id": "uuid",
  "helpful": true | false,
  "note": "optional"
}
```

### Radar & Alerts

```http
GET /api/radar/:familyId
Response: {
  "deadlines": [
    {"activity_id": "uuid", "deadline": "2025-11-08", "type": "signup"}
  ],
  "new_matches": [
    {"activity_id": "uuid", "reason": "new_provider"}
  ],
  "scholarships": [
    {"activity_id": "uuid", "deadline": "2025-11-11"}
  ]
}

POST /api/radar/digest/send  # Triggered by cron
```

### Partner Sharing

```http
POST /api/share/:familyId
Response: {
  "share_url": "https://compass.app/share/abc123xyz",
  "expires_at": "2025-12-04T00:00:00Z"
}

GET /api/share/:token
Response: {
  "family_id": "uuid",
  "recommendations": [...],
  "partner_votes": {...}
}

POST /api/share/:token/input
Body: {
  "activity_id": "uuid",
  "vote": "up" | "down",
  "note": "Looks good but schedule conflicts"
}
```

### Reports

```http
POST /api/reports
Body: {
  "activity_id": "uuid",
  "reason": "wrong_dates" | "wrong_price" | "canceled" | "safety" | "other",
  "note": "optional details"
}

Response: {
  "report_id": "uuid",
  "hidden_for_user": true
}
```

### Metrics (Internal)

```http
GET /api/metrics/cockpit
Response: {
  "catalog": {
    "coverage": {"soccer": 47, "swim": 32, ...},
    "freshness": 0.96,
    "broken_links": 0.03
  },
  "users": {
    "acceptance_rate": 0.22,
    "continue_30_rate": 0.73,
    "decision_latency_p50": 2.4
  },
  "learning": {
    "bandits_enabled": true,
    "exploration_rate": 0.08,
    "reward_delta": 0.12
  },
  "costs": {
    "llm_spend_week": 47.00,
    "llm_usage_rate": 0.14,
    "llm_thumbs_up_rate": 0.68
  },
  "reports_queue": 3
}
```

---

## 5. Catalog Ingestion Pipeline

### Scraper Architecture

```python
# Base scraper interface
class BaseScraper:
    def __init__(self, source_config: dict):
        self.scraper_id = source_config['id']
        self.source_url = source_config['url']
        self.scraper_type = source_config['type']  # ics, rss, json, html
        
    async def fetch(self) -> List[RawActivity]:
        """Fetch raw data from source"""
        pass
    
    async def parse(self, raw_data: bytes) -> List[ActivityDict]:
        """Parse into structured format"""
        pass
    
    async def validate(self, activities: List[ActivityDict]) -> ValidationResult:
        """Run quality checks"""
        pass
```

### Scraper Types

#### ICS/iCal Scraper
```python
class ICScraper(BaseScraper):
    async def parse(self, raw_data: bytes) -> List[ActivityDict]:
        cal = icalendar.Calendar.from_ical(raw_data)
        activities = []
        for event in cal.walk('VEVENT'):
            activity = {
                'name': str(event.get('SUMMARY')),
                'description': str(event.get('DESCRIPTION', '')),
                'schedule_rrule': self._extract_rrule(event),
                'venue': self._parse_location(event.get('LOCATION')),
                # ... more fields
            }
            activities.append(activity)
        return activities
    
    def _extract_rrule(self, event) -> str:
        dtstart = event.get('DTSTART').dt
        rrule = event.get('RRULE')
        # Format as RFC 5545 string
        return f"DTSTART:{dtstart.isoformat()}\nRRULE:{rrule.to_ical()}"
```

#### RSS Feed Scraper
```python
class RSSScraper(BaseScraper):
    async def parse(self, raw_data: bytes) -> List[ActivityDict]:
        feed = feedparser.parse(raw_data)
        activities = []
        for entry in feed.entries:
            activity = {
                'name': entry.title,
                'description': entry.summary,
                'source_url': entry.link,
                'schedule_rrule': self._extract_from_description(entry),
                # ... more fields
            }
            activities.append(activity)
        return activities
```

#### HTML Table Scraper
```python
class HTMLTableScraper(BaseScraper):
    def __init__(self, source_config: dict):
        super().__init__(source_config)
        self.table_selector = source_config['selectors']['table']
        
    async def parse(self, raw_data: bytes) -> List[ActivityDict]:
        soup = BeautifulSoup(raw_data, 'html.parser')
        table = soup.select_one(self.table_selector)
        activities = []
        
        for row in table.find_all('tr')[1:]:  # Skip header
            cols = row.find_all('td')
            activity = {
                'name': cols[0].text.strip(),
                'age_range': self._parse_age(cols[1].text),
                'schedule': self._parse_schedule(cols[2].text),
                'price': self._parse_price(cols[3].text),
                # ... more fields
            }
            activities.append(activity)
        return activities
```

### De-duplication Engine

```python
def compute_canon_hash(activity: ActivityDict) -> str:
    """
    Generate canonical hash for de-duplication
    
    Hash components:
    - Normalized name (lowercase, no punctuation)
    - Fuzzy date (±3 days)
    - Venue geohash6 (~1km)
    - Provider org name
    """
    norm_name = normalize_name(activity['name'])
    fuzzy_date = fuzzy_round_date(activity['start_date'], days=3)
    geo = geohash.encode(activity['venue']['lat'], 
                         activity['venue']['lon'], 
                         precision=6)
    org = activity['provider']['name'].lower()
    
    hash_input = f"{norm_name}|{fuzzy_date}|{geo}|{org}"
    return hashlib.sha256(hash_input.encode()).hexdigest()

def deduplicate(activities: List[Activity]) -> List[Activity]:
    """
    Group by canon_hash, pick best entry using Levenshtein
    """
    groups = defaultdict(list)
    for act in activities:
        groups[act.canon_hash].append(act)
    
    canonical = []
    for hash_key, group in groups.items():
        if len(group) == 1:
            canonical.append(group[0])
        else:
            # Pick entry with longest description (more complete)
            # Or use Levenshtein to find most common form
            best = max(group, key=lambda a: len(a.description))
            canonical.append(best)
    
    return canonical
```

### Quality Validation

```python
def validate_activity(activity: ActivityDict) -> ValidationResult:
    """
    Run quality checks on activity data
    
    Returns: ValidationResult with pass/fail + issues
    """
    checks = []
    
    # HTTP 200 check
    try:
        resp = requests.head(activity['source_url'], timeout=5)
        checks.append(('http_200', resp.status_code == 200))
    except:
        checks.append(('http_200', False))
    
    # Future date check
    start_date = parse_date(activity['start_date'])
    checks.append(('future_date', start_date > datetime.now()))
    
    # Price format check
    price_valid = re.match(r'^\$?\d+(\.\d{2})?$', activity['price'])
    checks.append(('price_format', bool(price_valid)))
    
    # Geocoding check
    try:
        lat, lon = geocode_address(activity['venue']['address'])
        checks.append(('geocode', lat is not None))
    except:
        checks.append(('geocode', False))
    
    # Age sanity check
    age_min = activity.get('age_min', 0)
    age_max = activity.get('age_max', 100)
    checks.append(('age_sane', 2 <= age_min < age_max <= 18))
    
    # Required fields check
    required = ['name', 'category', 'age_min', 'age_max', 'venue', 'schedule']
    missing = [f for f in required if not activity.get(f)]
    checks.append(('required_fields', len(missing) == 0))
    
    # Result
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    return ValidationResult(
        passed=passed >= total - 1,  # Allow 1 failure
        pass_rate=passed / total,
        issues=[name for name, result in checks if not result]
    )
```

### Scraper Orchestration

```python
# Celery task
@celery.task
async def run_scraper_cycle():
    """
    Runs every 72 hours via cron
    """
    source_configs = load_source_configs()  # From YAML
    
    for config in source_configs:
        scraper = create_scraper(config)
        
        try:
            # Fetch
            raw_data = await scraper.fetch()
            
            # Parse
            activities = await scraper.parse(raw_data)
            
            # Validate
            valid_activities = []
            flagged = []
            
            for act in activities:
                result = validate_activity(act)
                if result.passed:
                    valid_activities.append(act)
                else:
                    flagged.append((act, result.issues))
            
            # De-duplicate
            canonical = deduplicate(valid_activities)
            
            # Compute canon hashes
            for act in canonical:
                act['canon_hash'] = compute_canon_hash(act)
            
            # Upsert to database
            for act in canonical:
                await upsert_activity(act, scraper.scraper_id)
            
            # Log results
            await log_scraper_run(
                scraper_id=scraper.scraper_id,
                source_url=scraper.source_url,
                items_found=len(activities),
                items_created=count_new,
                items_updated=count_updated,
                items_flagged=len(flagged),
                pass_rate=len(valid_activities) / len(activities)
            )
            
            # Auto-demote source if quality drops
            if pass_rate < 0.85:
                await flag_source_quality(scraper.scraper_id)
            
        except Exception as e:
            logger.error(f"Scraper {scraper.scraper_id} failed: {e}")
            await log_scraper_error(scraper.scraper_id, str(e))
```

---

## 6. Recommendation Engine

### Scoring Function

```python
def score_activity(activity: Activity, 
                   child: ChildProfile,
                   family: Family) -> ScoredActivity:
    """
    Weighted scoring: Fit 50% + Practical 30% + Goals 20%
    """
    # Fit features (50%)
    fit_score = (
        age_band_match(activity, child) * 0.15 +
        intensity_match(activity, child) * 0.10 +
        sensory_match(activity, child) * 0.10 +
        team_solo_match(activity, child) * 0.05 +
        prerequisites_match(activity, child) * 0.05 +
        neurodiversity_fit(activity, child) * 0.05  # NEW
    )
    
    # Practical features (30%)
    commute = compute_commute_time(activity.venue, family)
    schedule = schedule_fit_score(activity, child)
    price_norm = normalize_price_to_monthly(activity.money)
    
    practical_score = (
        commute_score(commute, child.driving_radius_km) * 0.10 +
        schedule * 0.10 +
        price_score(price_norm, child.budget_per_month) * 0.05 +
        scholarship_bonus(activity, child) * 0.025 +
        transit_bonus(activity, family) * 0.025  # NEW
    )
    
    # Goals alignment (20%)
    goals_score = sum(
        goal_weight * goal_match(activity, goal)
        for goal, goal_weight in zip(child.goals, [0.10, 0.06, 0.04])
    )
    
    # Total score
    total = fit_score + practical_score + goals_score
    
    # Apply contextual bandit adjustment (if enabled)
    if BANDITS_ENABLED:
        total = apply_bandit_adjustment(total, activity, child)
    
    return ScoredActivity(
        activity=activity,
        score=total,
        components={
            'fit': fit_score,
            'practical': practical_score,
            'goals': goals_score
        }
    )

def age_band_match(activity: Activity, child: ChildProfile) -> float:
    """Score 1.0 if exact match, 0.7 if adjacent, 0.0 if out of range"""
    if activity.age_min <= child.age <= activity.age_max:
        return 1.0
    elif activity.age_min - 2 <= child.age <= activity.age_max + 2:
        return 0.7
    else:
        return 0.0

def neurodiversity_fit(activity: Activity, child: ChildProfile) -> float:
    """Bonus if activity matches neurodiversity flags"""
    child_flags = child.temperament.get('neurodiversity_flags', [])
    if not child_flags:
        return 0.0
    
    activity_flags = activity.attributes.get('neurodiversity_friendly', [])
    overlap = set(child_flags) & set(activity_flags)
    
    return len(overlap) / len(child_flags)  # 0.0 to 1.0
```

### Recommendation Generation

```python
async def generate_recommendations(
    profile: ChildProfile,
    family: Family,
    count: int = 3
) -> RecommendationSet:
    """
    Generate Primary / Budget-Saver / Stretch recommendations
    """
    # Get candidate activities
    candidates = await get_candidate_activities(
        category=None,  # All categories or filtered
        age_min=profile.age - 2,
        age_max=profile.age + 2,
        geo_point=family.geo_block_centroid,
        radius_km=profile.driving_radius_km,
        is_recommendable=True
    )
    
    # Score all candidates
    scored = [
        score_activity(act, profile, family)
        for act in candidates
    ]
    
    # Sort by score
    scored.sort(key=lambda x: x.score, reverse=True)
    
    # Select Primary (highest score)
    primary = scored[0]
    
    # Select Budget-Saver (lowest cost in top 20%)
    top_20 = scored[:int(len(scored) * 0.2)]
    budget_saver = min(
        top_20,
        key=lambda x: normalize_price_to_monthly(x.activity.money)
    )
    
    # Select Stretch (highest score > budget)
    budget_limit = profile.budget_per_month
    stretch_candidates = [
        s for s in scored
        if normalize_price_to_monthly(s.activity.money) > budget_limit * 1.2
    ]
    stretch = stretch_candidates[0] if stretch_candidates else scored[1]
    
    # Generate explanations
    primary_exp = generate_explanation(primary, profile, family)
    budget_exp = generate_explanation(budget_saver, profile, family)
    stretch_exp = generate_explanation(stretch, profile, family)
    
    return RecommendationSet(
        primary=(primary.activity, primary_exp),
        budget_saver=(budget_saver.activity, budget_exp),
        stretch=(stretch.activity, stretch_exp)
    )
```

### Explanation Template

```python
def generate_explanation(
    scored: ScoredActivity,
    profile: ChildProfile,
    family: Family
) -> Explanation:
    """
    Generate deterministic explanation (no LLM)
    """
    activity = scored.activity
    components = scored.components
    
    bullets = []
    
    # Age appropriateness
    bullets.append(
        f"Age-appropriate: For {activity.age_min}-{activity.age_max} year olds"
    )
    
    # Schedule match
    if components['practical'] > 0.15:
        schedule = parse_rrule(activity.schedule_rrule)
        bullets.append(
            f"Schedule match: {schedule['days']} {schedule['times']} fits your availability"
        )
    
    # Intensity/sensory
    intensity = activity.attributes.get('intensity', 'medium')
    child_pref = profile.temperament.get('energy', 'medium')
    if intensity == child_pref:
        bullets.append(
            f"{intensity.capitalize()} energy: Matches '{child_pref}' preference"
        )
    
    # Budget
    price_monthly = normalize_price_to_monthly(activity.money)
    if price_monthly <= profile.budget_per_month:
        bullets.append(
            f"Budget-friendly: ${price_monthly:.0f}/mo (within your ${profile.budget_per_month}/mo limit)"
        )
    
    # Distance
    commute = compute_commute_time(activity.venue, family)
    bullets.append(
        f"Close by: {commute['distance_km']:.1f} km ({commute['drive_min']:.0f} min drive)"
    )
    
    # Neurodiversity
    if profile.temperament.get('neurodiversity_flags'):
        ndf = activity.attributes.get('neurodiversity_friendly', [])
        if ndf:
            bullets.append(
                f"Neurodiversity-friendly: {', '.join(ndf)}"
            )
    
    # Transit
    if family.car_light_preference and activity.venue.transit_accessible:
        bullets.append("Transit-accessible: Reachable by public transport")
    
    # Scholarship
    if activity.scholarships_available:
        bullets.append(
            f"Scholarship available: Apply by {activity.signup_deadline.strftime('%b %d')}"
        )
    
    # Tradeoffs
    tradeoffs = []
    
    if price_monthly > profile.budget_per_month * 0.8:
        alt = find_cheaper_alternative(activity, profile)
        if alt:
            tradeoffs.append(
                f"If budget → ${profile.budget_per_month * 0.7:.0f}/mo → Would recommend {alt.name}"
            )
    
    if commute['drive_min'] > 15:
        nearby = count_activities_within(family, 10)
        tradeoffs.append(
            f"If closer → Within 10 km → {nearby} more options available"
        )
    
    return Explanation(
        bullets=bullets[:5],  # Max 5
        tradeoffs=tradeoffs[:3],  # Max 3
        confidence=scored.score,
        confidence_label=confidence_label(scored.score),
        last_verified=activity.last_verified
    )

def confidence_label(score: float) -> str:
    if score >= 0.8:
        return "Excellent fit"
    elif score >= 0.6:
        return "Good fit"
    elif score >= 0.4:
        return "Moderate fit"
    else:
        return "Possible fit"
```

---

## 7. Constraint Solver

### Problem Formulation

```python
from ortools.sat.python import cp_model

def solve_family_schedule(
    family: Family,
    child_profiles: List[ChildProfile],
    max_activities_per_child: int = 2,
    max_budget_total: float = None
) -> SolverResult:
    """
    CP-SAT constraint satisfaction problem
    
    Decision variables:
    - x[child, activity] ∈ {0, 1}  # binary: child assigned to activity
    
    Constraints:
    - Each child gets <= max_activities_per_child activities
    - No schedule conflicts (time windows + imported ICS)
    - Total cost <= max_budget_total
    - Commute within radius for each child
    
    Objective:
    - Maximize sum of scores
    """
    model = cp_model.CpModel()
    
    # Get candidate activities for each child
    candidates = {}
    for child in child_profiles:
        candidates[child.id] = get_candidate_activities(
            age_min=child.age - 1,
            age_max=child.age + 1,
            geo=family.geo_block_centroid,
            radius=child.driving_radius_km
        )
    
    # Decision variables: x[child_id, activity_id]
    x = {}
    for child_id, activities in candidates.items():
        for activity in activities:
            var_name = f"x_{child_id}_{activity.id}"
            x[(child_id, activity.id)] = model.NewBoolVar(var_name)
    
    # Constraint: Max activities per child
    for child in child_profiles:
        child_vars = [
            x[(child.id, act.id)]
            for act in candidates[child.id]
        ]
        model.Add(sum(child_vars) <= max_activities_per_child)
    
    # Constraint: No schedule conflicts within child
    for child in child_profiles:
        for i, act1 in enumerate(candidates[child.id]):
            for act2 in candidates[child.id][i+1:]:
                if schedules_conflict(act1, act2, child):
                    # Can't assign both
                    model.Add(
                        x[(child.id, act1.id)] + x[(child.id, act2.id)] <= 1
                    )
    
    # Constraint: Budget
    if max_budget_total:
        cost_vars = []
        for child_id, activities in candidates.items():
            for activity in activities:
                cost = int(normalize_price_to_monthly(activity.money) * 100)  # cents
                cost_vars.append(x[(child_id, activity.id)] * cost)
        
        model.Add(sum(cost_vars) <= int(max_budget_total * 100))
    
    # Objective: Maximize total score
    score_vars = []
    for child in child_profiles:
        for activity in candidates[child.id]:
            score = score_activity(activity, child, family).score
            # Scale to integer (CP-SAT requires integers)
            score_int = int(score * 1000)
            score_vars.append(x[(child.id, activity.id)] * score_int)
    
    model.Maximize(sum(score_vars))
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0  # 10 sec timeout
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract solution
        plan = {}
        for child in child_profiles:
            assigned = []
            for activity in candidates[child.id]:
                if solver.Value(x[(child.id, activity.id)]) == 1:
                    assigned.append(activity.id)
            plan[child.id] = assigned
        
        total_cost = sum(
            normalize_price_to_monthly(
                Activity.get(act_id).money
            )
            for acts in plan.values()
            for act_id in acts
        )
        
        return SolverResult(
            feasible=True,
            plan=plan,
            total_cost_monthly=total_cost,
            relaxation_suggestions=None
        )
    
    else:
        # Infeasible - generate relaxation suggestions
        suggestions = diagnose_infeasibility(
            model, x, child_profiles, candidates, max_budget_total
        )
        
        return SolverResult(
            feasible=False,
            plan=None,
            total_cost_monthly=None,
            relaxation_suggestions=suggestions
        )

def schedules_conflict(act1: Activity, act2: Activity, child: ChildProfile) -> bool:
    """
    Check if two activities have schedule conflict
    
    Parse RRULE and check for overlapping time blocks
    """
    rrule1 = parse_rrule(act1.schedule_rrule)
    rrule2 = parse_rrule(act2.schedule_rrule)
    
    # Check day overlap
    days1 = set(rrule1['days'])  # e.g., {'TU', 'TH'}
    days2 = set(rrule2['days'])
    
    if not days1 & days2:
        return False  # No overlapping days
    
    # Check time overlap on overlapping days
    for day in days1 & days2:
        time1 = rrule1['times'][day]  # (start, end) tuples
        time2 = rrule2['times'][day]
        
        if times_overlap(time1, time2):
            return True
    
    # Also check against imported ICS commitments
    imported = parse_imported_ics(child.family.imported_calendar_ics)
    for commitment in imported:
        if schedules_overlap(rrule1, commitment) or schedules_overlap(rrule2, commitment):
            return True
    
    return False

def diagnose_infeasibility(
    model, x, child_profiles, candidates, max_budget
) -> List[RelaxationSuggestion]:
    """
    Try relaxing constraints one at a time to find what enables feasibility
    """
    suggestions = []
    
    # Try increasing budget
    if max_budget:
        for increase in [50, 100, 150]:
            new_budget = max_budget + increase
            # Re-solve with new budget
            feasible = test_solver_with_budget(
                model.Clone(), x, child_profiles, candidates, new_budget
            )
            if feasible:
                suggestions.append(
                    RelaxationSuggestion(
                        type='increase_budget',
                        to=new_budget,
                        enables=feasible.plan
                    )
                )
                break
    
    # Try expanding radius
    for child in child_profiles:
        for increase in [5, 10, 15]:
            new_radius = child.driving_radius_km + increase
            # Re-fetch candidates with new radius
            new_candidates = get_candidate_activities(
                age_min=child.age - 1,
                age_max=child.age + 1,
                geo=child.family.geo_block_centroid,
                radius=new_radius
            )
            count_new = len(new_candidates) - len(candidates[child.id])
            
            if count_new > 0:
                suggestions.append(
                    RelaxationSuggestion(
                        type='expand_radius',
                        child_id=child.id,
                        to=new_radius,
                        enables=f"{count_new} more options"
                    )
                )
                break
    
    # Try adding time windows
    for child in child_profiles:
        # Identify common activity times not in child's windows
        popular_times = get_popular_activity_times(child.family.geo_block_centroid)
        missing = set(popular_times) - set(child.schedule_windows)
        
        if missing:
            suggestions.append(
                RelaxationSuggestion(
                    type='add_time_window',
                    child_id=child.id,
                    windows=list(missing)[:2]  # Suggest top 2
                )
            )
    
    return suggestions
```

---

## 8. Frontend Architecture

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── intake/
│   │   │   ├── ChildBasics.tsx
│   │   │   ├── Goals.tsx
│   │   │   ├── Temperament.tsx
│   │   │   ├── Constraints.tsx
│   │   │   └── ICSImport.tsx
│   │   ├── recommendations/
│   │   │   ├── RecommendationCard.tsx
│   │   │   ├── ExplanationBullets.tsx
│   │   │   ├── TradeoffSection.tsx
│   │   │   └── ReportButton.tsx
│   │   ├── solver/
│   │   │   ├── InfeasibleView.tsx
│   │   │   └── RelaxerButtons.tsx
│   │   ├── partner/
│   │   │   ├── ShareLink.tsx
│   │   │   └── PartnerView.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       └── Loading.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Intake.tsx
│   │   ├── Recommendations.tsx
│   │   ├── Profile.tsx
│   │   ├── Radar.tsx
│   │   └── Share.tsx
│   ├── hooks/
│   │   ├── useProfile.ts
│   │   ├── useRecommendations.ts
│   │   ├── useSolver.ts
│   │   └── useAuth.ts
│   ├── store/
│   │   ├── authStore.ts
│   │   ├── profileStore.ts
│   │   └── uiStore.ts
│   ├── services/
│   │   └── api.ts
│   ├── utils/
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   └── ics.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
│   ├── manifest.json
│   └── robots.txt
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### State Management (Zustand)

```typescript
// store/profileStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ProfileState {
  family: Family | null;
  children: ChildProfile[];
  currentChild: ChildProfile | null;
  
  setFamily: (family: Family) => void;
  addChild: (child: ChildProfile) => void;
  updateChild: (id: string, updates: Partial<ChildProfile>) => void;
  deleteChild: (id: string) => void;
  setCurrentChild: (child: ChildProfile) => void;
}

export const useProfileStore = create<ProfileState>()(
  persist(
    (set) => ({
      family: null,
      children: [],
      currentChild: null,
      
      setFamily: (family) => set({ family }),
      
      addChild: (child) =>
        set((state) => ({
          children: [...state.children, child],
          currentChild: child
        })),
      
      updateChild: (id, updates) =>
        set((state) => ({
          children: state.children.map((c) =>
            c.id === id ? { ...c, ...updates } : c
          )
        })),
      
      deleteChild: (id) =>
        set((state) => ({
          children: state.children.filter((c) => c.id !== id),
          currentChild: state.currentChild?.id === id ? null : state.currentChild
        })),
      
      setCurrentChild: (child) => set({ currentChild: child })
    }),
    { name: 'compass-profile' }
  )
);
```

### API Client

```typescript
// services/api.ts
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add auth token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle 401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try refresh token
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry original request
        error.config.headers.Authorization = `Bearer ${refreshed}`;
        return api.request(error.config);
      } else {
        // Logout
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// Typed API methods
export const profileAPI = {
  list: () => api.get<ChildProfile[]>('/profiles'),
  get: (id: string) => api.get<ChildProfile>(`/profiles/${id}`),
  create: (data: CreateProfileDTO) => api.post<ChildProfile>('/profiles', data),
  update: (id: string, data: UpdateProfileDTO) => 
    api.put<ChildProfile>(`/profiles/${id}`, data),
  delete: (id: string) => api.delete(`/profiles/${id}`)
};

export const recommendationsAPI = {
  get: (profileId: string, options?: { count?: number }) =>
    api.get<RecommendationSet>(`/recommendations?profileId=${profileId}`, {
      params: options
    }),
  
  feedback: (data: FeedbackDTO) =>
    api.post('/recommendations/feedback', data)
};

export const solverAPI = {
  solve: (data: SolverRequest) =>
    api.post<SolverResult>('/solve', data)
};
```

### Key Components

```typescript
// components/recommendations/RecommendationCard.tsx
import { Activity, Explanation } from '@/types';
import { formatPrice, formatDistance } from '@/utils/formatting';

interface Props {
  activity: Activity;
  explanation: Explanation;
  type: 'primary' | 'budget_saver' | 'stretch';
  onReport: () => void;
  onFeedback: (type: 'up' | 'down') => void;
}

export function RecommendationCard({
  activity,
  explanation,
  type,
  onReport,
  onFeedback
}: Props) {
  const iconMap = {
    primary: '🥇',
    budget_saver: '💰',
    stretch: '⭐'
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">{iconMap[type]}</span>
        <span className="text-sm uppercase font-semibold text-gray-500">
          {type.replace('_', ' ')}
        </span>
      </div>
      
      {/* Activity info */}
      <h3 className="text-xl font-bold mb-1">{activity.name}</h3>
      <p className="text-gray-600 mb-4">
        {formatPrice(activity.money)} • {activity.category}
      </p>
      
      {/* Explanation bullets */}
      <div className="space-y-2 mb-4">
        <p className="font-semibold text-sm">Why this fits:</p>
        <ul className="space-y-1">
          {explanation.bullets.map((bullet, i) => (
            <li key={i} className="text-sm flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>{bullet}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Confidence & verification */}
      <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
        <span>
          Confidence: {(explanation.confidence * 100).toFixed(0)}% 
          ({explanation.confidence_label})
        </span>
        <span>
          Last verified: {new Date(explanation.last_verified).toLocaleDateString()}
        </span>
      </div>
      
      {/* Tradeoffs */}
      {explanation.tradeoffs.length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 rounded">
          <p className="font-semibold text-sm mb-2">What would change this?</p>
          <ul className="space-y-1 text-sm">
            {explanation.tradeoffs.map((trade, i) => (
              <li key={i}>• {trade}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Actions */}
      <div className="flex gap-2">
        <button className="btn-primary flex-1">
          Open Signup
        </button>
        <button className="btn-secondary">
          Add to Calendar
        </button>
      </div>
      
      {/* Feedback */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t">
        <div className="flex gap-2">
          <button
            onClick={() => onFeedback('up')}
            className="p-2 hover:bg-gray-100 rounded"
          >
            👍
          </button>
          <button
            onClick={() => onFeedback('down')}
            className="p-2 hover:bg-gray-100 rounded"
          >
            👎
          </button>
        </div>
        
        <button
          onClick={onReport}
          className="text-sm text-red-600 hover:underline"
        >
          ⚠️ Report inaccurate info
        </button>
      </div>
    </div>
  );
}
```

---

## 9. Deployment & Infrastructure

### Environment Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: compass
      POSTGRES_USER: compass
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      DATABASE_URL: postgresql://compass:${DB_PASSWORD}@postgres:5432/compass
      REDIS_URL: redis://redis:6379/0
      QDRANT_URL: http://qdrant:6333
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
      - qdrant
  
  celery_worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://compass:${DB_PASSWORD}@postgres:5432/compass
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - backend
  
  celery_beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://compass:${DB_PASSWORD}@postgres:5432/compass
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - backend

volumes:
  postgres_data:
  qdrant_data:
```

### Production Deployment

**Backend (Railway/Fly.io):**
```bash
# Railway
railway init
railway up

# Fly.io
fly launch
fly deploy
```

**Frontend (Vercel):**
```bash
vercel --prod
```

**Database:**
- PostgreSQL: Railway/Neon/Supabase
- Redis: Upstash Redis
- Object Storage: Cloudflare R2 / AWS S3

**Monitoring:**
- Sentry for error tracking
- Plausible for privacy-friendly analytics
- Uptime monitoring: Better Uptime / Checkly

---

## 10. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Backend:**
- [ ] Project setup (FastAPI, SQLAlchemy, Alembic)
- [ ] Database schema creation
- [ ] Authentication (JWT, registration, login)
- [ ] Profile CRUD APIs
- [ ] Basic catalog API (mock data initially)

**Frontend:**
- [ ] Project setup (Vite + React + TypeScript)
- [ ] Routing & navigation
- [ ] Authentication flow (login/register)
- [ ] Intake form (child profile creation)
- [ ] Basic UI components library

**Deliverable:** Working auth + profile management

---

### Phase 2: Catalog Pipeline (Week 3-4)

**Backend:**
- [ ] Scraper framework (base classes)
- [ ] ICS scraper implementation
- [ ] HTML table scraper implementation
- [ ] De-duplication engine
- [ ] Quality validation
- [ ] Celery setup for async tasks
- [ ] Scraper orchestration job

**Data:**
- [ ] Source config YAML
- [ ] Initial scrape of 2-3 test sources
- [ ] Venues table population

**Deliverable:** Automated catalog with real data

---

### Phase 3: Recommendations & Solver (Week 5-6)

**Backend:**
- [ ] Scoring function implementation
- [ ] Recommendation generation
- [ ] Explanation template rendering
- [ ] CP-SAT constraint solver
- [ ] Infeasibility diagnosis
- [ ] Recommendation APIs

**Frontend:**
- [ ] Recommendation cards
- [ ] Explanation display
- [ ] Solver infeasible view with relaxers
- [ ] Feedback buttons (thumbs, report)

**Deliverable:** End-to-end recommendation flow

---

### Phase 4: Features & Polish (Week 7-8)

**Backend:**
- [ ] Partner sharing (token generation, partner view API)
- [ ] Radar digest generation
- [ ] Email integration (SendGrid)
- [ ] ICS import parser
- [ ] Report handling
- [ ] Metrics dashboard API

**Frontend:**
- [ ] Partner share flow
- [ ] Radar digest view
- [ ] ICS import UI
- [ ] Report modal
- [ ] Coverage meter display
- [ ] PWA setup (service worker, manifest)

**DevOps:**
- [ ] Production deployment
- [ ] CI/CD pipeline
- [ ] Monitoring setup

**Deliverable:** MVP ready for pilot launch

---

## Next Steps

1. Review and approve this technical specification
2. Set up development environment (see Phase 1)
3. Create GitHub repository with project structure
4. Begin Phase 1 implementation
5. Weekly check-ins to track progress

---

**Document Version:** 1.0  
**Last Updated:** November 04, 2025  
**Status:** Ready for Implementation
