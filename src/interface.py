import plotly.graph_objects as go
import streamlit as st

from core_metrics import build_weekly_volume_stats, get_garmin_metrics, get_lift_metrics, load_and_combine_data

st.set_page_config(page_title="Workout Metrics Dashboard", layout="wide")
st.title("🏋️‍♂️ Workout Analytics Dashboard")
st.markdown("Phase 1: Extensible Local Performance Metrics")
st.markdown(
    """
    <style>
        .programme-section {
            margin-top: 0.35rem;
            margin-bottom: 0.8rem;
        }
        .programme-heading {
            font-size: 1.08rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            color: #1f2937;
            margin: 0 0 0.35rem 0;
        }
        .panel-heading {
            font-size: 0.88rem;
            font-weight: 600;
            color: #374151;
            margin: 0 0 0.2rem 0;
        }
        div[data-testid="stPlotlyChart"] {
            margin-top: 0.05rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    garmin_df, lift_df = load_and_combine_data("data/workout_data.xlsx")
    lift_metrics = get_lift_metrics(lift_df)
    garmin_metrics = get_garmin_metrics(garmin_df)
except Exception as e:
    st.error(f"Error reading data/workout_data.xlsx. Details: {e}")
    st.stop()


def create_combo_chart(df, x_col, bar_col, line_col, title, xaxis_title="Month", yaxis_title="Volume"):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[bar_col],
            name="Volume",
            marker_color="#5B8FF9",
            opacity=0.8,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[line_col],
            mode="lines+markers",
            name="Trend",
            line={"color": "#ff7f0e", "width": 3},
            marker={"size": 7},
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.05, "x": 0},
        margin={"l": 30, "r": 20, "t": 40, "b": 30},
        height=260,
    )
    return fig


# Layout split into two high-level tabs
program_tab, activity_tab = st.tabs(["💪 LiftTrack Strength Analytics", "⌚ Garmin Activity Analytics"])

with program_tab:
    st.header("LiftTrack")

    if lift_df.empty:
        st.warning("No LiftTrack data found in the workbook.")
    else:
        programme_options = ["Programme 1", "Programme 2"]
        selected_programme = st.selectbox("Programme", programme_options, index=0)

        programme_df = lift_df[lift_df["Programme"] == selected_programme].copy()
        cycle_options = ["All Cycles"] + [str(cycle) for cycle in sorted(programme_df["Cycle"].dropna().unique().tolist())]
        if not cycle_options[1:]:
            cycle_options = ["All Cycles", "1"]
        selected_cycle = st.selectbox("Cycle", cycle_options, index=0)

        chart_df = programme_df.copy()
        if selected_cycle != "All Cycles":
            chart_df = chart_df[chart_df["Cycle"] == int(selected_cycle)]

        st.markdown("### Programme Overview")

        st.markdown('<div class="programme-section">', unsafe_allow_html=True)
        programme_one_col_1, programme_one_col_2 = st.columns(2)
        st.markdown('<div class="programme-heading">Programme One</div>', unsafe_allow_html=True)
        programme_one_df = lift_df[lift_df["Programme"] == "Programme 1"].copy()
        filtered_one = programme_one_df.copy()
        if selected_cycle != "All Cycles":
            filtered_one = filtered_one[filtered_one["Cycle"] == int(selected_cycle)]
        one_monthly = (
            filtered_one.groupby("Month_Name", as_index=False)
            .agg(Total_Volume=("Volume", "sum"), Set_Count=("Volume", "count"))
        )
        one_monthly["Avg_Volume_Per_Set"] = one_monthly["Total_Volume"] / one_monthly["Set_Count"].replace(0, 1)

        with programme_one_col_1:
            st.markdown('<div class="panel-heading">Average Volume per Set</div>', unsafe_allow_html=True)
            fig_avg_one = create_combo_chart(
                one_monthly,
                "Month_Name",
                "Avg_Volume_Per_Set",
                "Avg_Volume_Per_Set",
                title="Programme One Average Volume per Set",
                xaxis_title="Month",
                yaxis_title="Average Volume per Set",
            )
            st.plotly_chart(fig_avg_one, use_container_width=True)

        with programme_one_col_2:
            st.markdown('<div class="panel-heading">Total Volume per Cycle</div>', unsafe_allow_html=True)
            fig_total_one = create_combo_chart(
                one_monthly,
                "Month_Name",
                "Total_Volume",
                "Total_Volume",
                title="Programme One Total Volume per Cycle",
                xaxis_title="Month",
                yaxis_title="Total Volume",
            )
            st.plotly_chart(fig_total_one, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="programme-section">', unsafe_allow_html=True)
        programme_two_col_1, programme_two_col_2 = st.columns(2)
        st.markdown('<div class="programme-heading">Programme Two</div>', unsafe_allow_html=True)
        programme_two_df = lift_df[lift_df["Programme"] == "Programme 2"].copy()
        filtered_two = programme_two_df.copy()
        if selected_cycle != "All Cycles":
            filtered_two = filtered_two[filtered_two["Cycle"] == int(selected_cycle)]
        two_monthly = (
            filtered_two.groupby("Month_Name", as_index=False)
            .agg(Total_Volume=("Volume", "sum"), Set_Count=("Volume", "count"))
        )
        two_monthly["Avg_Volume_Per_Set"] = two_monthly["Total_Volume"] / two_monthly["Set_Count"].replace(0, 1)

        with programme_two_col_1:
            st.markdown('<div class="panel-heading">Average Volume per Set</div>', unsafe_allow_html=True)
            fig_avg_two = create_combo_chart(
                two_monthly,
                "Month_Name",
                "Avg_Volume_Per_Set",
                "Avg_Volume_Per_Set",
                title="Programme Two Average Volume per Set",
                xaxis_title="Month",
                yaxis_title="Average Volume per Set",
            )
            st.plotly_chart(fig_avg_two, use_container_width=True)

        with programme_two_col_2:
            st.markdown('<div class="panel-heading">Total Volume per Cycle</div>', unsafe_allow_html=True)
            fig_total_two = create_combo_chart(
                two_monthly,
                "Month_Name",
                "Total_Volume",
                "Total_Volume",
                title="Programme Two Total Volume per Cycle",
                xaxis_title="Month",
                yaxis_title="Total Volume",
            )
            st.plotly_chart(fig_total_two, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Exercise Deep Dive")

        exercise_programme_df = lift_df[lift_df["Programme"] == selected_programme].copy()
        exercise_options = sorted(exercise_programme_df["Exercise"].dropna().unique().tolist())
        selected_exercise = st.selectbox("Exercise", exercise_options, index=0 if exercise_options else None)

        if selected_exercise and exercise_options:
            exercise_df = exercise_programme_df[exercise_programme_df["Exercise"] == selected_exercise].copy()
            if selected_cycle != "All Cycles":
                exercise_df = exercise_df[exercise_df["Cycle"] == int(selected_cycle)]

            monthly_exercise = exercise_df.groupby("Month_Name", as_index=False)["Volume"].sum().rename(columns={"Volume": "Monthly_Volume"})
            weekly_exercise = exercise_df.groupby("Week", as_index=False)["Volume"].sum().rename(columns={"Volume": "Weekly_Volume"})

            ex_col_1, ex_col_2 = st.columns(2)
            with ex_col_1:
                st.subheader("Monthly Volume per Exercise")
                fig_month_ex = create_combo_chart(
                    monthly_exercise,
                    "Month_Name",
                    "Monthly_Volume",
                    "Monthly_Volume",
                    title=f"{selected_exercise} Monthly Volume",
                    xaxis_title="Month",
                    yaxis_title="Volume",
                )
                st.plotly_chart(fig_month_ex, use_container_width=True)

            with ex_col_2:
                st.subheader("Weekly Volume per Exercise")
                fig_week_ex = create_combo_chart(
                    weekly_exercise,
                    "Week",
                    "Weekly_Volume",
                    "Weekly_Volume",
                    title=f"{selected_exercise} Weekly Volume",
                    xaxis_title="Week",
                    yaxis_title="Volume",
                )
                st.plotly_chart(fig_week_ex, use_container_width=True)

        st.markdown("---")
        st.markdown("### Weekly Volume Stats")
        weekly_table = build_weekly_volume_stats(lift_df, programme=selected_programme, cycle=selected_cycle)
        st.dataframe(weekly_table, use_container_width=True, hide_index=True)

with activity_tab:
    st.header("Cardio, Intensity & Consistency Tracking")

    if garmin_df.empty:
        st.warning("No Garmin data found in the workbook.")
    else:
        st.metric(label="Historical Average Workouts per Month", value=f"{garmin_metrics['avg_workouts_per_month']:.1f}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Total Workouts per Month")
            import plotly.express as px

            fig_gar_month = px.bar(
                garmin_metrics["total_workouts_month"],
                x="Month_Name",
                y="Total_Workouts",
                text_auto=True,
                labels={"Total_Workouts": "Workout Count", "Month_Name": "Month"},
            )
            st.plotly_chart(fig_gar_month, use_container_width=True)
            st.dataframe(garmin_metrics["total_workouts_month"], use_container_width=True, hide_index=True)

            st.markdown("---")

            st.subheader("Average Heart Rate per Workout Type")
            fig_hr = px.bar(
                garmin_metrics["avg_hr_per_type"],
                x="Activity Type",
                y="Avg_Heart_Rate",
                text_auto=".1f",
                labels={"Avg_Heart_Rate": "Heart Rate (BPM)"},
            )
            st.plotly_chart(fig_hr, use_container_width=True)
            st.dataframe(garmin_metrics["avg_hr_per_type"], use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Average Workouts per Type per Week")
            fig_type_week = px.bar(
                garmin_metrics["avg_workouts_type_week"],
                x="Activity Type",
                y="Avg_Workouts_Per_Week",
                text_auto=".1f",
                labels={"Avg_Workouts_Per_Week": "Avg Weekly Frequency"},
            )
            st.plotly_chart(fig_type_week, use_container_width=True)
            st.dataframe(garmin_metrics["avg_workouts_type_week"], use_container_width=True, hide_index=True)