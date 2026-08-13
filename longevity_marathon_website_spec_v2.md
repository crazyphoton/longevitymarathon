# Longevity Marathon

## Website Product & Build Specification — Version 2.0

**Domain:** longevitymarathon.run  
**Status:** Build-ready specification  
**Project window:** Four-month training period through the BYD Singapore Marathon 2026, plus an immediate post-race retrospective  
**Target outcome:** Complete 42.2 km in 5:00  
**Last revised:** 13 August 2026  
**Scope:** This document is the canonical build spec — information architecture, page requirements, the content/data model, the disagreement/decision framework, and exact wording (see §18 for canonical starter copy). Build against this document. `longevity_marathon_editorial_spec.md` and `design.md` are intentionally sparse companion checklists — voice/rhetoric and aesthetic/feel respectively — used for QC review, not as independent sources of structure or content.

> **The question is the product; the author is the experiment.** The site asks whether four months of marathon training makes a person measurably healthier, and documents the answer without assuming it will be positive.

---

## 1. Executive summary

Longevity Marathon is a public, evidence-aware self-experiment documenting one person's four-month preparation for the BYD Singapore Marathon 2026. The author is the protagonist and aims to finish the marathon in five hours. Dr. Varun Reddy appears as a named collaborator, sports-medicine expert, and research scientist; his exact public title and credentials must be confirmed before launch.

The editorial premise is deliberately more interesting than “watch me train.” The homepage leads with a broader question: **Does training for a marathon make you healthier?** The project follows what happens to cardiorespiratory fitness, body composition, strength, recovery, metabolic markers, and overall health while a non-expert plan collides with expert review and real life.

The health outcomes are observations, not success criteria. An increase, decrease, or neutral result is valid. The project succeeds if the author runs 42.2 km in 5:00 and documents the process rigorously enough for readers to understand what was planned, what occurred, what changed, and what can and cannot be inferred.

Version 1 of the website is a complete navigable shell. Every primary page exists at launch. Sections without sufficient content use deliberate **Coming Soon** or **Awaiting Data** states that explain what will appear and what event unlocks it. No navigation item leads to a dead end.

### 1.1 Product promise

For longevity-aware readers, Longevity Marathon turns abstract ideas such as VO₂ max, Zone 2, body composition, strength, and metabolic health into a lived story with data, mistakes, expert disagreement, and evidence. Newcomers remain welcome through progressive disclosure and concise explainers.

### 1.2 V1 in one sentence

A question-led editorial website with a journal, living training plan, marathon-progress dashboard, observational health metrics, evidence-backed expert commentary, explainers, newsletter, and honest placeholder states for data or content that does not yet exist.

---

## 2. Product principles

### 2.1 Question first, protagonist second

The first screen should make the health question irresistible before asking visitors to care about the author. The author's personality, stakes, and story then carry the reader through the experiment.

### 2.2 Rigorous, not solemn

Measurements, evidence, uncertainty, and attribution are handled carefully. The prose remains conversational, curious, occasionally irreverent, and willing to admit “that was a terrible idea.” The explanatory ambition may be inspired by the make-complex-things-understandable philosophy associated with Wait But Why, but the site must not imitate Tim Urban's voice, recurring characters, visual language, or phrasing.

### 2.3 The marathon has a target; health does not

Marathon progress is judged against 42.2 km in 5:00. Health markers are observed without directional success targets. The interface must not reward or shame health changes with premature green/red narratives.

### 2.4 The story is larger than the runs

Every run should be publishable, but the primary content object is the **Journal entry**. Entries may be run reports, reflections, doctor conversations, test updates, plan changes, injuries, gear decisions, research explainers, setbacks, or long-form essays.

### 2.5 Reality leaves a visible trail

The initial plan, subsequent revisions, actual training, and outcomes remain distinguishable. Changes are explained rather than silently overwritten. Missed sessions, abandoned workouts, injuries, poor decisions, uncertainty, and disagreement are editorial assets, not embarrassing exceptions.

### 2.6 One-person evidence is not universal evidence

The site clearly separates the author's experience, Garmin estimates, clinical measurements, Dr. Reddy's interpretation, and established research. It never presents a personal outcome as proof of a general health claim.

### 2.7 Publishable from Day 1

The newsletter works at launch. The whole site shell works at launch. Missing data is represented honestly. Advanced automation, AI-assisted writing, community interaction, and future “seasons” are not prerequisites.

---

## 3. Goals, non-goals, and success

### 3.1 Product goals

- Explain whether and how marathon training may affect healthspan-related markers through one transparent case study.
- Build an engaging narrative around four months of training, expert collaboration, adaptation, and measurement.
- Publish every run while supporting broader journal formats with equal prominence.
- Make the plan-versus-reality gap visible and useful.
- Present marathon progress and health observations clearly without overstating precision or causality.
- Give Dr. Reddy a consistent, attributable format for evidence-backed commentary.
- Make difficult fitness and longevity concepts accessible through progressive disclosure and reusable explainers.
- Convert interested readers into newsletter subscribers from Day 1 without turning the site into a capture funnel.
- Reduce publishing friction with repeatable content and visual templates.

### 3.2 Experiment hypothesis

> Can four months of training for a marathon meaningfully improve measurable healthspan and cardiorespiratory fitness without sacrificing muscle, strength, or overall health?

This is a question to investigate, not a claim to prove. The project should actively surface trade-offs and null results.

### 3.3 Project success criteria

The project is a success when:

1. The author completes the BYD Singapore Marathon 2026 in 5:00 or less.
2. The process is documented rigorously enough to reconstruct intended training, actual training, changes, decisions, and significant outcomes.
3. Health findings are reported accurately regardless of direction.
4. The immediate post-marathon retrospective is published within the project window.

If the five-hour target is missed, the site must still document the result honestly. Product quality should not depend on athletic success.

### 3.4 V1 product success indicators

