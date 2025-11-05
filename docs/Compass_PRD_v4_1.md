
# Compass PRD (v4.1) — Solo-Ready, Comprehensive, Pragmatic
**Document Type:** Product Requirements Document (Solo-Adapted & Battle-Tested)  
**Version:** 4.1  
**Date:** November 04, 2025  
**Status:** Ready for Solo Engineering Kickoff

---

## Changelog (v4 → v4.1)
- Added de-dup/canonicalization, RRULE schedules, and ingestion hygiene
- Added one-tap constraint relaxers and report button
- Added neurodiversity-friendly attribute flags and car-light preference
- Added ICS import for existing family calendars (no OAuth)
- Tightened bandits: fallback switch, sparse-data guard, seeded priors
- Reduced weekly metrics to a 5-minute cockpit
- Strengthened legal/ops: DMARC/CAN-SPAM, robots/respect, safety takedown
- Added “Coverage Meter” UX and explicit source validation thresholds
- Included **Catalog Pipeline Sources** (Tier-1 structured sources + examples)
- Engineering checklists and order-of-operations updated

---

## 0) One-Page Summary
**Problem.** Parents face overwhelming, high-stakes choices around enrichment with little trustworthy guidance; directories and groups don’t optimize for schedule, budget, or fit.

**Solution.** **Compass** is a hybrid AI advisor that collects concise family signals, uses a **structured recommender** + **constraint solver** to generate a small, actionable plan, then explains *why* via deterministic templates (LLM-optional for Q&A). The moat is **automated, fresh local data**, deduped and normalized from structured public sources.

**Age of AI.** Optimization + explanation beats chat. Guardrailed LLM improves nuance without owning the decision boundary.

**Solo Reality.** Nights-and-weekends build, zero-touch ops. No manual catalog workflows. ≤ 5 hrs/week maintenance.

**Impact.** Faster, better-fit decisions; lower waste; equity via public programs/scholarships; calmer parents. Start with one metro and 4–5 reliable categories, then expand.

---

## 1) Principles (unchanged + additions)
1) Explainability by design (templates; tradeoffs; confidence).  
2) Optimization first, chat second (LLM is optional, sandboxed).  
3) Automated catalog = moat (structured sources, zero-touch).  
4) Lightweight feedback loops (Continue/Stop, thumbs, check-ins).  
5) Privacy & safety (minimal data; consent; clinical boundary).  
6) Equity aware (scholarship, commute, fairness metrics).  
7) **Solo-sustainable** (features must cost <1 hr/week to maintain).  
8) **Hygienic ingestion** (dedup, canonicalization, RRULE, validation, robots).

---

## 2) Scope of MVP (6–8 Weeks, Solo Build)
**In-scope:** Mobile PWA; rapid intake; structured recommender; **Constraint Solver v1**; deterministic explanations; **LLM Q&A (Beta, flagged)**; automated Tier-1 catalog; **partner sharing**; **weekly radar**; **calendar export + ICS import**; progress signals; **report button**; Trust Center; English-only; **coverage meter** per category.

**Out-of-scope:** Boutique studios; community; bilingual; provider portal; native apps; multi-city; real-time push; PDF parsing.

**Deferred:** Semi-auto weight tuning; ontology enrichment with HIL; bilingual; provider portal; multi-city.

---

## 3) Catalog Pipeline Sources (Tier‑1 Structured)
**Strategy:** Structured, public-good sources with predictable updates. Prefer ICS/iCal, RSS, or JSON feeds; fall back to well-formed HTML tables. No PDFs in MVP.

### Core Source Types & Examples (build as pluggable scrapers)
- **City Recreation Departments**  
  - *Data:* seasons/leagues/classes; often ICS/CSV/JSON or HTML tables  
  - *Examples:* “City of <Metro> Parks & Rec”, “Community Recreation Centers”
- **Public Library Systems**  
  - *Data:* youth events/classes; typically ICS/RSS feeds per branch or system  
  - *Examples:* “<County> Library Events Calendar”
- **YMCA Branches**  
  - *Data:* swim lessons, youth sports; sometimes JSON endpoints or structured HTML  
  - *Examples:* “YMCA of <Metro> – Programs”
