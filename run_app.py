import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime as dt
import plotly.express as px
import pytz
import re
from collections import Counter
from pathlib import Path


st.set_page_config(page_title= "Kelvin and JingJing's love story",
                   page_icon= ":heart:",
                   layout="wide")

curr_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
data_file = curr_dir / "C:\\Users\\Kelvin\\Documents\\Python Scripts\\ChatLogs\\cleaned_discord_data.csv"

# Load the data
df = pd.read_csv(data_file)

st.title("Happy Valentine Bunny! :heart:")

total_message = df['type'].count()


with st.container():
    st.header("Our Journey", divider="rainbow")
    
    col1, col2, col3 = st.columns([1, 1, 1]) 
    with col1:
        st.metric("Days since our first hello", (dt.datetime.now() - dt.datetime(2023, 11, 9)).days, "❤️")
    with col2:
        st.metric("Total Messages", total_message)
    with col3:
        st.metric("Days we are together", (dt.datetime.now() - dt.datetime(2023, 12, 4)).days, "❤️")
        
    screen1, screen2 = st.columns(2)
    with screen1:
        st.image("ChatLogs\\img\\first_message.png")
        st.caption("Me attempting to talk to the pretty girl more")
    with screen2:
        st.image("ChatLogs\\img\\important_question.png")
        st.caption("Walking down cringey memory lane")



