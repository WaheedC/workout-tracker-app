import pandas as pd

path = r'.\data\workout_data.xlsx'
xl = pd.ExcelFile(path)
print('SHEETS:', xl.sheet_names)
for s in xl.sheet_names:
    df = xl.parse(s)
    print(f'\n--- SHEET: {s} ---')
    print('COLUMNS:', list(df.columns))
    print('SHAPE:', df.shape)
    print(df.head(3).to_string(index=False))