- **Youth Sports Orgs (National → Local Chapters)**  
  - *AYSO (soccer), Little League (baseball), USSSA/Babe Ruth (baseball), US Youth Soccer (clubs), USA Swimming local clubs, Scouts (BSA/Girl Scouts) service units*  
  - *Data:* registration windows, age bands, locations (chapter-level pages)
- **Community & Cultural Centers**  
  - *JCCs, Boys & Girls Clubs, Parks Conservancies, Nature Centers*  
  - *Data:* classes/events; ICS/RSS; sometimes JSON calendars
- **School District Extracurriculars (when structured)**  
  - *Data:* after-school programs, clubs, sports; seek ICS/CSV athletic calendars; avoid PDFs
- **Civic Event Hubs (when structured)**  
  - *Data:* citywide event APIs or open data portals with youth tags
- **Aquatics & Rec Facilities**  
  - *Data:* lessons, open swim blocks; often ICS/CSV

**Access Modalities (priority order):**
1) ICS/iCal (RRULE-ready)  
2) RSS/Atom feeds  
3) JSON/CSV APIs or downloads  
4) HTML tables (consistent structure only)

**Validation thresholds per source:**
- Pass rate ≥ 85% (fields present, dates sane, links 200)  
- Broken-link rate ≤ 5%  
- If a source drops below thresholds for 2 consecutive runs → **auto-demote** (not “recommendable”) and alert.

**Robots/compliance:** Respect robots.txt, rate-limit; UA includes contact email; cease on request. Maintain allowlist YAML for base URLs; hard-exclude brittle JS apps or blocked paths.

---

## 4) Ingestion & Normalization (v4.1)
- **De‑dup & canonicalization:** `canon_hash = hash(normalize(name), start_date±3d, geohash6(venue), org_name)` with Levenshtein tie-break.  
- **Schedules:** Store as **RRULE** (BYDAY/BYHOUR/BYMINUTE, DTSTART).  
- **Money:** `{{amount, currency, period}}` (season/month/term). Delay normalization to $/mo until comparison time.  
- **Venues:** Separate table with geohash + timezone.  
- **Source fingerprint:** persist `source_item_id`, `source_url`, `scraper_id`.  
- **Quality checks (auto-exclude if ≥2 fail):** HTTP 200, future date, price regex, geocode ok, sane ages, required fields present.  
- **Change detection flags:** >50% field change, >30% price delta, new provider at known venue, deadline ≤7d. Weekly spot-check (≤1 hr).  
- **Freshness SLAs:** 72h re-scrape; freshness ≥95%; deadline detection ≥90%; change→flag ≤72h.

**Coverage Meter (user-facing):** “We track **47 soccer** programs in your area • **updated every 72h**.”

---

## 5) Recommendation & Solver
**Scoring:** weighted: Fit 50% (age/intensity/sensory/team/prereqs), Practical 30% (commute/schedule/price/scholarship), Goals 20% (ranked).

**Outputs:** For each child, **Primary / Budget‑Saver / Stretch** with deterministic template:
- Why it fits (3–5 bullets)  
- What would change this (budget, radius, intensity)  
- Cost impact; travel time; schedule fit  
- Confidence (0–1) label; Last verified timestamp

**Constraint Solver v1:** CP‑SAT/backtracking; inputs: windows, radius, budget, per‑child activity caps, fixed commitments.  
**Failure UX:** Show *why infeasible* + **one‑tap relaxers** (expand radius, raise budget, permit one extra time window).

**Personalization:**  
- **Phase 1 (MVP):** Contextual bandits (Thompson) behind feature flag, ε start 0.1 → decay. Seed priors by category. **Sparse guard:** if <50 accepted events lifetime → disable updates. ENV fallback `BANDITS_ENABLED=false`.  
- **Phase 2:** Semi‑auto weight tuning from aggregate signals (monthly review).

---

## 6) Explainability & LLM Q&A (Beta)
**Primary:** deterministic templates (fast, free, grounded).  
**Secondary:** **LLM Q&A** modal, Beta-labeled; RAG over catalog + profile context; citations link back to listings.  
**Guardrails:** no provider/date hallucinations; medical/clinical questions routed to resources; rate limits by plan; per‑answer token cap; response helpfulness thumbs.  
**Cost control:** cache common Qs; monitor spend; pause for Free tier if costs spike.

---

