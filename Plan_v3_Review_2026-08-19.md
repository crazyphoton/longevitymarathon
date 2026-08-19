# Plan v3 — Expert Panel Review, 19 August 2026

Three independent reviews of the Adaptive Marathon Plan v3 (17 weeks, BYD Singapore
Marathon, Fri 4 Dec 2026), each from a different professional lens: an exercise
physiologist, a marathon coach, and a sports podiatrist. Each reviewer read the full
plan document, the athlete's daily notes from 26 Jul–19 Aug (extracted from Notion
into `checkin`/`issue` and `data/notion_fitness_notes/`), and the gate rules in
`supabase/migrations/20260816090000_adaptive_v3.sql`.

**Provenance and limits.** The "experts" are AI personas run over this repository's
data — structured role-play, not clinicians. Nothing here is a diagnosis. The one
recommendation all three made unprompted is precisely that a remote review cannot
substitute for the in-person assessment the plan itself schedules (§5) and which has
not happened.

After the reviews ran, two data pulls changed the evidence base, and this document
reports both honestly:

1. **Garmin backfill to mid-June.** The panel was told "18.4 km logged in Week 1."
   With the Sunday 16 Aug run counted, Week 1 actually closed at **30.8 of 31 km
   (99%)**. The panel's specific week-by-week rebase numbers are therefore stale —
   but the corrected history *strengthens* their shared conclusion, because it
   reveals what the plan's baseline assumption was really resting on (§ "The 35
   km/week assumption," below).
2. **Time-in-HR-zone extraction.** Every run since June now has Garmin zone data
   (`export_run_zones`, charted on the dashboard). It contradicts the training log's
   own language about easy running (§ "Gates vs reality," item 4).

---

## 1. Consensus — what all three reviewers said independently

1. **The plan's architecture is good; its entry conditions are false.** The 80/20
   structure, long-run share cap, time caps, duration-led load table, fueling ladder,
   heat-by-residence framing, and symptom-corroborated wearable gates were praised by
   all three. All three also flagged the same false premise: "~35 km/week already
   tolerated."
2. **The heel is the controlling risk.** Morning pain that fades with warming up,
   returning as background pain, worsening 16→19 Aug — all three read this as an
   early plantar-fasciopathy / insertional-Achilles pattern. The right-calf pain
   migrating distally toward the Achilles (after July's bilateral Achilles episode)
   was read as the same loading chain, not a separate niggle.
3. **The 19 Aug run violated the plan's own gate.** Pain ~3/10 and rising at run
   start is tissue-amber under §9. The athlete ran.
4. **Book the in-person assessment now.** §5 schedules it for Weeks 1–2 with prior
   heel/Achilles concerns. Overdue by the plan's own standard.
5. **Drop strides while the heel is reactive; start the §10 strength work for real**
   (soleus-biased calf raises, foot intrinsics — the notes show stretching only);
   **substitute bike/pool rather than just cutting** to protect aerobic volume.

## 2. The 35 km/week assumption — settled by backfill

Weekly running volume, Garmin, weeks beginning (SGT):

| Week of | Runs | Km | Notes |
|---|---|---|---|
| 15 Jun | 1 | 8.2 | avg HR 159 |
| 22 Jun | 1 | 7.7 | avg HR 159 |
| 29 Jun | 0 | 0 | — |
| 6 Jul | 1 | 7.1 | hardest run in the window: 99% above easy |
| 13 Jul | 1 | 10.2 | |
| 20 Jul | 1 | 14.2 | the "12.5k" of the 26 Jul note — see §3, item 6 |
| 27 Jul–9 Aug | 0 | 0 | two empty weeks |
| 10 Aug (W1) | 3 | 30.8 | ~3× the summer norm, in one step |
| 17 Aug (W2) | 1+ | 9.4+ | week in progress |

The baseline was **one run a week, 7–14 km, at tempo-or-harder intensity, with two
multi-week gaps** — then Week 1 tripled it. The plan's stated envelope (~35 km/week
tolerated) was never demonstrated anywhere in the visible history. The niggle
cluster — heel niggle (16 Aug), sharp right knee (16 Aug), right calf (17 Aug) —
onset within days of the 30.8 km week. Correlation is not causation, but every
reviewer's causal model (tissue capacity lagging cardiovascular fitness) predicts
exactly this sequence, and no reviewer's model predicts its absence.

Consequence for the panel's advice: the question is no longer "how fast may we ramp
toward 35" (the ramp already happened, and tissue is objecting) but "how much of
30 km/week is retainable while the heel settles." The panel's consolidation
instinct — hold or reduce now, don't progress to W3's 36 km — survives the data
correction; their specific numbers don't.

