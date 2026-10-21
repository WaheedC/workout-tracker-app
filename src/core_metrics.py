import re

import numpy as np
import pandas as pd


def _normalize_column_name(column_name):
    return re.sub(r"[^a-z0-9]+", "_", str(column_name).strip().lower()).strip("_")


def _programme_from_value(value):
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip()
    if not text:
        return "Unknown"
    match = re.search(r"(?i)\bP([12])\b", text)
    if match:
        return f"Programme {match.group(1)}"
    if text.lower().startswith("programme"):
        return text.title()
    return text


def _canonicalize_lift_columns(df):
    if df.empty:
        return df

    rename_map = {
        "programme_name": "Programme",
        "program": "Programme",
        "programme": "Programme",
        "cycle_number": "Cycle",
        "cycle": "Cycle",
        "week_number": "Week",
        "week": "Week",
        "date": "Date",
        "exercise_name": "Exercise",
        "exercise": "Exercise",
        "exercise_display_name": "Exercise",
        "exercise_display": "Exercise",
        "reps": "Reps",
        "rep_count": "Reps",
        "weight_kg": "Weight",
        "weight": "Weight",
        "load_kg": "Weight",
        "load": "Weight",
        "volume": "Volume",
        "calculated_volume": "Volume",
        "total_volume": "Volume",
    }

    cleaned = {str(col).strip(): col for col in df.columns}
    for current_name, canonical in rename_map.items():
        if current_name in cleaned and canonical not in df.columns:
            df.rename(columns={cleaned[current_name]: canonical}, inplace=True)

    df.columns = [str(col).strip() for col in df.columns]
    return df


