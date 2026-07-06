"""Business Insights Agent — a 3-agent ADK pipeline.

Agent 1 (query_planner): turns a natural-language business question into a
                          structured plan (which filters to apply).
Agent 2 (data_retrieval): calls the query_business_data tool using that plan.
Agent 3 (insight_generator): turns the retrieved rows/summary into a plain
                              -English business insight with a recommendation.

Root agent: a SequentialAgent that chains all three, so `adk run` /
`adk web` can execute the whole pipeline as one turn.
"""

import os

from google.adk.agents import Agent, SequentialAgent

from .tools import query_business_data

MODEL = "gemini-2.5-flash"

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")


def load_skill(filename: str) -> str:
    """Reads a SKILL.md file so its contents can be injected into an agent's
    instruction. Keeps the skill spec as the single source of truth instead
    of duplicating it inside the prompt string.
    """
    path = os.path.join(SKILLS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


DATA_RETRIEVAL_SKILL = load_skill("data_retrieval.md")

query_planner = Agent(
    name="query_planner",
    model=MODEL,
    description="Parses a natural-language business question into a structured filter plan.",
    instruction="""
You are a query planning agent for a sales analytics tool.

The dataset has these columns: sales_rep_name, team, client_name, effort_id,
lead_id, region (North/South/East/West), sale_type (New Business/Renewal/Upsell),
estimated_revenue, actual_revenue, submission_date. Each sales rep belongs to
exactly one team (Team Alpha, Team Beta, Team Gamma, Team Delta) — team is a
property of the rep, not something that varies row to row.

Given the user's question, output a short, clear plan describing exactly
which filters should be applied (sales_rep_name, team, client_name, region,
sale_type — any of which may be "none" if not mentioned) and what the user is
really asking for (e.g. "compare estimated vs actual revenue for a rep",
"find which team has the biggest revenue gap", "check a client's deal
history").

Keep the plan to 2-3 sentences. Do not answer the question yourself — that is
the next agent's job.
""",
)

data_retrieval = Agent(
    name="data_retrieval",
    model=MODEL,
    description="Retrieves the relevant rows and summary stats from the sales dataset.",
    instruction="""
You are a data retrieval agent. Read the plan produced by the previous agent
and call the `query_business_data` tool with the appropriate sales_rep_name,
team, client_name, region, and sale_type arguments (leave any as an empty
string if the plan doesn't specify them). Report back the tool's result
as-is, without adding commentary or analysis.

Below is the full skill spec for this capability — follow its gotchas and
output-shape notes exactly:

---
"""
    + DATA_RETRIEVAL_SKILL,
    tools=[query_business_data],
)

insight_generator = Agent(
    name="insight_generator",
    model=MODEL,
    description="Turns retrieved data into a plain-English business insight and recommendation.",
    instruction="""
You are a senior sales analyst. Using the data retrieved by the previous
agent, write a short insight (3-5 sentences) that:
1. States the key finding in plain English (no jargon).
2. Backs it up with 1-2 concrete numbers from the data — especially the gap
   or achievement rate between estimated_revenue and actual_revenue where
   relevant.
3. Ends with one actionable recommendation (e.g. which rep, client, or
   region needs follow-up).

If the data is empty, say so plainly and suggest the user broaden their
filters instead of inventing numbers.
""",
)

root_agent = SequentialAgent(
    name="business_insights_agent",
    sub_agents=[query_planner, data_retrieval, insight_generator],
    description="End-to-end pipeline: plan the query, retrieve the data, generate the insight.",
)