## 3. Gates vs reality — where the control loop failed to describe the athlete

This is the sharpest finding of the whole exercise. The adaptive machinery is well
designed, but on 19 Aug it was describing a fictional athlete:

1. **The gates ran blind for their whole life.** The `checkin` table was empty until
   the Notion backfill on 19 Aug. Every daily status the site published was computed
   from wearable data alone — and by design, wearable-only deviation defaults to
   *green-easy*, never amber. The dashboard showed **green for 15 Aug**, the
   wine-headache-skipped-run day, and counted exactly 1 amber day in Week 1 (a
   wearable signal). The rules were fine; the sensor they depend on — the athlete
   writing things down where the engine can read them — was disconnected. Notes went
   to Notion; the engine read Supabase.
2. **The circuit breaker could never have fired.** §9's breaker (3 ambers in 7 days →
   structured review) counts computed daily statuses. With no symptom capture, four
   concurrent physical issues plus a lifestyle miss produced *one* recorded amber.
   The mechanism designed to catch exactly this situation was structurally unable to
   see it.
3. **The morning-pain blind spot.** The pain gate keys on in-run pain, next-morning
   stiffness minutes, and gait change. The heel's actual signature — pain on waking
   that *warms up and disappears mid-run* — never trips any of them. Tendinopathy's
   classic early pattern is invisible to the gate as written. (Podiatrist's proposed
   rule: same-site morning pain ≥3 consecutive mornings = tissue-amber regardless of
   in-run pain.)
4. **The intensity self-model was wrong by a full zone.** The notes say "zone 2 most
   of it, capping out at 150" (26 Jul) and describe slowing to stay easy. Garmin's
   zone ledger: every run from June through 13 Aug spent 78–99% of HR time *above*
   Z2; the June–July singles averaged HR 159. Only 16 Aug (56% Z2) resembles an easy
   run. Nothing in the gate system gates on intensity discipline — the 80/20
   structure is enforced by nothing but self-perception, which the data shows was
   off by a zone. (Author's clarification, 19 Aug: the zone boundaries are
   calibrated against an earlier VO2max test and are to be treated as more or less
   correct; current HR comes from the wrist optical sensor while the chest strap's
   battery is dead. That removes the "maybe the zones are wrong" escape hatch —
   the intensity finding stands.)
5. **Spec drift inside the machine.** The SQL gate rule says minimum viable peak
   `by_week: 13`; the plan document says end of Week 14. One of them is wrong, and
   which one decides when the go/no-go fires.
6. **Self-report noise is measurable.** The 26 Jul note says 12.5 km; Garmin logged
   14.2 km. A 13% recall error in the one number the athlete was surest of is the
   right prior for every subjective severity score in the system.
7. **The public record contradicts the private one.** The dashboard's hand-written
   copy still reads "No interruptions, injuries, or material plan deviations" while
   the issue register carries four active watches. (The generated regions will
   correct themselves on the next build now that data exists; the hand-written
   sentence needs an editorial pass.)

The unifying lesson: **every gate failure was a capture failure or a modeling
failure, not a threshold failure.** The thresholds the panel examined are
defensible; what broke was the assumption that the data reaching them described
reality.

## 4. Where the experts disagree — and why the disagreements can't be settled from here

**D1. How alarmed to be right now.**
Physiologist: the circuit breaker should already be firing; run the §9 structured
review formally. Coach: cut to 3 runs/week at 60–70% volume until seen. Podiatrist:
"nothing race-threatening today" — one consolidation week, progress after two
pain-free mornings.
*Underlying assumptions:* whether retrospectively-known symptoms count as formal
ambers when they were never logged through the system; whether four niggles are four
problems or one kinetic-chain problem plus noise; whether the knee counts at all
(D4). *Why uncertain:* the amber history is a reconstruction, not a record (§3.1);
severity scores are self-reported through a rememberer shown to drift 13% on
distance (§3.6); and none of the three has examined the leg. The difference between
"watch" and "circuit-break" is a clinical judgment being made without a clinic.