- Every primary navigation destination exists and resolves.
- Visitors can understand the question, experiment, participants, target, current status, and next useful action from the homepage.
- Journal entries support multiple entry types; run entries can hold structured Garmin data.
- The living plan shows planned, revised, and actual states.
- The dashboard separates marathon progress from health observations.
- Newsletter signup is functional, consented, and confirmed.
- Placeholder states are specific and useful rather than generic empty pages.
- The publishing team can add a normal entry, run entry, plan revision, metric reading, citation, and doctor note without developer intervention.

### 3.5 Non-goals for V1

- Comments, reader questions, polls, accounts, profiles, forums, or community submissions.
- Personalized training, diagnosis, medical advice, or recommendations to readers.
- Publishing raw medical reports.
- Treating HRV as a core metric or requiring a Whoop subscription.
- AI-generated copy as an architectural dependency.
- Fully automated Garmin ingestion as a launch blocker.
- A forensic audit log of every edit or separate “happened on” and “published on” timestamps.
- Deciding whether the project continues beyond the immediate post-race retrospective.
- Making cost a primary narrative or dashboard.

---

## 4. Audience and user journeys

### 4.1 Primary audience

Longevity-aware adults who have encountered concepts such as VO₂ max, Zone 2, resistance training, metabolic health, and body composition, and want to see how those ideas behave in a real, time-bound marathon project.

They value evidence but may be skeptical of optimized influencer narratives. They are interested in trade-offs, practical application, and the gap between a clean theory and a messy life.

### 4.2 Secondary audience

- Newcomers who are interested in healthspan but do not yet understand the terminology.
- Recreational runners interested in training adaptation, mistakes, gear, injury, and expert review.
- Clinicians, researchers, and coaches interested in the communication of a one-person experiment.
- Friends, colleagues, and newsletter readers following the personal story.

### 4.3 Progressive disclosure standard

The main narrative should not be diluted into a beginner glossary. When a technical term appears:

- Give enough context in the sentence to preserve flow.
- Link the term to a concise explainer or open an inline definition.
- Offer methodology, caveats, and sources at a deeper level.
- Never require a reader to understand an acronym to follow the human story.

### 4.4 Core journeys

**First-time visitor:** Lands on the homepage → understands the question and experiment → sees current marathon status → opens the latest journal entry or experiment overview → subscribes.

**Returning follower:** Lands on homepage or newsletter link → sees what changed → reads latest journal entry → follows a referenced plan revision or metric update.

**Data-curious reader:** Opens Dashboard → reads marathon progress → explores health observations → opens methodology and related explainers → follows source-linked doctor commentary.

**Plan-curious runner:** Opens Plan → compares intended and current plan → reviews change history → opens entries explaining why a change occurred → sees actual outcome.

**Newcomer:** Encounters an unfamiliar term → uses inline definition or Explainer → returns to the originating story without losing context.

---

## 5. Information architecture and page map

### 5.1 Primary navigation

Use short, stable labels:

1. **Journal**
2. **The Experiment**
3. **The Plan**
4. **Dashboard**
5. **Explainers**
6. **About**

The logo/domain returns home. Newsletter signup appears as a visually distinct but restrained action. Labs, doctor notes, injuries, gear, and costs live as content views or subpages rather than crowding the primary navigation.

### 5.2 Complete V1 shell

| Route | Page | V1 status | Primary job |
|---|---|---|---|
| `/` | Home | Live | Sell the question, orient visitors, show status, route to current story and newsletter |
| `/journal` | Journal index | Live | Browse all editorial content, not only runs |
| `/journal/[slug]` | Journal entry | Live | Tell one part of the story with optional structured modules |
| `/experiment` | The Experiment | Live | Define question, method, measures, boundaries, and interpretation rules |
| `/plan` | The Plan | Live | Show intended plan, current version, revisions, and actual adherence |
| `/plan/versions/[id]` | Plan version | Shell/live as available | Preserve a dated plan snapshot and rationale |
| `/dashboard` | Dashboard | Live with Awaiting Data states | Foreground marathon progress and separately observe health metrics |
| `/dashboard/methodology` | Measurement methodology | Live | Explain sources, cadence, limitations, and estimate-versus-measurement status |
| `/health` | Health observations | Shell/live as available | Provide metric histories, tests, and interpretation without raw reports |
| `/health/[metric]` | Metric detail | Shell/live as available | Show one metric's readings, method, context, and commentary |
| `/explainer` | Explainers index | Live/shell | Browse evidence-aware explanations |
| `/explainer/[slug]` | Explainer | Shell/live as available | Explain a concept at multiple depths with sources |
| `/collaborators/dr-varun-reddy` | Dr. Reddy profile | Live after credential verification | Explain role, credentials, commentary standard, and disclosures |
| `/injuries` | Injury & interruption log | Shell/live as available | Track meaningful issues, adaptations, and outcomes |
| `/gear` | Gear notes | Shell/live as available | Document meaningful gear decisions without becoming a review site |
| `/costs` | Cost addendum | Coming Soon initially acceptable | Summarize experiment costs as supporting information |
| `/about` | About | Live | Introduce the author, Dr. Reddy, project boundary, and contact/newsletter paths |
| `/newsletter` | Newsletter landing | Live | Explain cadence/value and collect subscriptions |
| `/privacy` | Privacy | Live | Explain analytics, newsletter processing, health-data publishing choices, and rights |
| `/terms` | Terms & medical disclaimer | Live | Set informational boundaries and site terms |
| `/404` | Not found | Live | Recover gracefully with search/navigation and latest content |

### 5.3 Content taxonomy

Journal entries use one primary type and zero or more topics.

**Primary types:** Run, Reflection, Doctor Conversation, Plan Update, Test Update, Injury/Interruption, Gear, Explainer, Retrospective.

**Suggested topics:** VO₂ max, Zone 2, RHR, sleep, strength, body composition, glucose, blood pressure, fueling, heat, shoes, recovery, injury, motivation, research, race strategy.

Avoid overlapping category systems. Type answers “what format is this?” Topic answers “what is this about?”