def _derive_week_and_cycle(df):
    if df.empty:
        return df

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if "Programme" not in df.columns:
        df["Programme"] = "Unknown"

    if "Week" not in df.columns:
        df["Week"] = np.nan
        for programme_value, group in df.groupby("Programme", sort=False):
            group_index = group.index
            valid_dates = group["Date"].notna()
            if not valid_dates.any():
                continue
            base_date = group.loc[valid_dates, "Date"].min()
            deltas = (group["Date"] - base_date).dt.days
            df.loc[group_index, "Week"] = ((deltas // 7) + 1).astype(int)

    if "Cycle" not in df.columns:
        if df["Week"].notna().any():
            df["Cycle"] = ((pd.to_numeric(df["Week"], errors="coerce") - 1) // 10 + 1).astype(float)
        else:
            df["Cycle"] = 1

    df["Week"] = pd.to_numeric(df["Week"], errors="coerce").fillna(1).astype(int)
    df["Cycle"] = pd.to_numeric(df["Cycle"], errors="coerce").fillna(1).astype(int)
    return df


def load_and_combine_data(file_path="data/workout_data.xlsx"):
    workbook_path = file_path or "data/workout_data.xlsx"
    workbook_path = str(workbook_path)

    if not pd.io.common.file_exists(workbook_path):
        raise FileNotFoundError(f"Workbook not found: {workbook_path}")

    excel = pd.ExcelFile(workbook_path, engine="openpyxl")
    garmin_frames = []
    lift_frames = []

    for sheet_name in excel.sheet_names:
        df = excel.parse(sheet_name)
        if df.empty:
            continue
        df.columns = [str(col).strip() for col in df.columns]
        if "garmin" in sheet_name.lower():
            garmin_frames.append(df)
        elif "lift" in sheet_name.lower() or "track" in sheet_name.lower():
            lift_frames.append(df)
        else:
            lift_frames.append(df)

    garmin_df = pd.concat(garmin_frames, ignore_index=True) if garmin_frames else pd.DataFrame()
    lift_df = pd.concat(lift_frames, ignore_index=True) if lift_frames else pd.DataFrame()
    return preprocess_garmin(garmin_df), preprocess_lift(lift_df)


def preprocess_garmin(df):
    if df.empty:
        return df
    df = df.copy()
    df.columns = df.columns.map(str).map(str.strip)

    if "week" in {str(col).lower() for col in df.columns}:
        for col in list(df.columns):
            if str(col).lower() == "week":
                df.rename(columns={col: "Week"}, inplace=True)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    elif "date" in df.columns:
        df["Date"] = pd.to_datetime(df["date"], errors="coerce")

    if "Date" in df.columns:
        df["Month_Name"] = df["Date"].dt.strftime("%b %Y")
    return df


def preprocess_lift(df):
    if df.empty:
        return df

    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    df = _canonicalize_lift_columns(df)

    exact_aliases = {
        "Programme": ["Programme", "programme", "Program", "program", "Programme Name", "Programme_Name"],
        "Cycle": ["Cycle", "cycle", "Cycle Number", "Cycle_Number"],
        "Week": ["Week", "week", "Week Number", "Week_Number"],
        "Date": ["Date", "date"],
        "Exercise": ["Exercise", "exercise", "Exercise Name", "Exercise_Name", "exercise_display_name"],
        "Sets": ["Sets", "sets"],
        "Reps": ["Reps", "reps", "Rep", "rep_count"],
        "Weight": ["Weight", "weight", "Weight Kg", "Weight_kg", "Load", "load", "Load Kg", "Load_kg"],
        "Volume": ["Volume", "volume", "Calculated Volume", "Calculated_Volume", "Total Volume", "Total_Volume"],
    }

    for canonical, aliases in exact_aliases.items():
        match = next((alias for alias in aliases if alias in df.columns), None)
        if match and canonical not in df.columns:
            df.rename(columns={match: canonical}, inplace=True)

    if "Programme" not in df.columns and "workout_name" in df.columns:
        df["Programme"] = df["workout_name"].map(_programme_from_value)
    if "Exercise" not in df.columns and "exercise_name" in df.columns:
        df.rename(columns={"exercise_name": "Exercise"}, inplace=True)
    if "Reps" not in df.columns and "reps" in df.columns:
        df.rename(columns={"reps": "Reps"}, inplace=True)
    if "Weight" not in df.columns and "weight" in df.columns:
        df.rename(columns={"weight": "Weight"}, inplace=True)
    if "Volume" not in df.columns and "calculated_volume" in df.columns:
        df.rename(columns={"calculated_volume": "Volume"}, inplace=True)

    if "Sets" in df.columns:
        df["Sets"] = pd.to_numeric(df["Sets"], errors="coerce").fillna(1)
    if "Reps" in df.columns:
        df["Reps"] = pd.to_numeric(df["Reps"], errors="coerce").fillna(0)
    if "Weight" in df.columns:
        df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce").fillna(0)

    if "Volume" in df.columns:
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
    else:
        df["Volume"] = np.nan

    if ("Sets" in df.columns) and ("Reps" in df.columns) and ("Weight" in df.columns):
        df["Volume"] = df["Volume"].fillna(df["Sets"] * df["Reps"] * df["Weight"])
    elif ("Reps" in df.columns) and ("Weight" in df.columns):
        df["Volume"] = df["Volume"].fillna(df["Reps"] * df["Weight"])

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Month_Name"] = df["Date"].dt.strftime("%b %Y") if "Date" in df.columns else "Unknown"
    if "Week" not in df.columns:
        df["Week"] = 1
    if "Cycle" not in df.columns:
        df["Cycle"] = 1

    df["Week"] = pd.to_numeric(df["Week"], errors="coerce").fillna(1).astype(int)
    df["Cycle"] = pd.to_numeric(df["Cycle"], errors="coerce").fillna(1).astype(int)
    df["Programme"] = df.get("Programme", "Unknown").astype(str).str.strip().replace({"": "Unknown"})
    df["Programme"] = df["Programme"].map(_programme_from_value)
    df["Exercise"] = df.get("Exercise", "Unknown").fillna("Unknown").astype(str)
    df["Month_Year"] = df["Date"].dt.to_period("M").astype(str) if "Date" in df.columns else "Unknown"
    return df


def _build_weekly_pivot(df, programme=None, cycle="All Cycles"):
    filtered = df.copy()
    if programme:
        filtered = filtered[filtered["Programme"] == programme]
    if cycle != "All Cycles":
        filtered = filtered[filtered["Cycle"] == int(cycle)]

    if filtered.empty:
        return pd.DataFrame(columns=["Exercise"] + [f"Week {week}" for week in range(1, 11)])

    weekly = filtered.groupby(["Exercise", "Week"], as_index=False)["Volume"].sum()

    if cycle == "All Cycles":
        weekly = weekly.groupby(["Exercise", "Week"], as_index=False)["Volume"].mean()

    pivot = weekly.pivot(index="Exercise", columns="Week", values="Volume").reindex(range(1, 11), axis=1)
    pivot.columns = [f"Week {week}" for week in pivot.columns]
    pivot = pivot.reset_index().rename(columns={"Exercise": "Exercise"})
    for week_label in [f"Week {week}" for week in range(1, 11)]:
        if week_label not in pivot.columns:
            pivot[week_label] = 0
    return pivot[["Exercise"] + [f"Week {week}" for week in range(1, 11)]]


def get_lift_metrics(lift_df):
    if lift_df.empty:
        return {}

    df = lift_df.copy()
    metrics = {}

    monthly_total = (
        df.groupby(["Programme", "Month_Name"], as_index=False)["Volume"].sum().rename(columns={"Volume": "Total_Volume"}))
    monthly_avg = (
        df.groupby(["Programme", "Month_Name"], as_index=False)
        .agg(Avg_Volume_Per_Set=("Volume", lambda x: x.mean()), Total_Volume=("Volume", "sum"))
    )
    monthly_avg["Avg_Volume_Per_Set"] = monthly_avg["Avg_Volume_Per_Set"].fillna(0)

    metrics["programme_overview_total_volume"] = monthly_total
    metrics["programme_overview_avg_volume_per_set"] = monthly_avg
    metrics["exercise_monthly_volume"] = (
        df.groupby(["Programme", "Exercise", "Month_Name"], as_index=False)["Volume"].sum()
    )
    metrics["exercise_weekly_volume"] = (
        df.groupby(["Programme", "Exercise", "Week"], as_index=False)["Volume"].sum()
    )
    metrics["weekly_volume_stats"] = _build_weekly_pivot(df)
    return metrics


def build_weekly_volume_stats(lift_df, programme=None, cycle="All Cycles"):
    if lift_df.empty:
        return pd.DataFrame(columns=["Exercise"] + [f"Week {week}" for week in range(1, 11)])
    return _build_weekly_pivot(lift_df, programme=programme, cycle=cycle)


def get_garmin_metrics(garmin_df):
    if garmin_df.empty:
        return {}
    metrics = {}
    workouts_per_month = garmin_df.groupby("Month_Name")["Date"].count().reset_index()
    workouts_per_month.columns = ["Month_Name", "Total_Workouts"]
    metrics["total_workouts_month"] = workouts_per_month
    metrics["avg_workouts_per_month"] = workouts_per_month["Total_Workouts"].mean()

    type_week_counts = garmin_df.groupby(["Activity Type", "Week"])["Date"].count().reset_index()
    type_week_counts.columns = ["Activity Type", "Week", "Workout_Count"]
    metrics["avg_workouts_type_week"] = (
        type_week_counts.groupby("Activity Type")["Workout_Count"].mean().reset_index()
    )
    metrics["avg_workouts_type_week"].columns = ["Activity Type", "Avg_Workouts_Per_Week"]

    metrics["avg_hr_per_type"] = garmin_df.groupby("Activity Type")["Avg HR"].mean().reset_index()
    metrics["avg_hr_per_type"].columns = ["Activity Type", "Avg_Heart_Rate"]
    return metrics