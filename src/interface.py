import streamlit as st
import plotly.express as px
from core_metrics import load_and_combine_data, get_lift_metrics, get_garmin_metrics

# Set up page styling
st.set_page_config(page_title="Workout Metrics Dashboard", layout="wide")
st.title("🏋️‍♂️ Workout Analytics Dashboard")
st.markdown("Phase 1: Extensible Local Performance Metrics")

# Load and process the raw workbook data
try:
    garmin_df, lift_df = load_and_combine_data()
    lift_metrics = get_lift_metrics(lift_df)
    garmin_metrics = get_garmin_metrics(garmin_df)
except Exception as e:
    st.error(f"Error reading 'data/workout_data.xlsx'. Make sure the file exists and is closed. Details: {e}")
    st.stop()

# Layout split into two high-level tabs
tab1, tab2 = st.tabs(["💪 LiftTrack Strength Analytics", "⌚ Garmin Activity Analytics"])

# ==========================================
# TAB 1: LIFTTRACK STRENGTH ANALYTICS
# ==========================================
with tab1:
    st.header("Strength Progression & Volume")
    
    if lift_df.empty:
        st.warning("No LiftTrack data found in the workbook.")
    else:
        # Split layout into two columns for side-by-side analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Volume per Exercise")
            fig_ex_month = px.bar(
                lift_metrics['vol_per_exercise_month'], 
                x='Month_Name', 
                y='Calculated_Volume', 
                color='exercise_display_name',
                barmode='group',
                labels={'Calculated_Volume': 'Total Volume', 'Month_Name': 'Month'}
            )
            st.plotly_chart(fig_ex_month, use_container_width=True)
            st.dataframe(lift_metrics['vol_per_exercise_month'], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            st.subheader("Monthly Volume per Workout Plan")
            fig_wk_month = px.bar(
                lift_metrics['vol_per_workout_month'], 
                x='Month_Name', 
                y='Calculated_Volume', 
                color='workout_name',
                barmode='group',
                labels={'Calculated_Volume': 'Total Volume', 'Month_Name': 'Month'}
            )
            st.plotly_chart(fig_wk_month, use_container_width=True)
            st.dataframe(lift_metrics['vol_per_workout_month'], use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Weekly Volume per Exercise")
            fig_ex_week = px.bar(
                lift_metrics['vol_per_exercise_week'], 
                x='Week', # <-- Fixed casing here
                y='Calculated_Volume', 
                color='exercise_display_name',
                barmode='group',
                labels={'Calculated_Volume': 'Total Volume', 'Week': 'Week Number'}
            )
            st.plotly_chart(fig_ex_week, use_container_width=True)
            st.dataframe(lift_metrics['vol_per_exercise_week'], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            st.subheader("Weekly Volume per Workout Plan")
            fig_wk_week = px.bar(
                lift_metrics['vol_per_workout_week'], 
                x='Week', # <-- Fixed casing here
                y='Calculated_Volume', 
                color='workout_name',
                barmode='group',
                labels={'Calculated_Volume': 'Total Volume', 'Week': 'Week Number'}
            )
            st.plotly_chart(fig_wk_week, use_container_width=True)
            st.dataframe(lift_metrics['vol_per_workout_week'], use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: GARMIN ACTIVITY ANALYTICS
# ==========================================
with tab2:
    st.header("Cardio, Intensity & Consistency Tracking")
    
    if garmin_df.empty:
        st.warning("No Garmin data found in the workbook.")
    else:
        # High-level consistency KPI metric box
        st.metric(
            label="Historical Average Workouts per Month", 
            value=f"{garmin_metrics['avg_workouts_per_month']:.1f}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total Workouts per Month")
            fig_gar_month = px.bar(
                garmin_metrics['total_workouts_month'],
                x='Month_Name',
                y='Total_Workouts',
                text_auto=True,
                labels={'Total_Workouts': 'Workout Count', 'Month_Name': 'Month'}
            )
            st.plotly_chart(fig_gar_month, use_container_width=True)
            st.dataframe(garmin_metrics['total_workouts_month'], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            st.subheader("Average Heart Rate per Workout Type")
            fig_hr = px.bar(
                garmin_metrics['avg_hr_per_type'],
                x='Activity Type',
                y='Avg_Heart_Rate',
                text_auto='.1f',
                labels={'Avg_Heart_Rate': 'Heart Rate (BPM)'}
            )
            st.plotly_chart(fig_hr, use_container_width=True)
            st.dataframe(garmin_metrics['avg_hr_per_type'], use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Average Workouts per Type per Week")
            fig_type_week = px.bar(
                garmin_metrics['avg_workouts_type_week'],
                x='Activity Type',
                y='Avg_Workouts_Per_Week',
                text_auto='.1f',
                labels={'Avg_Workouts_Per_Week': 'Avg Weekly Frequency'}
            )
            st.plotly_chart(fig_type_week, use_container_width=True)
            st.dataframe(garmin_metrics['avg_workouts_type_week'], use_container_width=True, hide_index=True)