---

## 6. Page specifications

## 6.1 Home

### Purpose

Explain the experiment without requiring a separate Start Here page. Sell the question first, establish the human stakes, show current status, and give visitors a clear next step.

### Required modules, in order

1. **Hero question**
   - Recommended working headline: “Does training for a marathon make you healthier?”
   - Supporting copy: four months, a five-hour marathon target, observed health markers, one curious amateur, and one sports-medicine expert/research scientist.
   - Primary action: Read the latest.
   - Secondary action: See the experiment.

2. **Experiment in one glance**
   - Event: BYD Singapore Marathon 2026.
   - Goal: 42.2 km in 5:00.
   - Scope: four months through immediate post-race retrospective.
   - Status: week number or current phase.
   - Collaborators: author and Dr. Varun Reddy.

3. **Marathon progress strip**
   - Weeks completed / total planned.
   - Sessions completed / planned for current period.
   - Current weekly mileage.
   - Longest run so far.
   - Target: 42.2 km in 5:00.
   - Readiness only if a defensible, explained model exists; otherwise omit or label Awaiting Sufficient Data.

4. **Latest from the Journal**
   - One featured entry plus three recent entries across different types when available.
   - Run entries may show distance and duration, but non-run entries must not appear subordinate.

5. **The health question**
   - Compact explanation of what is being observed and why outcomes are not scored as wins or losses.
   - Link to The Experiment and Dashboard.

6. **Plan meets reality**
   - Current plan status, latest revision, short reason, and link to comparison.

7. **Two perspectives**
   - Introduce the author and Dr. Reddy.
   - Preview the recurring framework: What I thought → What Dr. Reddy thought → What we did → What happened.

8. **Explainer feature**
   - Highlight one timely concept connected to current training.

9. **Newsletter signup**
   - Explain what subscribers receive: new entries, meaningful data updates, plan changes, and the eventual result.
   - Keep the form low friction: email, optional first name, clear consent copy.

10. **Project boundary and disclaimer**
   - Briefly state that this is one person's experience and not medical advice.

### Home acceptance criteria

- A first-time visitor can explain the question, target, protagonists, and current state after scanning the page.
- The hero does not lead with the author's biography.
- Both run and non-run Journal entries can be featured.
- Health numbers do not display celebratory or alarming trend language without interpretation.
- Homepage replaces, rather than duplicates, a Start Here page.

## 6.2 Journal index

### Purpose

Make the evolving story easy to follow while supporting every run and broader editorial work.

### Requirements

- Default view is reverse chronological.
- Featured/pinned entry is optional and used sparingly.
- Filters: primary type, topic, and phase; filters must produce shareable URLs.
- Search is desirable for V1 but may be deferred if content volume is low; the shell must not show a non-functional search box.
- Cards display title, short deck, publication date, optional Updated date, primary type, reading time, and an appropriate visual.
- Run cards may also display distance, duration, average pace, and perceived effort.
- Empty filter results offer a reset action and relevant alternatives.

### Editorial ordering

Do not force every run onto the homepage. Every run is published and discoverable, while editorial curation determines which entries become featured stories or newsletter leads.

## 6.3 Journal entry

### Shared anatomy

- Title and deck.
- Primary type and topics.
- Publication date; Updated date only after meaningful additions.
- Author and, where applicable, reviewer/contributor attribution.
- Hero image or deliberately selected visual treatment.
- Narrative body.
- Optional structured modules.
- Sources and evidence notes where claims require them.
- “What changed?” note for meaningful updates.
- Related plan version, metrics, explainers, injuries, or entries.
- Previous/next or recommended reading.
- Newsletter module after the main narrative.

### Optional structured modules

- Garmin run summary.
- Subjective reflection.
- Plan-versus-actual comparison.
- Doctor commentary.
- Four-part disagreement/decision framework.
- Metric snapshot.
- Evidence note.
- Timeline or sequence.
- Image gallery.
- “What I would do differently.”

### Run-entry fields

- Activity date.
- Session name/type.
- Planned session reference.
- Distance, duration, average pace.
- Heart-rate summary where available and useful.
- Elevation, cadence, temperature/conditions where available and relevant.
- Garmin source identifier or private source URL.
- Completion status: completed, modified, stopped, skipped, or reconstructed.
- Perceived effort, feel, pain/discomfort, sleep/recovery context, fueling/hydration notes.
- Narrative reflection and lesson.

Garmin fields are estimates or device measurements and must be labeled accordingly. Do not expose precise start/end coordinates or home-location patterns by default.

### Retrospective entries

The first two weeks may be reconstructed from existing writing and Garmin data. A “Reconstructed” label may be used when it adds clarity, but the site does not need separate event and publication timestamp machinery. Older writing can be published later. Meaningful data or commentary additions use the normal Updated date.

## 6.4 The Experiment

### Purpose

Define what is being asked, measured, and inferred so the public story remains intellectually honest.

### Required sections

1. Central hypothesis.
2. Why a marathon, and why four months.
3. Athletic target and project success criteria.
4. Health markers observed.
5. Baseline and follow-up schedule.
6. Garmin and other data sources.
7. Distinction between estimates, home readings, laboratory measurements, and subjective reports.
8. Confounders and limitations.
9. Dr. Reddy's role and evidence standard.
10. How conclusions will be framed.
11. Project timeline through immediate post-race retrospective.
12. Medical/informational disclaimer.

### Interpretation rules

- Never infer causation from a single before/after comparison.
- Do not call short-term noise a trend.
- Preserve units, dates, conditions, devices, and methods.
- Identify changes in measurement method.
- Distinguish Garmin-estimated VO₂ max from laboratory-measured VO₂ max.
- State when a reading is missing, inconsistent, or not comparable.
- Where Dr. Reddy interprets evidence, link to primary research or strong evidence reviews when appropriate.
- Present individual observations as observations, not general recommendations.

## 6.5 The Plan

### Purpose

Treat the training plan as living content and make adaptation visible.

### Required views

