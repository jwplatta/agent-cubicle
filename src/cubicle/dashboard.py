import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from dashboard_queries import (
    get_daily_sessions,
    get_model_distribution,
    get_repo_distribution,
    get_session_events,
    get_sessions,
    get_summary_stats,
    get_tool_usage,
    get_usage_heatmap,
)

st.set_page_config(
    page_title="Cubicle Agent Dashboard",
    page_icon="🤖",
    layout="wide",
)


page = st.sidebar.radio("Navigate", ["Overview", "Sessions"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption("Cubicle Telemetry Dashboard")


# ---------------------------------------------------------------------------
# OVERVIEW PAGE
# ---------------------------------------------------------------------------

def render_overview():
    stats = get_summary_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sessions", f"{stats['total_sessions']:,}")
    c2.metric("Total Tool Calls", f"{stats['total_tool_calls']:,}")
    c3.metric("Total Prompts", f"{stats['total_prompts']:,}")
    c4.metric("Avg Session Duration", f"{stats['avg_duration_min']} min")

    st.markdown("---")

    # Daily activity
    st.subheader("Daily Activity (last 30 days)")
    daily = get_daily_sessions(days=30)
    if not daily.empty:
        fig = px.bar(
            daily,
            x="date",
            y="sessions",
            color="model",
            labels={"date": "Date", "sessions": "Sessions", "model": "Model"},
            barmode="stack",
        )
        fig.update_layout(margin=dict(t=10, b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No session data available.")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # Model/agent mix
    with col_left:
        st.subheader("Model Mix (by sessions)")
        model_dist = get_model_distribution()
        if not model_dist.empty:
            fig = px.pie(
                model_dist,
                names="model",
                values="sessions",
                hole=0.4,
            )
            fig.update_layout(margin=dict(t=10, b=10), height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Model Breakdown")
            display = model_dist[["model", "sessions", "tool_calls"]].rename(columns={
                "model": "Model", "sessions": "Sessions", "tool_calls": "Tool Calls"
            })
            st.dataframe(display, hide_index=True, use_container_width=True)

    # Top repos
    with col_right:
        st.subheader("Top Repos by Tool Calls")
        repos = get_repo_distribution()
        if not repos.empty:
            fig = px.bar(
                repos.sort_values("tool_calls"),
                x="tool_calls",
                y="repo",
                orientation="h",
                labels={"tool_calls": "Tool Calls", "repo": "Repo"},
                color_discrete_sequence=["#3B82F6"],
            )
            fig.update_layout(margin=dict(t=10, b=10), height=400)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col_tools, col_heat = st.columns(2)

    # Tool usage
    with col_tools:
        st.subheader("Top Tools Used")
        tools = get_tool_usage()
        if not tools.empty:
            fig = px.bar(
                tools.head(15).sort_values("count"),
                x="count",
                y="tool_name",
                orientation="h",
                labels={"count": "Calls", "tool_name": "Tool"},
                color_discrete_sequence=["#10B981"],
            )
            fig.update_layout(margin=dict(t=10, b=10), height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Usage heatmap
    with col_heat:
        st.subheader("Usage Heatmap (day × hour)")
        heatmap_df = get_usage_heatmap()
        if not heatmap_df.empty:
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            heatmap_df["day_name"] = heatmap_df["dow"].map(lambda d: day_names[d])
            pivot = heatmap_df.pivot_table(index="day_name", columns="hour", values="sessions", fill_value=0)
            pivot = pivot.reindex([d for d in day_names if d in pivot.index])
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=[str(h) for h in pivot.columns],
                y=pivot.index.tolist(),
                colorscale="Blues",
                showscale=True,
            ))
            fig.update_layout(
                margin=dict(t=10, b=10),
                height=400,
                xaxis_title="Hour of Day",
                yaxis_title="Day of Week",
            )
            st.plotly_chart(fig, use_container_width=True)



# ---------------------------------------------------------------------------
# SESSIONS PAGE
# ---------------------------------------------------------------------------

def render_sessions():
    st.title("Sessions")

    sessions = get_sessions()
    if sessions.empty:
        st.info("No sessions found.")
        return

    # Filter controls
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        models = ["All"] + sorted(sessions["model"].dropna().unique().tolist())
        selected_model = st.selectbox("Model", models)
    with col_f2:
        repos = ["All"] + sorted(sessions["repo"].unique().tolist())
        selected_repo = st.selectbox("Repo", repos)
    with col_f3:
        min_tools = st.number_input("Min tool calls", min_value=0, value=0)

    filtered = sessions.copy()
    if selected_model != "All":
        filtered = filtered[filtered["model"] == selected_model]
    if selected_repo != "All":
        filtered = filtered[filtered["repo"] == selected_repo]
    filtered = filtered[filtered["tool_count"] >= min_tools]

    # Table columns
    display_cols = ["session_short", "model", "repo", "start_time", "duration_min", "tool_count", "prompt_count", "permission_count"]
    display = filtered[display_cols].rename(columns={
        "session_short": "Session",
        "model": "Model",
        "repo": "Repo",
        "start_time": "Started",
        "duration_min": "Duration (min)",
        "tool_count": "Tools",
        "prompt_count": "Prompts",
        "permission_count": "Permissions",
    })

    st.caption(f"{len(filtered)} sessions")
    selection = st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Session drill-down
    selected_rows = selection.selection.rows if selection and selection.selection else []
    if selected_rows:
        idx = selected_rows[0]
        session_row = filtered.iloc[idx]
        session_id = session_row["session_id"]

        st.markdown("---")
        st.subheader(f"Session: {session_id}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Model", session_row["model"] or "Unknown")
        m2.metric("Repo", session_row["repo"])
        m3.metric("Duration", f"{session_row['duration_min']} min")
        m4.metric("Tool Calls", int(session_row["tool_count"]))

        st.markdown("**Event Timeline**")
        events = get_session_events(session_id)

        if events.empty:
            st.info("No events found for this session.")
            return

        for _, ev in events.iterrows():
            norm = ev["norm_event"]

            if norm == "userpromptsubmit" and ev["prompt_text"]:
                with st.chat_message("user"):
                    st.write(ev["prompt_text"])
                    st.caption(ev["timestamp"])

            elif norm in ("turncomplete", "stop") and ev["assistant_message"]:
                with st.chat_message("assistant"):
                    st.write(ev["assistant_message"])
                    st.caption(ev["timestamp"])

            elif norm == "pretooluse" and ev["tool_name"]:
                with st.expander(f"🔧 {ev['tool_name']}  —  {ev['timestamp']}", expanded=False):
                    if ev["tool_input"]:
                        st.code(ev["tool_input"], language="json")

            elif norm == "posttooluse" and ev["tool_response"]:
                with st.expander(f"↩ {ev['tool_name'] or 'tool'} response  —  {ev['timestamp']}", expanded=False):
                    st.text(ev["tool_response"])

            elif norm in ("notification", "permissionrequest") and ev["notification_msg"]:
                st.info(f"**{ev['event_type']}**: {ev['notification_msg']}  `{ev['timestamp']}`")

            elif norm == "session_start":
                st.success(f"Session started  `{ev['timestamp']}`  cwd: `{ev['cwd'] or ''}`")

            elif norm in ("agent_stop", "session_end", "sessionend"):
                st.warning(f"Session ended  `{ev['timestamp']}`")


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------

if page == "Overview":
    render_overview()
else:
    render_sessions()