**D2. Is the 26 km minimum viable peak still real?**
Coach: at current easy pace (~7:40–8:00/km), 26 km takes ~3:20 — past the plan's own
3:15 time cap, so the MVP is unreachable as written; re-express it as time-based
(3:00–3:15 fueled, ~23–25 km) and make run-walk the A-strategy from Week 6, with a
realistic finish of 5:45–6:15. Physiologist: ≥26 km remains reachable in Weeks
12–14 if the heel is handled now; keep the target.
*Underlying assumptions:* the coach extrapolates current pace forward (pace is what
it is, heat is permanent, injury course eats the improvement window); the
physiologist assumes a normal training response (VO2max ~49 implies substantial
headroom over 12 weeks once volume is consistent — current pace reflects heat, HR
caps, and caution, not the aerobic ceiling). *Why uncertain — and this is the
interesting one:* the zone data undermines **both** positions at once. The author
has since confirmed (19 Aug) that the zone boundaries are calibrated against an
earlier VO2max test and should be treated as more or less correct (wrist optical
sensor for now — chest strap battery dead — which adds noise to any single reading
but little to multi-minute time-in-zone totals). Taking the zones as real: nearly
all past running was tempo-intensity, so the aerobic base is thinner than VO2max
suggests (coach's way) — but genuinely easy consistent volume is therefore an
untried stimulus with unusually large expected gains (physiologist's way). The
calibration being historical leaves modest drift possible, but the residual
uncertainty is no longer about measurement; it is about training response.
Pace-at-Week-12 is unknowable from here; the honest move is the plan's own one:
let the Week 11 half-marathon tune-up decide, and pre-commit to what result
triggers which goal.

**D3. What actually failed on 19 Aug — the rule or the athlete?**
Podiatrist: the rulebook missed the pattern (morning pain that warms up is
invisible to the gates) — fix the rules. Coach: the rulebook was clear enough and
was overridden — fix enforcement (a no-self-negotiation pre-run rule, weekly
external review of the amber log).
*Underlying assumptions:* one about rule coverage, one about athlete psychology.
*Why uncertain:* there is exactly one incident, and it supports both readings
simultaneously — 3/10-rising arguably was already amber (adherence failure), and
the morning pattern genuinely wasn't codified (coverage failure). n=1 cannot
separate them. Fortunately it doesn't need to: both fixes are cheap, non-conflicting,
and worth doing regardless of which story is true.

**D4. Does the right knee count?**
Podiatrist: patellofemoral pattern (squat/downhill-provoked, walking/running fine) —
monitor, don't count it toward escalation. Physiologist: a new symptom during a load
spike counts toward the circuit breaker, whatever its label.
*Underlying assumptions:* a specific benign diagnosis versus a deliberately
diagnosis-agnostic counting rule. *Why uncertain:* the pattern-match to PFPS is
plausible but unexamined; intermittent sharp pain can also be referred or mechanical.
More deeply, this is a policy disagreement about what counters are *for* — clinical
triage (count what's dangerous) versus system safety (count what's new). The plan's
gate rules currently embody the physiologist's philosophy; the podiatrist is applying
clinical parsimony. Both are coherent; they just answer different questions.

**The general pattern across all four:** each disagreement bottoms out in something
unmeasured — an unexamined leg, an unvalidated zone configuration, an unrecorded
amber history, an unknowable training response. None of it is resolvable by more
argument. Three of the four (D1, D3, and the zone half of D2) are resolvable by
cheap actions: capture symptoms where the engine reads them (done as of 19 Aug),
verify the watch's zone settings (resolved 19 Aug: calibrated against an earlier
VO2max test, per the author), get the in-person exam. D2's core — what pace will
exist in November — is genuinely unknowable, which is why the plan's Week-11
tune-up-then-decide mechanism, not any expert's forecast, is the right arbiter.

## 5. Actions implied (decisions left to the author)

Cheap and consensus-backed, in order:

1. In-person podiatry/physio assessment this week (§5 requirement, all three
   reviewers).
2. Hold Week 2–3 at or below Week 1's load; no strides; flat routes; substitute one
   run with bike/pool; begin daily calf/foot loading per §10.
3. ~~Verify Garmin's HR zone configuration~~ — resolved 19 Aug: boundaries are
   calibrated against an earlier VO2max test (author). Residual: recharge/replace
   the chest-strap battery — wrist optical is fine for time-in-zone but the strap
   is better for any future threshold work — and note the calibration's age when
   the next VO2max estimate lands.
4. Add the morning-pain gate rule (podiatrist) *and* the pre-run no-negotiation
   rule (coach) — D3 doesn't need to be adjudicated to act.
5. Fix the `min_viable_peak` week-13/14 inconsistency (SQL vs document).
6. Editorial pass on the dashboard's "no injuries" sentence.

Requiring an actual decision by the author:

7. Whether the MVP stays 26 km or becomes time-based (D2) — defensibly deferred to
   the Week 11 tune-up, but the deferral should be recorded as a `weekly_decision`
   with pre-committed criteria, not left implicit.
8. Whether to run the §9 structured review now (D1). Given §3.2 showed the breaker
   *couldn't* have fired even if deserved, running one voluntarily this week is the
   conservative reading of the plan's own intent.
