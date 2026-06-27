import pandas as pd
import numpy as np

def load_and_combine_data(file_path="data/workout_data.xlsx"):
    excel = pd.ExcelFile(file_path)
    garmin_sheets = []
    lift_sheets = []
    
    for sheet_name in excel.sheet_names:
        df = excel.parse(sheet_name)
        if "garmin" in sheet_name.lower():
            garmin_sheets.append(df)
        elif "lift" in sheet_name.lower() or "track" in sheet_name.lower():
            lift_sheets.append(df)
            
    garmin_df = pd.concat(garmin_sheets, ignore_index=True) if garmin_sheets else pd.DataFrame()
    lift_df = pd.concat(lift_sheets, ignore_index=True) if lift_sheets else pd.DataFrame()
    
    return preprocess_garmin(garmin_df), preprocess_lift(lift_df)

def preprocess_garmin(df):
    if df.empty: return df
    df.columns = df.columns.str.strip()
    
    # Force 'Week' to be capitalized for consistency
    if 'week' in df.columns: df.rename(columns={'week': 'Week'}, inplace=True)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month_Name'] = df['Date'].dt.strftime('%B %Y')
    
    if 'Activity Type' in df.columns:
        df['Activity Type'] = df['Activity Type'].replace('Cardio', 'HIIT')
    if 'Avg HR' in df.columns:
        df['Avg HR'] = pd.to_numeric(df['Avg HR'], errors='coerce')
    return df

def preprocess_lift(df):
    if df.empty: return df
    df.columns = df.columns.str.strip()
    
    # Force 'Week' to be capitalized for consistency
    if 'week' in df.columns: df.rename(columns={'week': 'Week'}, inplace=True)
    
    df['date'] = pd.to_datetime(df['date'])
    df['Month_Name'] = df['date'].dt.strftime('%B %Y')
    
    if all(col in df.columns for col in ['sets', 'reps', 'weight']):
        df['Calculated_Volume'] = df['sets'] * df['reps'] * df['weight']
    elif all(col in df.columns for col in ['reps', 'weight']):
        df['Calculated_Volume'] = df['reps'] * df['weight']
    else:
        df['Calculated_Volume'] = 0
    return df

def get_lift_metrics(lift_df):
    if lift_df.empty: return {}
    metrics = {}
    # Both calculations now strictly look for the standardized 'Week' column
    metrics['vol_per_exercise_week'] = lift_df.groupby(['exercise_display_name', 'Week'])['Calculated_Volume'].sum().reset_index()
    metrics['vol_per_exercise_month'] = lift_df.groupby(['exercise_display_name', 'Month_Name'])['Calculated_Volume'].sum().reset_index()
    metrics['vol_per_workout_week'] = lift_df.groupby(['workout_name', 'Week'])['Calculated_Volume'].sum().reset_index()
    metrics['vol_per_workout_month'] = lift_df.groupby(['workout_name', 'Month_Name'])['Calculated_Volume'].sum().reset_index()
    return metrics

def get_garmin_metrics(garmin_df):
    if garmin_df.empty: return {}
    metrics = {}
    workouts_per_month = garmin_df.groupby('Month_Name')['Date'].count().reset_index()
    workouts_per_month.columns = ['Month_Name', 'Total_Workouts']
    metrics['total_workouts_month'] = workouts_per_month
    metrics['avg_workouts_per_month'] = workouts_per_month['Total_Workouts'].mean()
    
    type_week_counts = garmin_df.groupby(['Activity Type', 'Week'])['Date'].count().reset_index()
    type_week_counts.columns = ['Activity Type', 'Week', 'Workout_Count']
    metrics['avg_workouts_type_week'] = type_week_counts.groupby('Activity Type')['Workout_Count'].mean().reset_index()
    metrics['avg_workouts_type_week'].columns = ['Activity Type', 'Avg_Workouts_Per_Week']
    
    metrics['avg_hr_per_type'] = garmin_df.groupby('Activity Type')['Avg HR'].mean().reset_index()
    metrics['avg_hr_per_type'].columns = ['Activity Type', 'Avg_Heart_Rate']
    return metrics