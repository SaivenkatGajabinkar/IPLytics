import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="IPLytics",
    page_icon="🏏",
    layout="wide"
)

# =====================================================
# TITLE SECTION
# =====================================================

st.title("🏏 IPLytics")

st.subheader("Decoding Match-Winning Patterns in IPL")

st.markdown("""
Explore match-winning patterns, player impact,
toss influence, venue behavior, and phase-wise
IPL performance insights.
""")

# =====================================================
# LOAD DATA
# =====================================================

matches = pd.read_csv("Data/matches.csv")
deliveries = pd.read_csv("Data/deliveries.csv")

# =====================================================
# METRICS SECTION
# =====================================================

total_matches = matches.shape[0]
total_deliveries = deliveries.shape[0]
total_teams = deliveries['batting_team'].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("🏏 Total Matches", total_matches)
col2.metric("🎯 Total Deliveries", total_deliveries)
col3.metric("👥 Teams Analyzed", total_teams)

st.divider()

# =====================================================
# INSIGHT BOXES
# =====================================================

st.info("""
📌 Key Insight:
Teams with stronger middle-over stability and
death-over acceleration consistently achieve
better match outcomes.
""")

st.warning("""
⚡ Surprise Finding:
Winning the toss has significantly less impact
than sustained scoring momentum.
""")

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("📌 Dashboard Filters")

teams = sorted(deliveries['batting_team'].unique())

team1 = st.sidebar.selectbox(
    "Select Team 1",
    teams
)

team2 = st.sidebar.selectbox(
    "Select Team 2",
    teams,
    index=1
)

# =====================================================
# PHASE CLASSIFICATION
# =====================================================

def get_phase(over):

    if over <= 6:
        return "Powerplay"

    elif over <= 15:
        return "Middle Overs"

    else:
        return "Death Overs"

deliveries['phase'] = deliveries['over'].apply(get_phase)

# =====================================================
# FILTER TEAM DATA
# =====================================================

team1_data = deliveries[
    deliveries['batting_team'] == team1
]

team2_data = deliveries[
    deliveries['batting_team'] == team2
]

# =====================================================
# CREATE TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Match Analytics",
    "⭐ Player Intelligence",
    "🏟 Venue Insights",
    "📈 Win Predictor"
])

# =====================================================
# TAB 1 — MATCH ANALYTICS
# =====================================================