## 7) UX Highlights
- Intake ≤90s; dyslexia‑friendly font option; high‑contrast mode.  
- Rec cards with **Report** button (auto-hide for family; queues URL for weekly review).  
- Partner share: read‑only link with up/downvotes and notes; 30‑day expiry.  
- Radar: weekly digest; one‑click check‑in links (“Great / OK / Not great”).  
- **ICS import**: block off existing commitments without OAuth.  
- “Car‑light” preference; neurodiversity flags (low sensory, small group, predictable routine).

---

## 8) Safety, Privacy, Ops
- COPPA‑style consent; minimal data; geomask home addresses.  
- “Recommendations, not endorsements” disclaimer; link provider safety policies.  
- **Fast takedown:** report → hide in 24h; review ≤48h.  
- Email compliance: SPF/DKIM/DMARC; CAN‑SPAM footer (address, unsubscribe).  
- Robots.txt respected; polite crawling; cease-on-request registry.  
- Legal: we may remove listings at our discretion for safety/accuracy.

---

## 9) Metrics Cockpit (weekly, 5 minutes)
- **Catalog:** Coverage / Freshness / Broken‑link%  
- **Quality:** Acceptance% / Continue@30%  
- **UX:** Decision latency p50  
- **Learning:** Bandit exploration & reward delta (or flag off)  
- **Costs:** LLM spend & Q&A helpfulness%

---

## 10) Engineering Order‑of‑Operations (Solo)
1) **Week 1–2:** Scraper framework (ICS/RSS/JSON → HTML); schema (venues, RRULE, money); dedup; validation; coverage meter.  
2) **Week 3:** Scoring + Solver v1 + one‑tap relaxers; deterministic templates.  
3) **Week 4:** Partner share; radar digest; report button; ICS import.  
4) **Week 5:** Bandits (behind flag); telemetry; ops dashboard.  
5) **Week 6:** LLM Q&A Beta; trust center; DMARC/SPF/DKIM; pilot.

**Testing harness:** 30 synthetic families × 4 categories nightly (ingest → solve → recs).  
**Time math:** store UTC; convert to venue TZ in responses.  
**Distance:** precompute simple drive time proxy nightly; avoid hot‑path map APIs.

---

## 11) Pricing & Gating (MVP posture)
- **Free:** Radar digest, 1 full rec/child/season, Solver Lite.  
- **Essential ($9.99/mo | $79/yr):** Unlimited recs, full solver, partner share, calendar/ICS, progress tracking.  
- **Premium ($19.99/mo | $149/yr):** + LLM Q&A (unlimited), scholarship alerts, early features.  
- Gate heavy features to protect costs; pilot free for first 100 families.

---

## 12) Risks & Mitigations (delta highlights)
- **School district PDFs:** auto‑demote if validation <70%; no PDF parsing in MVP.  
- **Over‑exploration:** start ε=0.1, decay; turn off via flag if noisy.  
- **Ops overload:** any feature >1 hr/week maintenance → deprecate or automate.  
- **Scrape blocks:** favor feeds/APIs; polite rates; hard‑exclude brittle apps; cease-on-request.

---

## 13) Pipeline Source Backlog (by integration effort)
- **Low effort (start here):** ICS/iCal library events; city rec ICS/CSV; YMCA JSON/HTML tables; AYSO region pages; Boys & Girls Clubs calendars.  
- **Medium:** JCC calendars; nature centers (often ICS); aquatics facilities with CSV/HTML tables.  
- **High (post‑MVP):** School district extracurriculars if not structured; civic open data APIs needing mapping; scout councils with irregular pages.

---

## 14) What We’ll Change (Impact)
Parents decide faster with clarity; children land in better‑fit activities; public programs get filled; equity improves through scholarships and local options; a solo builder sustains a useful service with <5 hrs/week.

---

## Appendices
- **A. Data Model:** money objects, venues, RRULE schedules, source fingerprints.  
- **B. API Sketches:** Profiles, Recommendations, Solve, Radar, Telemetry, Share.  
- **C. Templates:** Rec card copy; Beta Q&A prompt & guardrails.  
- **D. Ops Checklists:** Monday/Wednesday/Friday/Sunday routines; incident flows.

---

**Compass turns chaos into a transparent, optimized plan—fast, trustworthy, and feasible for one builder to maintain.**
