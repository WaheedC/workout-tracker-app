import pandas as pd
from pathlib import Path

path = Path(r'c:\Users\Waheed\Projects\workout-tracker-app\data\workout_data.xlsx')
print('PATH EXISTS:', path.exists())
xl = pd.ExcelFile(path)
print('SHEETS:', xl.sheet_names)
for sheet_name in xl.sheet_names:
    df = xl.parse(sheet_name)
    print(f'\n--- SHEET: {sheet_name} ---')
    print('COLUMNS:', list(df.columns))
    print('DTYPES:', df.dtypes.astype(str).to_dict())
    print('SHAPE:', df.shape)
    print(df.head(3).to_string(index=False))
