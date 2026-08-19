# Plan v3 expert review

**Date:** August 19, 2026

Three reviewers assessed the plan: an exercise physiologist, a marathon coach, and
a podiatrist. Each read the plan document, the daily notes from July 26 to
August 19, and the gate rules.

**Important:** The reviewers are AI personas, not clinicians. This review is not
medical advice. All three reviewers recommend the in-person assessment that the
plan schedules in §5. It hasn't happened yet.

Two data updates landed after the reviews:

- Garmin history now goes back to mid-June. The reviewers saw "18.4 km logged in
  Week 1". The true Week 1 total is 30.8 of 31 km.
- Every run now has time-in-zone data. The zone boundaries are calibrated against
  an earlier VO2max test, so treat them as correct. The chest strap battery is
  dead; wrist heart rate is noisy per beat but reliable for time-in-zone totals.

## Consensus findings

All three reviewers agree on the following:

- **The plan design is sound, but its starting assumption is wrong.** The 80/20
  structure, time caps, cutback weeks, fueling ladder, and wearable gates are
  well designed. However, the plan assumes you already tolerate about 35 km per
  week. The training history doesn't show this.
- **The heel is the controlling risk.** Morning pain that fades as you warm up is
  the classic early pattern of plantar fascia or Achilles injury. The calf pain
  moving toward the Achilles belongs to the same loading chain.
- **The August 19 run broke the plan's own rule.** Pain at 3/10 and rising at the
  start of a run is a tissue amber under §9.
- **Book the in-person assessment this week.**
- **Stop strides while the heel is reactive. Start the §10 strength work.** The
  notes show stretching but no strength sessions. Replace one run with cycling
  instead of only cutting volume.

## The 35 km per week assumption

Weekly running volume from Garmin:

| Week of | Distance |
|---|---|
| June 15 | 8.2 km |
| June 22 | 7.7 km |
| June 29 | 0 |
| July 6 | 7.1 km |
| July 13 | 10.2 km |
| July 20 | 14.2 km |
| July 27–August 9 | 0 |
| August 10 (Week 1) | 30.8 km |

The baseline is one run per week, usually under an hour, at tempo effort or
harder, with two multi-week gaps. Week 1 tripled that volume in one step. The
heel, knee, and calf symptoms all appeared within days.

The open question is no longer how fast to ramp toward 35 km. The ramp already
happened. The question is how much of 30 km per week the heel can keep.

## Gate failures

The gate system is well designed, but on August 19 it described an athlete that
doesn't exist. The thresholds are fine. The data never reached them.

1. **The gates ran without symptom data.** Check-ins went to Notion, but the gate
   engine reads Supabase. The `checkin` table was empty until August 19. The site
   showed green for August 15 — the skipped-run day — and recorded one amber for
   the whole week.
2. **The circuit breaker couldn't fire.** The breaker needs three amber days in a
   week. Four active issues produced one recorded amber, so the mechanism built
   for this situation couldn't see it.
3. **The rules can't see the heel's pattern.** The gates check in-run pain,
   next-morning stiffness, and gait. Morning pain that disappears mid-run trips
   none of them, and that pattern is the signature of early tendon injury.
4. **Nothing checks intensity.** The notes say "zone 2, capped at 150". The watch
   shows 78–99% of time above zone 2 in every run before August 16. The 80/20
   split is enforced only by self-perception.
5. **The spec and the code disagree.** The SQL sets the minimum viable long run at
   week 13. The document says week 14. The dashboard also still says "no
   injuries" while the issue register holds four.
6. **Self-reports drift.** The July 26 note says 12.5 km; Garmin recorded 14.2 km.
   Apply the same skepticism to the pain scores.

## Disagreements

### How serious is the current state?

- Physiologist: the circuit breaker should already be firing. Run the formal §9
  review now.
- Coach: cut to three runs per week at 60–70% volume until you're examined.
- Podiatrist: nothing is race-threatening. Hold for one week, then progress after
  two pain-free mornings.

The split depends on whether four symptoms are four problems or one, and on
whether unlogged symptoms count as ambers. No one can settle this without
examining the leg. That is what the in-person visit is for.

### Is the 26 km minimum long run still achievable?

- Coach: no. At current pace, 26 km takes about 3:20, which exceeds the plan's
  own 3:15 cap. Make the target time-based and rehearse run-walk from Week 6.
- Physiologist: yes. VO2max around 49 implies large headroom once volume is
  consistent.

The zone data supports both sides. If all past running was tempo effort, the
aerobic base is thinner than the VO2max suggests. It also means genuinely easy
volume is a stimulus you have never applied, so expected gains are large.
November pace can't be known today. Let the Week 11 half marathon decide, and
record in advance which result selects which goal.

### What failed on August 19: the rule or the athlete?

- Podiatrist: the rules missed the morning-pain pattern. Fix the rules.
- Coach: the rule was clear and was overridden. Fix enforcement.

One incident supports both readings. Both fixes are cheap. Apply both.

### Does the knee count toward escalation?

- Podiatrist: it matches a benign kneecap pattern. Monitor only.
- Physiologist: any new symptom during a load spike counts.

This is a policy question — whether counters exist to sort dangerous from benign,
or to catch anything new. The plan's rules currently implement the second view.

Each disagreement rests on something unmeasured: an unexamined leg or an
unknowable November. The measurable questions were settled today.

## Recommended actions

1. Book a podiatrist or physiotherapist this week.
2. Hold weekly load at or below Week 1. No strides. Flat routes. Replace one run
   with cycling. Start daily calf raises.
3. Add two gate rules: same-site morning pain on three consecutive mornings is a
   tissue amber, and no overriding a pre-run amber.
4. Fix the week 13/14 inconsistency. Correct the dashboard's "no injuries" text.
5. Recharge the chest strap.
6. Defer two decisions, with criteria recorded as a `weekly_decision`: whether
   the 26 km target becomes time-based (decide after the Week 11 tune-up), and
   whether to run the formal §9 review now. Because the breaker couldn't have
   fired even when deserved, running the review voluntarily is the conservative
   choice.