- **Current plan:** the version presently guiding training.
- **Original plan:** the author's initial lay understanding, preserved.
- **Doctor review:** Dr. Reddy's critique and proposed changes.
- **Plan vs actual:** what was scheduled and what occurred.
- **Change history:** dated revisions with reasons and linked Journal evidence.

### Plan states

Each session may be planned, completed as planned, completed with modification, moved, skipped, stopped, or awaiting outcome.

### Revision requirements

Every material revision records:

- Version identifier and effective date.
- Author/decision owner.
- What changed.
- Why it changed.
- Evidence or experience informing the change.
- Dr. Reddy's view, if relevant.
- Affected weeks or sessions.
- Later outcome when known.

Do not silently rewrite old plan versions. Minor copy corrections do not require a new version.

### Recommended comparison frame

> **What I thought → What Dr. Reddy thought → What we did → What happened**

This frame is used when it illuminates a genuine difference. Do not manufacture conflict or force the structure onto trivial decisions.

## 6.6 Dashboard

### Purpose

Answer two different questions without conflating them:

1. How is preparation for the five-hour marathon progressing?
2. What is happening to the author's health?

### Layer A: Marathon progress

This is the dominant dashboard layer.

- Target: 42.2 km in 5:00.
- Current phase and weeks completed.
- Planned versus completed sessions.
- Weekly mileage and recent training load using plainly described calculations.
- Longest run so far.
- Recent pace or benchmark performance where comparable.
- Interruptions, injuries, or material plan deviations.
- Readiness estimate only if defensible, transparent, and based on sufficient data.

Avoid a single gamified percentage that pretends marathon readiness is precisely knowable.

### Layer B: Health observations

- VO₂ max.
- Resting heart rate (RHR).
- Weight.
- Body fat and muscle mass.
- Strength benchmarks.
- Sleep.
- Blood pressure.
- Glucose.
- Selected blood tests.

HRV may appear as incidental data if later available, but it is not a core metric and must not create a paid-device dependency.

### Visualization rules

- Show raw values, units, dates, source, and method.
- Use neutral colors for changes until interpretation exists.
- Mark sparse charts as Awaiting More Data rather than drawing misleading lines.
- Do not compare unlike methods without a visible break or note.
- Provide accessible text summaries and data tables for charts.
- Link material updates to the Journal entry that interprets them.

### Awaiting Data behavior

An empty metric card should state:

- What will be measured.
- Why it matters to the question.
- The expected source or test.
- The event that unlocks the section, if known.
- A link to methodology or a relevant explainer.

It should not display an empty chart frame.

## 6.7 Health observations and metric detail

### Purpose

Publish extracted health numbers and interpretation without exposing raw medical documents.

### Metric detail anatomy

- Plain-language definition.
- Why it may matter here.
- Current and historical readings.
- Unit, date/time, source, method, and relevant conditions.
- Reference range where useful and properly contextualized.
- Measurement caveats.
- Author reflection.
- Dr. Reddy commentary and evidence links when applicable.
- Related Journal entries and explainers.

### Medical-report handling

Original reports remain private source material. The public site stores only selected measurements, reference ranges where useful, dates, methodology, and interpretation. Before publication, confirm that copied values are accurate and do not expose identifiers or unrelated sensitive information.

## 6.8 Explainers

### Purpose

Build an accessible fitness-and-longevity knowledge layer around questions raised by the journey.

### Explainer structure

1. One-sentence answer.
2. Why this came up in the experiment.
3. The intuitive model or analogy.
4. What the evidence says.
5. What remains uncertain or contested.
6. What is being observed in this project.
7. Sources and further reading.

Long explainers may use side quests, diagrams, and humor, but must maintain a visible logical spine. Avoid generic encyclopedia articles disconnected from the live project.

### Suggested initial explainers

- What VO₂ max is—and what Garmin is estimating.
- Why resting heart rate can be useful and noisy.
- Marathon fitness versus longevity fitness.
- Zone 2 without the mythology.
- What body-composition tests can and cannot tell us.
- Why endurance training might affect muscle and strength.
- Blood glucose in active people.
- Heat, hydration, and training in Singapore.

## 6.9 Dr. Varun Reddy profile and commentary

### Publication gate

Before launch, verify with Dr. Reddy:

- Preferred name and title.
- Clinical specialty and current role.
- Research position/affiliation.
- Degrees, registrations, and relevant credentials.
- Profile photo and biography permission.
- Any conflict-of-interest or disclosure language.
- Whether commentary is personal expert opinion or represents an institution.

Do not publish unverified credential language.

### Commentary requirements

- Clearly attributed to Dr. Reddy.
- Distinguish evidence summary, clinical/expert judgment, and project-specific suggestion.
- Link established evidence where appropriate, prioritizing primary research and strong evidence reviews.
- Include publication date and Updated date for material revisions.
- Preserve meaningful disagreements with the author.
- Never imply individual clinical care for readers.

## 6.10 Injury & interruption log

### Purpose

Document events that materially change training or interpretation.

### Fields

- Onset date and status.
- Plain-language description and affected activity.
- Severity/impact without self-diagnosing beyond confirmed information.
- Training modification.
- Professional assessment where available and authorized.
- Recovery milestones.
- Linked plan revisions and Journal entries.
- Outcome.

The page may begin in an Awaiting Data state. Do not frame the absence of injury as guaranteed or the occurrence of injury as failure.

## 6.11 Gear

Document gear only when it changes the experiment or teaches something: shoes, watch, testing equipment, fueling products, or meaningful replacements. Capture why a choice was made, cost where relevant, what changed, and later outcome. Avoid affiliate-style review language unless a future commercial policy explicitly permits it.

## 6.12 Cost addendum

Costs are supporting information. A simple categorized ledger may include race entry, tests, shoes, equipment, physiotherapy, and consultations. Publish totals and context; do not let cost dominate the main dashboard. This page may launch as Coming Soon.

## 6.13 About

