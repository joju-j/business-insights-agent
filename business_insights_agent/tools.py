"""Tools used by the Business Insights Agent."""

import os
import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "business_data.csv")


def query_business_data(
    sales_rep_name: str = "",
    team: str = "",
    client_name: str = "",
    region: str = "",
    sale_type: str = "",
) -> dict:
    """Loads the sales dataset and filters it by optional criteria.

    Args:
        sales_rep_name: Filter to a specific sales rep. Leave empty for all reps.
        team: Filter to a specific team (each rep belongs to exactly one team).
            Leave empty for all teams.
        client_name: Filter to a specific client. Leave empty for all clients.
        region: One of North, South, East, West. Leave empty for all regions.
        sale_type: One of New Business, Renewal, Upsell. Leave empty for all types.

    Returns:
        A dict with the matching rows and precomputed summary stats (including
        the gap between estimated and actual revenue), so the insight
        generation agent doesn't have to do arithmetic itself.
    """
    df = pd.read_csv(DATA_PATH)

    if sales_rep_name:
        df = df[df["sales_rep_name"].str.lower() == sales_rep_name.lower()]
    if team:
        df = df[df["team"].str.lower() == team.lower()]
    if client_name:
        df = df[df["client_name"].str.lower() == client_name.lower()]
    if region:
        df = df[df["region"].str.lower() == region.lower()]
    if sale_type:
        df = df[df["sale_type"].str.lower() == sale_type.lower()]

    if df.empty:
        return {"row_count": 0, "rows": [], "summary": "No matching rows found."}

    total_estimated = float(df["estimated_revenue"].sum())
    total_actual = float(df["actual_revenue"].sum())

    summary = {
        "row_count": len(df),
        "total_estimated_revenue": round(total_estimated, 2),
        "total_actual_revenue": round(total_actual, 2),
        "revenue_gap": round(total_estimated - total_actual, 2),
        "achievement_rate_pct": round((total_actual / total_estimated) * 100, 1)
        if total_estimated
        else None,
        "distinct_clients": int(df["client_name"].nunique()),
        "distinct_reps": int(df["sales_rep_name"].nunique()),
        "distinct_teams": int(df["team"].nunique()),
    }

    return {
        "row_count": len(df),
        "rows": df.to_dict(orient="records"),
        "summary": summary,
    }
