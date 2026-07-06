# Skill: Sales Data Retrieval

## What this skill does
Filters the sales/CRM dataset (`data/business_data.csv`) by any combination of
sales rep, team, client, region, or sale type, and returns both the matching
rows and precomputed summary stats (total estimated vs actual revenue, revenue
gap, achievement rate, distinct client/rep/team counts).

## When to use it
Use this skill whenever the user's question requires looking at actual data
rather than general reasoning — e.g. "how is X rep doing", "which team is
underperforming", "show me Y client's deal history". Do not use it for
questions that don't reference the dataset at all.

## Inputs
- `sales_rep_name` (optional) — exact name, e.g. "Ananya Rao"
- `team` (optional) — exact team name, e.g. "Team Alpha". Each rep belongs to
  exactly one team (it's a property of the rep, not the deal), so filtering
  by team is equivalent to filtering by "all reps on that team."
- `client_name` (optional) — exact name, e.g. "Vantage Logistics"
- `region` (optional) — one of North, South, East, West
- `sale_type` (optional) — one of New Business, Renewal, Upsell

Leave any field empty to not filter on it. Filters are combined with AND, not OR.

## Output shape
```json
{
  "row_count": 3,
  "rows": [ ... raw matching rows ... ],
  "summary": {
    "total_estimated_revenue": 123000.0,
    "total_actual_revenue": 118000.0,
    "revenue_gap": 5000.0,
    "achievement_rate_pct": 95.9,
    "distinct_clients": 2,
    "distinct_reps": 1,
    "distinct_teams": 1
  }
}
```

## Gotchas
- Field matching is case-insensitive but must otherwise be exact — "north"
  works, "northern region" does not. If a plan produces a fuzzy value, the
  agent should fall back to leaving that filter empty rather than guessing.
- `team` is a property of the rep, not the deal — every row for a given rep
  always has the same team. Don't treat team as something that could vary
  within one rep's rows.
- If `row_count` is 0, don't fabricate numbers — say plainly that no rows
  matched and suggest broadening the filters.
- `achievement_rate_pct` is `None` when `total_estimated_revenue` is 0 (avoid
  divide-by-zero) — handle that case in the write-up rather than crashing.

## Where it's implemented
`business_insights_agent/tools.py` → `query_business_data()`. The
`data_retrieval` agent in `agent.py` is the one that calls it.

## Why a SKILL.md at all
ADK doesn't auto-load skill files the way some coding agents do — this file
is a deliberate, human- and agent-readable spec for the capability, kept
separate from the prompt itself. It's here so the retrieval logic can be
audited, reused, or handed to a different agent without re-deriving what it
does from code. This is the same "skills" idea from Day 3 of the course
(context engineering / skills / memory), just applied by hand since ADK
doesn't ship the mechanism natively.