Introduce the author as the visible protagonist, explain the origin of the question, introduce Dr. Reddy after credential verification, state the project boundary, and reiterate the editorial/evidence principles. Include contact and newsletter links. Do not duplicate the full Experiment page.

## 6.14 Newsletter

### Day-1 requirements

- Dedicated landing page and forms on Home and Journal entries.
- Clear value proposition and approximate cadence without promising an unsustainable schedule.
- Double opt-in where supported.
- Confirmation, error, already-subscribed, and unsubscribe states.
- Privacy link adjacent to signup.
- Source/placement tagging for conversion analysis.
- Accessible labels and keyboard interaction.

Newsletter content may include new Journal entries, meaningful metric updates, plan revisions, and race milestones. No reader interaction is required.

---

## 7. Content and data model

The implementation may use a headless CMS, repository-based content, or another editor-friendly system. The logical model below is platform-agnostic.

## 7.1 Core entities

### Person

- `id`
- `name`
- `slug`
- `role` — author, collaborator, contributor, reviewer
- `short_bio`
- `full_bio`
- `credentials` — publication-gated
- `affiliations`
- `photo`
- `profile_permissions_confirmed`
- `disclosures`

### JournalEntry

- `id`, `slug`, `title`, `deck`
- `primary_type`
- `topics[]`
- `status` — draft, scheduled, published, archived
- `published_at`
- `updated_at` — only for meaningful updates
- `authors[]`, `contributors[]`, `reviewers[]`
- `hero_media`
- `body`
- `update_note`
- `featured`
- `newsletter_featured`
- `related_entries[]`
- `related_explainers[]`
- `related_plan_versions[]`
- `related_metrics[]`
- `seo_title`, `seo_description`, `social_image`
- `medical_review_status` where relevant

### RunActivity

- `id`
- `journal_entry_id`
- `activity_date`
- `session_type`
- `planned_session_id`
- `completion_status`
- `distance_km`, `duration_seconds`, `average_pace`
- `heart_rate_summary`
- `elevation_m`, `cadence`, `conditions`
- `device` and `source_type` — Garmin/manual
- `source_record_id` — private where appropriate
- `perceived_effort`
- `feel`, `pain_notes`, `sleep_context`, `fueling_notes`
- `reconstructed` boolean
- `location_privacy_checked`

### PlanVersion

- `id`, `name`, `version_number`
- `effective_from`, `effective_to`
- `status` — original, current, superseded
- `created_by`, `reviewed_by`
- `summary`
- `change_reason`
- `evidence_links[]`
- `affected_sessions[]`
- `related_entries[]`

### PlannedSession

- `id`, `plan_version_id`
- `scheduled_date` or `week_index`
- `session_type`, `title`, `description`
- `target_distance`, `target_duration`, `target_intensity`
- `status`
- `actual_activity_id`
- `modification_note`

### MetricDefinition

- `id`, `slug`, `name`
- `category` — marathon progress, cardiorespiratory, body composition, recovery, strength, metabolic, laboratory
- `unit`
- `plain_definition`
- `why_it_matters`
- `source_types[]`
- `core_metric` boolean
- `display_precision`
- `interpretation_rules`
- `methodology_notes`

### MetricReading

- `id`, `metric_definition_id`
- `measured_at`
- `value` and optional `range`
- `unit`
- `source_type` — Garmin estimate, device measurement, home reading, laboratory, clinical test, manual calculation
- `device_or_method`
- `conditions`
- `reference_range`
- `comparable_series_id`
- `quality_flag`
- `public_note`
- `related_entry_id`
- `verified_by`

### ExpertCommentary

- `id`
- `author_person_id`
- `context_type` and `context_id`
- `commentary_type` — evidence summary, expert judgment, project recommendation
- `body`
- `sources[]`
- `published_at`, `updated_at`
- `credential_snapshot`
- `disclosure`

### EvidenceSource

- `id`
- `title`, `authors`, `year`
- `source_kind` — primary research, systematic review, guideline, other
- `publisher_or_journal`
- `url`, `doi`
- `accessed_at`
- `evidence_note`

### Explainer

- `id`, `slug`, `title`, `one_sentence_answer`
- `body`
- `sources[]`
- `related_metrics[]`, `related_entries[]`
- `review_status`
- `published_at`, `updated_at`

### InjuryInterruption

- `id`, `title`
- `onset_date`, `resolved_date`, `status`
- `description`, `impact`, `training_modification`
- `assessment`
- `milestones[]`
- `related_plan_versions[]`, `related_entries[]`

### Expense

- `id`, `date`, `category`, `description`
- `amount`, `currency`
- `included_in_public_total`
- `related_entry_id`

### NewsletterSubscriber

Subscriber data should normally live in the chosen email platform, not the public CMS. Store only fields needed for consent, delivery, segmentation, and suppression.

## 7.2 Shared content states

- **Draft:** visible only to editors.
- **Scheduled:** queued for publication.
- **Published:** public and complete enough for use.
- **Updated:** published content with a meaningful later addition and visible update date/note.
- **Coming Soon:** the feature or editorial section is planned but not yet produced.
- **Awaiting Data:** the section exists and is designed, but the required measurement/event has not occurred.
- **Insufficient Data:** readings exist but cannot support a trend or interpretation.
- **Superseded:** preserved historical plan version or methodology no longer current.

---

## 8. Metrics and measurement plan

### 8.1 Core observations