with st.container():
    st.header("Our chats", divider="rainbow")
    df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    st.subheader("🕐 Our active times")
    use_nz_time = st.toggle('Switch to New Zealand Time (NZDT)', value=False)

    df['Timestamp_PST'] = df['Timestamp'].dt.tz_localize('America/Los_Angeles', ambiguous='infer')
    
    if use_nz_time:
        # Convert to NZ time
        df['Display_Time'] = df['Timestamp_PST'].dt.tz_convert('Pacific/Auckland')
        st.info("Showing in **New Zealand Time**")
    else:
        df['Display_Time'] = df['Timestamp_PST']
        st.info("Showing data in **PST**")
    
    df['Hour'] = df['Display_Time'].dt.hour
    hourly_df = df.groupby(['Hour', 'author']).size().reset_index(name='Message Count')
    
    fig = px.bar(
        hourly_df, 
        x='Hour', 
        y='Message Count',
        barmode='group',
        labels={'Hour': 'Hour of Day (24h)', 'Message Count': 'Messages Sent'},
        color_discrete_sequence=px.colors.qualitative.Pastel
        )

    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig, use_container_width=True)
    
    freq_options = {
    "Day": "D",
    "Week": "W",
    "Month": "ME"
    }
    
    st.subheader("💌 Message Volume Over Time")
    
    selected_label = st.selectbox("", options=list(freq_options.keys()))
    freq_code = freq_options[selected_label]

    timeline_df = (
        df.set_index('Display_Time')
        .resample(freq_code)
        .size()
        .reset_index(name='Message Count')
    )
    

    fig = px.bar(
        timeline_df,
        x='Display_Time',
        y='Message Count',
        color='Message Count',
        color_continuous_scale='Sunset' if selected_label == "Daily" else 'Viridis',
        template='plotly_white'
    )
    fig.update_layout(
        showlegend=False, 
        coloraxis_showscale=False 
    )
    fig.update_xaxes(
        title="Date")
    st.plotly_chart(fig, use_container_width=True)
    
    def get_emoji_data(series, top_n=10):
        all_emojis = []
        for entry in series.dropna():
            # 1. If it's already a list (like ['❤️', 'ChopperHappy']), just extend
            if isinstance(entry, list):
                all_emojis.extend([str(e) for e in entry])
            # 2. If it's a string, we need to check if it's a list-like string 
            # (Discord exports often look like "❤️, ChopperHappy")
            elif isinstance(entry, str):
                if ',' in entry:
                    # Split by comma and strip whitespace
                    items = [item.strip() for item in entry.split(',')]
                    all_emojis.extend(items)
                else:
                    # If it's just one item, add it as a single token
                    all_emojis.append(entry.strip())
        
        counts = Counter(all_emojis).most_common(top_n)
        df_ems = pd.DataFrame(counts, columns=['Emoji', 'Count'])
        # Plotly's 'total ascending' ensures the biggest bar is at the top for horizontal charts
        return df_ems

    st.subheader("✨ Emoji")
    

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Our fav emojis")
        source_choice = st.selectbox("", ["Text", "Reactions"], key="col1_source")
        
        global_df = get_emoji_data(df["inlineEmojis" if source_choice== "Text" else "reactions"])
        fig1 = px.bar(
        global_df, x='Count', y='Emoji',
        orientation='h',
        color='Count', color_continuous_scale='Viridis',
        template='plotly_white'
        )
        fig1.update_layout(showlegend=False, coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
    
    # --- COLUMN 2: Personal Favorites (By Author) ---
    with col2:
        st.subheader("Individual Favorites")
        selected_author = st.selectbox("", ["zensius", "skhuidn0"], key="col2_author")
        
        # Filter by author then count
        author_series = df[df['author'] == selected_author]['inlineEmojis']
        author_emoji_df = get_emoji_data(author_series)
        
        fig2 = px.bar(
            author_emoji_df, x='Emoji', y='Count',
            color='Count', color_continuous_scale='Magma',
            template='plotly_white'
        )
        fig2.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    # --- COLUMN 3: The "Emoji Diversity" (Idea for the 3rd Column) ---
    with col3:
        st.subheader("Emoji Vocabulary")
        # Calculating unique emojis used by each person
        # This shows who is more 'creative' with their emoji usage
        diversity_data = []
        for author in ["zensius", "skhuidn0"]:
            all_ems = []
            for entry in df[df['author'] == author]['inlineEmojis'].dropna():
                all_ems.extend(list(entry))
            diversity_data.append({'Author': author, 'Unique Emojis': len(set(all_ems))})
        
        diversity_df = pd.DataFrame(diversity_data)
        
        fig3 = px.bar(
            diversity_df, x='Author', y='Unique Emojis',
            color='Author',
            title="Total Unique Emojis Used",
            template='plotly_white'
        )
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Which partner uses a wider variety of emojis?")
        



    
with st.container():
    st.header("Call time!", divider="rainbow")
    def extract_mins(text):
        # Regex to find the number before "minutes"
        match = re.search(r'lasted (\d+) minutes', str(text))
        return int(match.group(1)) if match else 0

    # Filter for calls and extract duration
    # (We use the 'Display_Time' column from your previous timezone logic)
    calls_df = df[df['type'].str.contains('call', case=False, na=False)].copy()
    calls_df['duration_mins'] = calls_df['content'].apply(extract_mins)
    
    # --- 2. Stats Calculation ---
    total_calls = len(calls_df)
    total_mins = calls_df['duration_mins'].sum()
    avg_duration = calls_df['duration_mins'].mean() if total_calls > 0 else 0
    longest_call = calls_df['duration_mins'].max() if total_calls > 0 else 0
    
    # Convert total minutes to Days and Hours
    days = total_mins // 1440
    hours = (total_mins % 1440) // 60
    mins_rem = total_mins % 60
    
    # --- 3. Display Metrics (The Stats Table) ---
    st.header("📞 ring ring ring")
    
    # Using columns for a clean "dashboard" look
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Calls", f"{total_calls}")
    m2.metric("Longest Call", f"{longest_call} min")
    m3.metric("Avg Duration", f"{avg_duration:.1f} min")
    m4.metric("Total Time", f"{days}d {hours}h")
    
    # --- 4. Call Duration Chart ---
    st.subheader("Time Spent on Calls")
    call_freq = st.selectbox("Aggregate By", ["Daily", "Monthly"], key="call_agg")
    freq_map = {"Daily": "D", "Monthly": "ME"}
    
    # Resample based on the selected frequency
    timeline_calls = (
        calls_df.set_index('Display_Time')
        .resample(freq_map[call_freq])['duration_mins']
        .sum()
        .reset_index()
    )
    
    fig_calls = px.bar(
        timeline_calls,
        x='Display_Time',
        y='duration_mins',
        title=f"Total Minutes on Call ({call_freq})",
        color='duration_mins',
        color_continuous_scale='Reds',
        labels={'duration_mins': 'Total Minutes', 'Display_Time': 'Date'},
        template='plotly_white'
    )
    
    fig_calls.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_calls, use_container_width=True)



with st.expander("*psst*... message to the coolest girl in the world :sunglasses:"):
    message = '''
        I know I’m not always the easy to be with. At times, I can be arrogant, unreasonable, and slow to understand your side of things.
        But seeing you in tears fills me with the fear of losing you and makes me realize how much I need to grow. We’re both figuring this out as we go, but ever since the day we met at that 711, I’ve known you were the one for me.
        When you said you weren't, it honestly broke my heart because I can't imagine a future without you. Please be patient with me as I learn. I promise to give you my absolute best and make you as happy as you deserve to be.
        **Love you always**,
        Kelvin :heart:'''
    st.markdown(message)