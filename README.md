# Business Insights Agent

A 3-agent pipeline built with Google's **Agent Development Kit (ADK)** that answers
natural-language questions over a sales/CRM dataset — built as the capstone project
for Google & Kaggle's *AI Agents: Intensive Vibe Coding* course.

Ask something like *"How is Team Delta doing on New Business deals?"* and the agent
plans the query, retrieves the matching data, and writes back a plain-English insight
with a concrete recommendation.

## Architecture

Three agents chained with ADK's `SequentialAgent`, each one's output feeding the next:

| Agent | Job |
|---|---|
| `query_planner` | Parses the question into a structured filter plan (rep, team, client, region, sale type) |
| `data_retrieval` | Calls a tool that filters the dataset by that plan and returns matching rows + summary stats |
| `insight_generator` | Turns the retrieved data into a plain-English insight with a recommendation |

```
User question
     │
     ▼
query_planner  ──►  data_retrieval  ──►  insight_generator
 (plans filters)   (calls the tool,     (writes the final,
                    reads the data)      plain-English answer)
```

No GCP project or billing account required — runs entirely on a Gemini API key from
[Google AI Studio](https://aistudio.google.com/).

## Dataset

`data/business_data.csv` — a dummy CRM/sales dataset (not real company data):

`sales_rep_name, team, client_name, effort_id, lead_id, region, sale_type, estimated_revenue, actual_revenue, submission_date`

Each sales rep belongs to exactly one team.

## Quickstart

```bash
git clone <this-repo-url>
cd business-insights-agent
cp .env.example .env        # then paste your Gemini API key into .env
pip install -r requirements.txt
adk web
```

`adk web` opens a local browser UI where you can chat with `root_agent` and watch
all three sub-agents fire in sequence. Try:

- *"How is Team Delta doing on New Business deals?"*
- *"What's the revenue gap for Ananya Rao's deals?"*
- *"Give me a summary of Vantage Logistics as a client."*


## Project structure

```
business_insights_agent/
├── agent.py               # the 3 agents + SequentialAgent wiring
└── tools.py                # query_business_data — the data retrieval tool

skills/
└── data_retrieval.md       # skill spec for the retrieval capability
                             # (loaded into the agent's instruction at build time,
                             #  kept separate from the prompt as the source of truth)


data/business_data.csv      # dummy sales/CRM dataset
requirements.txt
.env.example
```

## Why a `SKILL.md`?

ADK doesn't auto-load skill files the way some coding agents do. `skills/data_retrieval.md`
is a deliberate, human- and agent-readable spec for the retrieval capability — its inputs,
output shape, and edge cases — kept separate from the agent's prompt so the logic can be
audited or reused without re-deriving it from code. `agent.py` reads this file at build
time and injects it into the `data_retrieval` agent's instruction.


## Notes

- If `adk web` / `adk run` or any import errors out, it's usually just an ADK
  version/API mismatch — the CLI shifts between releases.
- `.env` is git-ignored; never commit your actual API key. Use `.env.example` as the template.