| Area | Metric | Likely source | Presentation rule |
|---|---|---|---|
| Performance | Marathon completion and time | Official race result | Primary outcome: 42.2 km in 5:00 |
| Training | Sessions, mileage, longest run, pace | Garmin + plan | Compare planned and actual; expose missing/modified sessions |
| Cardiorespiratory | VO₂ max | Garmin estimate and/or clinical test | Keep methods separate and label estimates |
| Recovery | Resting heart rate | Garmin | Prefer consistent conditions; explain noise |
| Recovery | Sleep | Garmin and subjective notes | Avoid false precision; show trends cautiously |
| Body composition | Weight | Consistent scale | Show method/conditions and neutral change language |
| Body composition | Body fat, muscle mass | Selected body-composition method | Do not compare unlike methods as one series |
| Strength | Defined benchmark set | Logged testing protocol | Preserve exact exercise, load, reps, and protocol |
| Cardiometabolic | Blood pressure | Validated monitor/clinical reading | Preserve posture, repeat readings, and context where available |
| Cardiometabolic | Glucose | Chosen test/device | Explain whether fasting, spot, laboratory, or sensor-derived |
| Laboratory | Selected blood tests | Laboratory | Publish extracted values and interpretation, not raw reports |

### 8.2 HRV decision

HRV is not a core metric because the project should not require a Whoop subscription or add unnecessary device burden. If Garmin or another existing source later provides useful HRV data, it may be discussed as supplemental and method-specific. RHR remains the core practical recovery marker.

### 8.3 Measurement governance

- Define the measurement protocol before interpreting change.
- Store the source, unit, method, time, and relevant conditions with every reading.
- Preserve original precision internally; display only meaningful precision.
- Flag manually entered values for verification.
- Do not silently correct published health values; update with a note when material.
- Restrict CMS access to private source references and unpublished health information.
- Maintain a pre-publication verification step for clinical/laboratory values.

---

## 9. Editorial system

### 9.1 Voice

The voice is measured, factual, rigorous, conversational, curious, and irreverent. It can be self-deprecating, but not glib about health or other people's expertise. It explains complex ideas deeply without performing complexity.

### 9.2 Writing rules

- Lead with the human question, tension, or event.
- Use first person for experience and clearly attributed voice for Dr. Reddy.
- State uncertainty plainly.
- Separate observation, interpretation, hypothesis, and established evidence.
- Link claims about health or training to appropriate sources when material.
- Prefer specific numbers and concrete episodes over generic motivation language.
- Publish bad days and mistakes without manufacturing drama.
- Correct errors visibly and calmly.
- Avoid “reversing age” or “proof” language unless directly critiquing it. ("Biohacking" is permitted — the author uses the term for his own wearables/self-tracking history.)
- Do not imply that completing a marathon is necessary or sufficient for longevity.

### 9.3 Evidence standard

For Dr. Reddy's scientific commentary and dedicated explainers:

- Prefer primary research, systematic reviews, meta-analyses, and professional guidelines.
- Link directly to the source or stable identifier.
- Explain study population and relevance when it affects interpretation.
- Avoid citation decoration: every citation should support a specific claim.
- Note disagreement or uncertainty in the literature.
- Distinguish mechanistic plausibility from demonstrated outcomes.

### 9.4 Disagreement as a feature

Use this framework when the author and Dr. Reddy materially differ:

1. **What I thought** — preserve the author's initial model.
2. **What Dr. Reddy thought** — present his critique in his own attributed voice.
3. **What we did** — record the actual decision without implying consensus.
4. **What happened** — return later with the observed outcome.

The framework may span multiple entries and should link between them.

### 9.5 Update policy

- Use normal publication dates.
- Add an Updated date only for meaningful additions such as Garmin data, expert commentary, test results, corrections, or outcomes.
- Include a short update note when the nature of the change is not obvious.
- Do not create separate happened/written/published timestamp fields solely for the first reconstructed weeks.

### 9.6 Review workflow

1. Author drafts or assembles entry; AI assistance is optional.
2. Structured data is imported or entered and verified.
3. Claims are sourced in proportion to their importance.
4. Dr. Reddy reviews only content requiring his contribution, attribution, or medical/scientific check.
5. Privacy/location/third-party check is completed.
6. Editor previews desktop/mobile, links, visuals, metadata, and accessibility.
7. Publish; distribute through newsletter as appropriate.

AI-generated or AI-assisted text must receive human editorial approval. The platform does not need to know how the draft was created.

---

## 10. Visual and interaction design

### 10.1 Design character

The site should feel like a thoughtful independent publication crossed with a field notebook: warm, intelligent, legible, and slightly playful. Avoid clinical-dashboard sterility, macho running aesthetics, neon “biohacker” tropes, and generic wellness minimalism.

### 10.2 Visual hierarchy

- Editorial typography carries the story.
- Data visualizations use restrained, consistent colors and visible units.
- Marathon progress is visually primary on the Dashboard.
- Health observations are calm and neutral.
- Expert commentary is distinctive but not treated as a rubber stamp.
- Coming Soon/Awaiting Data states look intentional, not disabled.

### 10.3 Reusable visual templates

Create templates before demanding bespoke artwork:

- Run summary card.
- Planned vs actual session card.
- Weekly mileage chart.
- Plan revision timeline.
- Metric snapshot and metric history chart.
- “What I thought / Dr. Reddy thought / We did / What happened” sequence.
- Evidence-note card.
- Quote/commentary card.
- Simple explainer diagram frame.
- Photo + caption treatment.
- Newsletter/social share image.
- Coming Soon and Awaiting Data state.

Each template needs responsive behavior, accessible text, export guidance for social/newsletter use, and CMS fields matching the data model.

### 10.4 Image burden

Visuals are important, but a missing bespoke illustration must not block routine publication. Minimum expectations:

- Run entry: one photo or generated data visual when available.
- Test update: one clear chart or measurement card.
- Explainer: at least one purposeful diagram for concepts that benefit from it.
- Long-form feature: a considered hero and supporting visual rhythm.

### 10.5 Accessibility

- Meet WCAG 2.2 AA as the target.
- Full keyboard navigation and visible focus states.
- Semantic headings and landmarks.
- Color is never the only carrier of meaning.
- Sufficient contrast in text and charts.
- Alternative text for informative images; decorative images ignored by assistive technology.
- Text/table equivalent for charts.
- Respect reduced-motion preferences.
- Form errors are specific and programmatically associated.
- Do not hide essential definitions behind hover-only interactions.

---

## 11. Coming Soon and Awaiting Data system