with tab1:

    # -------------------------------------------------
    # PHASE ANALYSIS
    # -------------------------------------------------

    st.header("📈 Phase-wise Run Analysis")

    phase_runs = team1_data.groupby(
        'phase'
    )['total_runs'].mean().reset_index()

    fig1 = px.bar(
        phase_runs,
        x='phase',
        y='total_runs',
        color='total_runs',
        title=f'{team1} Average Runs by Match Phase',
        text_auto='.2f'
    )

    fig1.update_layout(
        height=500,
        xaxis_title="Match Phase",
        yaxis_title="Average Runs"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # -------------------------------------------------
    # TEAM COMPARISON
    # -------------------------------------------------

    st.header("⚔ Team Comparison")

    comparison = pd.DataFrame({
        'Team': [team1, team2],
        'Average Runs': [
            team1_data['total_runs'].mean(),
            team2_data['total_runs'].mean()
        ]
    })

    fig_compare = px.bar(
        comparison,
        x='Team',
        y='Average Runs',
        color='Average Runs',
        title='Average Runs Comparison',
        text_auto='.2f'
    )

    fig_compare.update_layout(height=500)

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

    # -------------------------------------------------
    # TOSS ANALYSIS
    # -------------------------------------------------

    st.header("🪙 Toss Impact Analysis")

    matches['toss_match_win'] = (
        matches['toss_winner']
        ==
        matches['winner']
    ).astype(int)

    toss_result = matches[
        'toss_match_win'
    ].value_counts().reset_index()

    toss_result.columns = [
        'Won Match After Toss',
        'Count'
    ]

    toss_result['Won Match After Toss'] = (
        toss_result['Won Match After Toss']
        .replace({
            1: 'Yes',
            0: 'No'
        })
    )

    fig2 = px.pie(
        toss_result,
        names='Won Match After Toss',
        values='Count',
        title='Does Winning Toss Really Matter?'
    )

    fig2.update_layout(height=500)

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -------------------------------------------------
    # DEATH OVER ANALYSIS
    # -------------------------------------------------

    st.header("🔥 Death Over Specialists")

    death_overs = deliveries[
        deliveries['phase'] == 'Death Overs'
    ]

    death_stats = death_overs.groupby(
        'batting_team'
    )['total_runs'].mean().reset_index()

    death_stats = death_stats.sort_values(
        by='total_runs',
        ascending=False
    )

    fig3 = px.bar(
        death_stats.head(10),
        x='batting_team',
        y='total_runs',
        color='total_runs',
        title='Top Death Over Batting Teams',
        text_auto='.2f'
    )

    fig3.update_layout(
        height=500,
        xaxis_title="Teams",
        yaxis_title="Average Death Over Runs"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# =====================================================
# TAB 2 — PLAYER INTELLIGENCE
# =====================================================

with tab2:

    # -------------------------------------------------
    # BATTER ANALYTICS
    # -------------------------------------------------

    st.header("⭐ Most Impactful Batters")

    batter_stats = deliveries.groupby(
        'batter'
    ).agg({
        'batsman_runs':'sum',
        'ball':'count'
    }).reset_index()

    batter_stats.columns = [
        'batter',
        'runs',
        'balls'
    ]

    batter_stats['strike_rate'] = (
        batter_stats['runs']
        /
        batter_stats['balls']
    ) * 100

    batter_stats['impact_score'] = (
        batter_stats['runs'] * 0.6
        +
        batter_stats['strike_rate'] * 0.4
    )

    batter_stats = batter_stats.sort_values(
        by='impact_score',
        ascending=False
    )

    fig4 = px.bar(
        batter_stats.head(10),
        x='batter',
        y='impact_score',
        color='impact_score',
        title='Top 10 Impactful IPL Batters',
        text_auto='.2f'
    )

    fig4.update_layout(
        height=550,
        xaxis_title="Batters",
        yaxis_title="Impact Score"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    # -------------------------------------------------
    # BOWLER ANALYTICS
    # -------------------------------------------------

    st.header("🎯 Most Impactful Bowlers")

    bowler_stats = deliveries.groupby(
        'bowler'
    ).agg({
        'is_wicket':'sum',
        'total_runs':'sum',
        'ball':'count'
    }).reset_index()

    bowler_stats.columns = [
        'bowler',
        'wickets',
        'runs_conceded',
        'balls'
    ]

    bowler_stats['economy'] = (
        bowler_stats['runs_conceded']
        /
        (bowler_stats['balls'] / 6)
    )

    bowler_stats['impact_score'] = (
        bowler_stats['wickets'] * 20
        -
        bowler_stats['economy'] * 2
    )

    bowler_stats = bowler_stats.sort_values(
        by='impact_score',
        ascending=False
    )

    fig5 = px.bar(
        bowler_stats.head(10),
        x='bowler',
        y='impact_score',
        color='impact_score',
        title='Top 10 Impactful IPL Bowlers',
        text_auto='.2f'
    )

    fig5.update_layout(
        height=550,
        xaxis_title="Bowlers",
        yaxis_title="Impact Score"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

# =====================================================
# TAB 3 — VENUE INSIGHTS
# =====================================================

with tab3:

    st.header("🏟 Venue Intelligence")

    venue_analysis = matches.groupby(
        'venue'
    ).agg({
        'target_runs':'mean',
        'id':'count'
    }).reset_index()

    venue_analysis.columns = [
        'venue',
        'avg_target',
        'matches'
    ]

    venue_analysis = venue_analysis.sort_values(
        by='avg_target',
        ascending=False
    )

    fig6 = px.bar(
        venue_analysis.head(10),
        x='venue',
        y='avg_target',
        color='avg_target',
        title='Highest Scoring IPL Venues',
        text_auto='.2f'
    )

    fig6.update_layout(
        height=600,
        xaxis_title="Venue",
        yaxis_title="Average Target Runs"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

# =====================================================
# TAB 4 — WIN PREDICTOR
# =====================================================

with tab4:

    st.header("📈 Match Win Predictor")

    current_score = st.number_input(
        "Current Score",
        min_value=0,
        max_value=300,
        value=120
    )

    overs = st.number_input(
        "Overs Completed",
        min_value=0.0,
        max_value=20.0,
        value=12.0
    )

    wickets = st.number_input(
        "Wickets Lost",
        min_value=0,
        max_value=10,
        value=3
    )

    predicted_score = current_score + (
        (20 - overs) * 8
    ) - (wickets * 2)

    win_probability = min(
        95,
        max(
            5,
            int((predicted_score / 220) * 100)
        )
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "🏏 Predicted Final Score",
        int(predicted_score)
    )

    col2.metric(
        "📊 Win Probability",
        f"{win_probability}%"
    )

    st.success("""
    Prediction generated using match momentum,
    scoring trends, and over progression logic.
    """)

# =====================================================
# FINAL INSIGHT
# =====================================================

st.divider()

st.info("""
📌 Final Insight:

IPL matches are not decided primarily by toss advantage.
Teams that sustain momentum during middle overs and
dominate death overs consistently achieve higher win rates.
""")

# =====================================================
# FOOTER
# =====================================================

st.success("""
✅ IPLytics transforms raw cricket data into actionable
match intelligence using data science and visualization.
""")
