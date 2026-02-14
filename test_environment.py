import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. LOAD DATA ---
FILE_PATH = 'C:\\Users\\Kelvin\\Documents\\Python Scripts\\ChatLogs\\dm.json'
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Convert the "messages" list into a DataFrame
df = pd.DataFrame(raw_data['messages'])

# Now apply the timestamp conversion we discussed
df['timestamp'] = pd.to_datetime(df['timestamp'],format='ISO8601', utc=True)
df['timestamp'] = df['timestamp'].dt.tz_convert('US/Pacific')
df['Date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
df['Time'] = df['timestamp'].dt.strftime('%H:%M')
df['author'] = df['author'].str.get('name')
df['attachments'] = df['attachments'].apply(lambda x: 1 if isinstance(x, list) and len(x) > 0 else 0)
df['attachments1'] = df['attachments'].apply(lambda x: 1 if isinstance(x, list) and len(x) > 0 else 0)

df['reaction_author'] = df['reactions'].str[0].str.get('users').str[0].str.get('name')
df['reactions'] = df['reactions'].str[0].str.get('emoji').str.get('name')

df['inlineEmojis'] = df['inlineEmojis'].str[0].str.get('name')

col_name = ['type','Date','Time','content','author','attachments','reactions','reaction_author','inlineEmojis']
df = df[col_name]

df.to_csv('cleaned_discord_data.csv', index=False, encoding='utf-8-sig')