### 11.1 When to use each state

**Coming Soon** means the content or feature is planned but has not been produced. Example: cost addendum before expenses are compiled.

**Awaiting Data** means the page structure and question are ready, but the relevant test, milestone, or measurement has not occurred. Example: post-marathon laboratory comparison.

**Insufficient Data** means readings exist but do not yet justify a trend or interpretation.

### 11.2 Required placeholder anatomy

Every placeholder states:

- What belongs here.
- Why it matters.
- Current status.
- What unlocks it, if known.
- What the visitor can do now: read a related entry, view methodology, or subscribe.

### 11.3 Prohibited placeholder behavior

- “Coming soon” with no explanation.
- Dead controls, fake charts, or disabled navigation with no alternative.
- Fabricated sample health data in production.
- Launch countdowns without a credible date.
- Newsletter forms that do not work.

---

## 12. Privacy, permissions, and medical safeguards

### 12.1 Author-owned material

There is no formal internal consent workflow for the author's own story, photos, or chosen health data. Use a practical publication check instead: accuracy, sensitivity, location safety, accidental identifiers, and future regret.

### 12.2 Third parties

Obtain permission before publishing identifiable third-party photos, personal messages, medical details, or substantive quotations not clearly intended for publication. Dr. Reddy must approve his biography, credentials, profile image, and attributed commentary. Institutional names and logos follow applicable permissions and brand rules.

### 12.3 Health information

- Publish selected values and interpretation, not raw reports.
- Keep original reports and private source links outside the public media library.
- Remove identifiers from any temporary image or excerpt used in production.
- Limit administrative access.
- Maintain backups and an incident-response contact.

### 12.4 Location safety

Garmin routes can reveal home, work, routines, and exact times. Public run entries should omit precise start/end points by default and use generalized maps only after review.

### 12.5 Medical boundary

Every medically relevant page should make it clear that:

- The site documents one person's experience.
- It is educational and informational, not medical advice.
- Dr. Reddy's project commentary is not a clinician-patient relationship with readers.
- Readers should seek appropriate professional care for personal decisions or symptoms.

The disclaimer should be visible but not repeated so aggressively that it disrupts every paragraph.

---

## 13. Functional and technical requirements

### 13.1 Content management

Editors must be able to:

- Create every Journal type from templates.
- Add structured run data without embedding screenshots.
- Create and compare plan versions.
- Add metric readings with source/method metadata.
- Attach Dr. Reddy commentary and evidence sources.
- Publish Coming Soon/Awaiting Data states.
- Set publication and Updated dates.
- Preview responsive layouts and social cards.
- Schedule and unpublish content.

### 13.2 Garmin data

Garmin is the primary training and day-to-day physiological source. V1 may begin with manual entry or export/import. The model should preserve a stable private source identifier so automation can be added later without rebuilding content.

If automation is implemented:

- Ingest into a private staging record.
- Let the author select what becomes public.
- Prevent duplicates.
- Preserve original source units and timestamps.
- Apply location privacy rules before publication.
- Never auto-publish health or route data.

### 13.3 Search and discovery

- Sitewide metadata supports type, topic, phase, people, metrics, and plan versions.
- Related-content links are curated first and algorithmic second.
- Generate XML sitemap, RSS/Atom feed, canonical URLs, and structured metadata.
- Use Article/BlogPosting and Person schema where accurate; do not use MedicalWebPage schema unless implementation and content warrant it.

### 13.4 Newsletter integration

- Use a reputable provider with double opt-in, unsubscribe, suppression, and export/delete capabilities.
- Store consent timestamp and signup source.
- Provide clear success/error states without losing the reader's page position.
- Avoid pre-checked marketing consent.

### 13.5 Performance

Targets for representative production pages on mobile:

- Core Web Vitals rated “good” at the 75th percentile where realistically measurable.
- Optimize and responsively size images.
- Defer non-essential scripts and embeds.
- Render critical editorial content without requiring client-side JavaScript.
- Keep chart libraries lightweight and accessible.

### 13.6 Analytics

Track only useful product signals:

- Page and entry views.
- Newsletter form views, submissions, confirmations, and source placement.
- Navigation and related-content clicks.
- Explainer opens from inline definitions.
- Filter usage.
- Outbound evidence-link clicks.

Avoid invasive session replay by default, and document analytics in Privacy.

### 13.7 Reliability and security

- TLS everywhere.
- Least-privilege CMS roles and multi-factor authentication where available.
- Automated backups and restore test.
- Form spam protection that remains accessible.
- Dependency and platform update process.
- Error monitoring without collecting unnecessary health or form data.

---

## 14. SEO and distribution

### 14.1 Editorial SEO

- One clear search intent per explainer; Journal entries remain story-first.
- Descriptive titles and summaries that do not sensationalize findings.
- Stable URLs and redirects for changed slugs.
- Strong internal links among entries, metrics, plan versions, and explainers.
- Source and author pages build trust.

### 14.2 Social and newsletter packaging

Every published entry supports:

- Custom social title and description.
- Reusable social image template.
- Correct Open Graph/Twitter metadata.
- Newsletter excerpt.
- Share image that does not reveal private health or route details.

### 14.3 Claims discipline

Do not use headlines such as “Marathon training reversed my biological age” or “The one exercise that makes you live longer.” Curiosity is encouraged; overclaiming is not.

---

## 15. Launch plan and acceptance criteria

### 15.1 Content required at launch

- Home with real experiment framing and current status.
- At least one foundational Journal entry.
- Reconstructed entries for the first two weeks may be incomplete at launch if clearly scheduled and the Journal is not empty.
- The Experiment with measurement and interpretation rules.
- Original/current Plan, even if later weeks remain subject to review.
- Dashboard with real marathon-progress data and honest health placeholders.
- At least one useful Explainer or a specific Coming Soon index with a launch-ready first topic.
- About page.
- Dr. Reddy profile only after credential/permission verification; otherwise use a precise temporary state without publishing unverified claims.
- Newsletter landing and functioning forms.
- Privacy, Terms, and medical disclaimer.
- 404 page.

