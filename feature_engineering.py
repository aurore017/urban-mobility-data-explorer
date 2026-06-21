import pandas as pd

df = pd.read_csv("data/processed/<aurore's_filename>.csv")  # adjust path/name

print(df.shape)
print(df.columns.tolist())
print(df.head())
