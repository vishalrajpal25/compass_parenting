# Activity Sources - Quick Reference

**Quick scan of all sources where parents search for activities, sorted by feasibility**

---

## 🟢 HIGH FEASIBILITY (Start Here)

| Source Type | Examples | Format | Coverage | Effort | Maintenance |
|------------|----------|--------|----------|--------|-------------|
| **City Rec Departments** | SF Parks & Rec, NYC Parks | ICS/CSV/JSON/HTML | Local | Low | Low |
| **Public Libraries** | County library systems | ICS/RSS | Local | Low | Low |
| **YMCA Branches** | YMCA of [Metro] | JSON/HTML/ICS | Regional | Medium | Medium |
| **Community Centers** | JCCs, Boys & Girls Clubs | ICS/RSS/JSON | Local | Medium | Medium |
| **Youth Sports Orgs** | AYSO, Little League, Scouts | HTML (chapter pages) | National→Local | Medium | Medium-High |
| **Eventbrite** | Eventbrite.com | API/HTML | Global | Low | Low |
| **Eventful/Songkick** | Eventful.com | API | Global | Low | Low |
| **Meetup** | Meetup.com | API (OAuth) | Global | Medium | Medium |
| **Facebook Events** | Public events | Graph API | Global | Medium | Medium |
| **ParentMap** | ParentMap.com | HTML/RSS | Seattle+ | Medium | Low-Medium |
| **City Open Data** | DataSF, NYC Open Data | JSON/CSV APIs | Local | Low | Low |

---

## 🟡 MEDIUM FEASIBILITY

| Source Type | Examples | Format | Coverage | Effort | Maintenance |
|------------|----------|--------|----------|--------|-------------|
| **Macaroni Kid** | 500+ franchises | HTML (varies) | 500+ US locations | High | High |
| **Red Tricycle** | RedTricycle.com | HTML | Major metros | Medium | Medium |
| **Mommy Poppins** | MommyPoppins.com | HTML | NYC/LA/SF/Boston | Medium | Medium |
| **Local Moms Network** | TheLocalMomsNetwork.com | HTML | Nationwide | Medium | Medium-High |
| **Upparent** | Upparent.com | HTML | Location-based | Medium | Medium |
| **Regional Mom Blogs** | Triad Moms, Denton County Moms | HTML | Regional | High | High |
| **School Districts** | Athletic calendars | ICS/CSV/HTML | Local | Medium | Medium-High |
| **Museums/Cultural** | Children's museums | ICS/HTML | Local | Medium | Medium |
| **Aquatics Facilities** | Pools, swim schools | ICS/CSV/HTML | Local | Medium | Medium |

---

## 🟠 LOW FEASIBILITY

| Source Type | Examples | Format | Coverage | Effort | Maintenance |
|------------|----------|--------|----------|--------|-------------|
| **Facebook Groups** | Public parent groups | Graph API/Scraping | Massive | High | Very High |
| **Nextdoor** | Nextdoor.com | No API | Hyper-local | N/A | N/A |
| **Reddit** | r/[city] subreddits | Reddit API | City-level | Medium | Medium |
| **Community Forums** | Local phpBB/vBulletin | HTML (varies) | Neighborhood | Very High | Very High |
| **Email Lists** | PTA listservs | Email parsing | Local | Very High | Very High |

---

## 🔴 VERY LOW FEASIBILITY (Avoid MVP)

| Source Type | Examples | Format | Coverage | Effort | Maintenance |
|------------|----------|--------|----------|--------|-------------|
| **Private Facebook Groups** | Closed groups | No access | Local | N/A | N/A |
| **WhatsApp Groups** | Neighborhood chats | No API | Hyper-local | N/A | N/A |
| **Peanut App** | Peanut app | No API | Mobile-only | N/A | N/A |
| **PDF Sources** | School brochures | PDF | Local | High | High |
| **Instagram** | Event posts | Graph API (limited) | Global | High | High |

---

## Implementation Roadmap

### ✅ Phase 1 (MVP - Weeks 1-2)
**Structured, high-value, low-maintenance**

1. City Recreation Departments
2. Public Library Systems  
3. YMCA Branches
4. Community Centers (JCCs, Boys & Girls Clubs)
5. Eventbrite API
6. City Open Data Portals

**Expected Sources:** 50-100 individual providers in one metro

---

### 📅 Phase 2 (Post-MVP)
**Medium effort, good coverage**

7. Youth Sports Organizations (AYSO, Little League, etc.)
8. Parenting websites (ParentMap, select Macaroni Kid franchises)
9. Museum & Cultural Institution calendars
10. Facebook Events API (if app approved)

**Expected Sources:** +100-200 providers

---

### 🚀 Phase 3 (Scale)
**Higher maintenance, but valuable**

11. Regional parenting networks
12. School district extracurriculars (structured only)
13. Activity marketplaces (if partnerships)

**Expected Sources:** +200-500 providers

---

## Key Metrics Per Source Type

| Source Type | Avg Sources/Metro | Pass Rate Target | Update Frequency | Maintenance Hrs/Week |
|------------|------------------|------------------|-------------------|---------------------|
| City Rec | 1-3 | 90%+ | Weekly | <0.1 |
| Libraries | 1-5 | 90%+ | Weekly | <0.1 |
| YMCA | 5-20 | 85%+ | Weekly | 0.2 |
| Community Centers | 10-30 | 85%+ | Weekly | 0.3 |
| Youth Sports | 20-50 | 80%+ | Seasonal | 0.5 |
| Eventbrite | 1 (API) | 95%+ | Daily | <0.1 |
| Parenting Sites | 5-10 | 75%+ | Daily | 0.5 |
| Facebook Events | 1 (API) | 70%+ | Real-time | 0.3 |

**Total MVP Target:** 50-100 sources, <5 hrs/week maintenance

---

## Decision Framework

**Include if:**
- ✅ Structured data (ICS/RSS/JSON/consistent HTML)
- ✅ Public access (no auth required)
- ✅ Predictable updates
- ✅ Can maintain <1 hr/week per source type
- ✅ Pass rate ≥85% achievable

**Exclude if:**
- ❌ PDF-only
- ❌ Requires authentication/partnership
- ❌ ToS violations
- ❌ Anti-bot measures too aggressive
- ❌ Format too variable
- ❌ Maintenance >1 hr/week per source type

---

## Quick Stats

- **Total Source Types Identified:** ~30
- **High Feasibility Types:** ~11
- **Medium Feasibility Types:** ~9
- **Low Feasibility Types:** ~5
- **Very Low Feasibility Types:** ~5

**Individual Sources (estimated):**
- **One Metro (Phase 1):** 50-100 sources
- **One Metro (Phase 2):** 150-300 sources
- **One Metro (Phase 3):** 350-800 sources
- **National (all phases):** 10,000+ potential sources

**Focus:** Quality over quantity. Start with structured sources in one metro, validate approach, then scale.