### 15.2 Functional launch checklist

- All navigation, footer, cards, filters, and related links work.
- All primary routes exist; no dead ends.
- Newsletter double opt-in, errors, confirmation, and unsubscribe are tested.
- CMS templates work for each content type.
- A run entry can be created with Garmin data and location review.
- A non-run Journal entry can be featured equally.
- A plan revision can be created without overwriting the prior version.
- Metric readings retain units, method, and source.
- Coming Soon, Awaiting Data, and Insufficient Data states render correctly.
- Updated dates appear only when set.
- Search, if shown, works; otherwise it is omitted.

### 15.3 Quality launch checklist

- Responsive QA across current mobile, tablet, and desktop breakpoints.
- Keyboard and screen-reader smoke test.
- Contrast and chart accessibility review.
- Copy edit and evidence-link check.
- Dr. Reddy attribution/credential approval complete.
- Health values independently checked against source material.
- Route maps and photos checked for privacy.
- No raw reports or unintended metadata in public assets.
- Performance, sitemap, robots, canonical, RSS, and social cards verified.
- Analytics and privacy disclosure match actual behavior.
- Backup and rollback process tested.

### 15.4 Definition of done for the full shell

A shell page is done when it has a stable route, final navigation label, page purpose, responsive design, real explanatory placeholder state, metadata, accessibility behavior, and a defined CMS pathway for replacing the placeholder. A blank page with “Coming soon” is not done.

---

## 16. Recommended delivery phases

The full shell launches in V1; phases describe implementation order, not omitted scope.

### Phase 1 — Foundation

- Design system, navigation, footer, content platform, shared metadata.
- Home, Journal, entry templates, Experiment, About.
- Newsletter integration.
- Privacy/terms and shared placeholder states.

### Phase 2 — Experiment mechanics

- Plan/version model and comparison views.
- Garmin-friendly run data entry/import.
- Dashboard Layer A.
- Metrics/methodology model and Dashboard Layer B placeholders.

### Phase 3 — Evidence and visual system

- Dr. Reddy commentary and source model.
- Explainers and progressive-disclosure components.
- Metric charts and accessible data tables.
- Reusable visual/social templates.

### Phase 4 — Shell completion and launch QA

- Health detail, injuries, gear, costs shell.
- Retrospective-ready templates.
- SEO/distribution plumbing.
- Accessibility, privacy, performance, and editorial QA.

---

## 17. Open questions and decisions deferred to implementation

These questions do not block the product definition, but should be resolved before their affected feature ships.

### Must resolve before public launch

1. ~~Exact BYD Singapore Marathon 2026 race date~~ — **resolved: 4 December 2026.** Official event naming and any trademark/brand-use constraints remain open.
2. Author's public name, preferred biography, portrait, and contact channel.
3. ~~Dr. Varun Reddy's exact title, credentials, affiliations, biography, attribution preferences, and disclosures~~ — **resolved: confirmed and published.** Photo permission remains open (no profile photo available yet).
4. CMS/hosting choice and responsible owner.
5. Newsletter provider, sender domain, cadence language, and privacy processor details.
6. Analytics provider and consent approach.
7. Initial measurement protocols, baseline dates, and which blood tests will be published.
8. Strength benchmark protocol.
9. Whether Garmin data begins as manual entry, export/import, or API integration.

### Resolve during design/build

10. Final brand identity, typography, palette, illustration style, and photography direction.
11. Exact homepage headline/deck and launch status wording.
12. Definition of training phases and filtering vocabulary.
13. Whether low-volume V1 needs site search at launch.
14. Readiness model, if any; default is to omit until defensible.
15. Charting implementation and data-download policy.
16. Formal editorial owner for source checks and health-value verification.
17. How newsletter archives appear on the site.
18. Whether costs are itemized or summarized by category.

### Deliberately undecided

19. Whether Longevity Marathon continues after the immediate post-race retrospective.
20. Whether reader interaction, accounts, questions, or community features ever become desirable.
21. How heavily AI is used in authoring; this remains a workflow choice, not a system dependency.

---

## 18. Starter copy direction

### Hero

**Does training for a marathon make you healthier?**

I have four months to train for the BYD Singapore Marathon, a five-hour target, a Garmin full of estimates, and Dr. Varun Reddy keeping the science honest. We are tracking what happens to my fitness, muscle, strength, recovery, and health—and publishing the useful parts, including the mistakes.

**Primary action:** Read the latest  
**Secondary action:** See how the experiment works

### Experiment summary

The athletic goal is simple: 42.2 km in 5:00. The health outcome is not. VO₂ max might improve. I might lose muscle. Some numbers may do nothing interesting at all. Those are all valid results. The job is to measure carefully, adapt the plan when reality intervenes, and resist turning one person's story into a universal prescription.

### Newsletter

**Follow the experiment, including the parts that go wrong.**

Get new Journal entries, meaningful data updates, plan changes, and the eventual marathon result. No community platform, no daily spam, and no pretending every wobble in a chart is a breakthrough.

### Awaiting Data

**Awaiting the next measurement**

This section will track body composition using the same method at meaningful points in the experiment. The baseline is being verified. Until then, read why endurance training might affect muscle and why short-term fluctuations are easy to overinterpret.

### Coming Soon

**The cost addendum is being assembled**

Race entry, shoes, tests, consultations, and the surprisingly expensive small objects that accumulate around a marathon will live here. It is supporting context, not the main event.

---

## 19. Final product statement

Longevity Marathon should launch as a complete, trustworthy publication shell around a live experiment. Its distinctive advantage is not exhaustive health data or elite athletic performance. It is the combination of a sharp question, a visible protagonist, an evidence-aware expert collaborator, a living plan, honest mistakes, and a design that lets readers move naturally between story, data, and explanation.

The five-hour marathon gives the project a finish line. The health measurements give it uncertainty. The publication system makes the uncertainty worth following.
