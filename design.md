# Longevity Marathon Website — Design & Aesthetic Guidelines

> **Scope:** This document owns the aesthetic *feel* of the site — palette, typography, motifs, restraint, and the visual vocabulary to avoid. It does not define information architecture, page content, or copy — see `longevity_marathon_website_spec_v2.md` (the canonical build spec) for that, and `longevity_marathon_editorial_spec.md` for voice. This doc is kept deliberately sparse: the main build is driven by the website spec, and this exists mainly for QC/review agents checking whether a built page matches the intended feel.

## 1. Core design idea

The website should feel like a **field notebook for a personal health experiment** — somewhere between a training diary, a medical case file, a scientific notebook, an editorial essay, and a restrained data publication. It should not feel like a fitness app, startup landing page, AI dashboard, or sports brand.

> **A serious experiment, conducted on one human, in public.**

The visitor should feel like they're looking over the shoulder of someone collecting evidence, forming hypotheses, changing their mind, and documenting what happens.

## 2. Design principles

### Calm and warm, not athletic

The overall character — matching `longevity_marathon_website_spec_v2.md` §10.1 — is **"a thoughtful independent publication crossed with a field notebook: warm, intelligent, legible, and slightly playful."** Avoid the visual vocabulary of marathon websites: black backgrounds, neon gradients, giant pace numbers, motivational photography, aggressive typography, achievement badges, progress rings everywhere.

"Slightly playful" means occasional wit in a caption, annotation, or chart title — not decoration, mascots, or a gradient hero.

Running is the subject matter, but the site is primarily about **thinking, experimentation, and health**.

### Editorial before dashboard

The site should feel like something you read. Data supports the story rather than becoming the interface — a visitor should move naturally between narrative and evidence rather than hitting a wall of metrics. (The specific sequence for that movement is defined once, canonically, as the website spec's disagreement/decision framework — §9.4 — not here.)

### Human and imperfect

This is a live experiment, not a retrospective success story. The design should leave visual room for uncertainty, annotations, changed opinions, abandoned hypotheses, mistakes, pain or injury, unexpected results, and comments from doctors or experts.

### Evidence without clinical coldness

Rigorous without looking like hospital software. Whitespace, typography, and restrained hierarchy do the work that boxes, borders, and UI chrome would otherwise do.

## 3. Visual language

### Background

Warm off-white rather than pure white. Think paper rather than screen. Very subtle texture is acceptable; avoid anything that reads as artificially vintage.

### Colour

Use an extremely limited palette. It should read as warm and intelligent rather than sterile — avoid, per the website spec §10.1, clinical-dashboard sterility, macho running aesthetics, neon "biohacker" tropes, and generic wellness minimalism.

- Base: warm off-white, charcoal/near-black, muted grey.
- One primary accent colour — probably a desaturated teal, green, or blue — used sparingly for links, selected data, annotations, timeline markers, and important changes.
- Health warnings or pain signals may use a restrained secondary colour, but avoid turning the page into traffic-light UI.

Colour should communicate meaning, not decorate.

## 4. Typography

Three roles carry the personality of the site:

- **Narrative / reflections** — a highly readable serif, for longer prose, personal reflections, journal excerpts, explanations. Should feel closer to an essay or notebook.
- **Interface / explanatory text** — a clean sans serif, for headings, labels, navigation, captions, annotations, doctor comments.
- **Data** — a restrained monospace, used selectively for dates, distance, pace, heart rate, sleep, training volume. Don't make every number monospace — it should function like notation in a scientific notebook, not a default.

## 5. Layout philosophy

Avoid a grid of cards; cards should be the exception, not the fundamental building block. Prefer sections, columns, horizontal rules, whitespace, marginal notes, inline data, and small charts — pages should resemble documents with layers of evidence rather than software screens.

Desktop layouts can use the margin as a second information channel (e.g. a narrative main column with quick vitals — HR, sleep, distance, soreness — running down the margin, creating the feel of an annotated case file). On mobile, those annotations move inline.

## 6. Recurring visual motifs

- **Annotations** — margin notes, corrections, and expert comments. Visually distinguish different voices/kinds of content (feeling, evidence, expert commentary, decision) with type and colour — the canonical structure of that pattern lives in the website spec, not here.
- **Revision marks** — show when an assumption changed (e.g. a struck-through old hypothesis next to the current one). Use sparingly.
- **Timeline markers** — dates, weeks, and phases acting like chapter markers (e.g. "AUG / WEEK 03"). Not necessarily a dedicated timeline component.
- **Small evidence charts** — resemble editorial graphics, not analytics dashboards: one metric, clear annotation, minimal axes, direct labels. A chart should answer one question.

## 7. Photography and imagery

Avoid generic running photography — no sunrise silhouettes, shoes on a track, finish-line celebrations, muscular athletes, motivational imagery. If used, photography should feel documentary: worn shoes, a blister, a Garmin screen after a run, breakfast before a long run, physio exercises, a notebook, actual training conditions in Singapore. Images should function as evidence from the experiment, not decoration.

## 8. Interaction design

The site should mostly behave like a publication — don't add interaction just because the medium allows it.

Useful: hover to reveal conditions, expand an annotation, move through the training timeline, compare planned vs. actual, inspect a data point.

Avoid: carousels, animated counters, floating glass panels, gratuitous parallax, excessive scroll animation, hover effects on every element.

Motion, where used, should reinforce chronology or causality.

## 9. Reference sites

Qualities to borrow, not templates to copy:

- **Our World in Data** — seriousness, information hierarchy, confidence in whitespace, mixing explanation and data. Not its institutional feel — this stays personal.
- **The Pudding** — narrative data storytelling, visualisation as argument, building a page around one idea. Considerably less visual playfulness.
- **Distill** — intellectual clarity, annotations, diagrams embedded in explanation.
- **Dear Data / Giorgia Lupi** — personal data as texture, small observations accumulating into a story. Not its hand-drawn visual language.
- **Low-Tech Magazine** — restraint, strong identity without elaborate UI.
- **Emergence Magazine** — editorial pacing, typography, calmness, considered digital reading.

## 10. Things to explicitly avoid

Gradient hero sections, glassmorphism, giant rounded cards, excessive rounded rectangles, generic icon sets, glowing charts, fitness rings, AI sparkles, dark-mode-first athletic aesthetics, giant motivational headlines, excessive shadows, decorative 3D illustrations, dashboards with ten metrics at once, every section sitting inside a container.

In particular, avoid the common AI-generated layout: **Huge headline → centered subtitle → two buttons → three cards → gradient → testimonials → CTA.** This is a publication and an experiment, not a SaaS landing page.

## 11. Design test

> **Does this look like a thoughtful person documenting an experiment, or like someone generated a health-tech website?**

If it feels like the latter: remove UI, reduce colour, remove a container, increase whitespace. Let content and typography do more of the work.

The finished website should feel **personal, rigorous, warm, curious, slightly playful, and unfinished in the right way** — because the experiment itself is still underway.
