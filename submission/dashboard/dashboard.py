# Import Library 
import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Config Wide Layout
st.set_page_config(
    layout="wide",
)


# Config background color
bg_css = """
<style>
[data-testid="stAppViewContainer"] {background: linear-gradient(45deg, #12063b, #09555c)}
[data-testid="stHeader"] {background: linear-gradient(45deg, #12063b, #09555c)}
[data-testid="stSidebar"] {
background-color: #09555c;
opacity: 0.8;
background-image:  radial-gradient(#12063b 1.7000000000000002px, transparent 1.7000000000000002px), radial-gradient(#12063b 1.7000000000000002px, #09555c 1.7000000000000002px);
background-size: 68px 68px;
background-position: 0 0,34px 34px;
}
</style>
"""
st.markdown(bg_css, unsafe_allow_html=True)


# Load Image
main_df = pd.read_csv("./dashboard/main_data.csv")

#opening the image
image = Image.open('./dashboard/bikesharing_img.jpg')


# Konversi kolom 'date' menjadi tipe data datetime
main_df['date'] = pd.to_datetime(main_df['date'])
main_df.sort_values(by="date", inplace=True)
main_df.reset_index(inplace=True)

 # Kelompokkan data berdasarkan tanggal dan hitung jumlah count_user
daily_count = main_df.groupby('date')['count_user'].sum().reset_index()
min_date = daily_count["date"].min()
max_date = daily_count["date"].max()


with st.sidebar:
    # Adding Image
    st.image(image)

    # Input Date Filter
    start_date, end_date = st.date_input(
        label = 'Rentang Waktu', 
        min_value = min_date,
        max_value = max_date,
        value = [min_date, max_date]
    )

    # Filter
    filter_df = main_df[(main_df["date"] >= str(start_date)) & 
                (main_df["date"] <= str(end_date))]

# Function for count Total User
def create_total_user_df(df):
    total_user_df = df.resample(rule='D', on='date').agg({"count_user": "sum"})
    total_user_df = total_user_df.reset_index()   
    return total_user_df

def create_registered_user_df(df):
    total_registered_df = df.resample(rule='D', on='date').agg({"registered_user": "sum"})
    total_registered_df = total_registered_df.reset_index()   
    return total_registered_df

def create_casual_user_df(df):
    total_casual_df = df.resample(rule='D', on='date').agg({"casual_user": "sum"})
    total_casual_df = total_casual_df.reset_index()   
    return total_casual_df

def create_daily_user_df(df):
    daily_user_df = df.resample(rule='D', on='date').agg({
        "count_user": "sum",
    })
    daily_user_df = daily_user_df.reset_index()   
    return daily_user_df

# Function for comparing user by workingday (pertanyaan 1)
def create_user_workingday_df(df):
    sum_user_workingday_df = df.groupby(['year', 'month', 'workingday'])[['casual_user', 'registered_user', 'count_user']].sum()
    months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    sum_user_workingday_df.reset_index(inplace=True)
    sum_user_workingday_df['month'] = pd.Categorical(sum_user_workingday_df['month'], categories=months_order, ordered=True)
    return sum_user_workingday_df

# Function for comparing user by hour (pertanyaan 2)
def create_user_hour_df(df):
    hour_casual_registered_df = df.groupby(by=["hour"]).agg({
    "casual_user": "sum",
    "registered_user": "sum"
    }).reset_index()
    return hour_casual_registered_df

# inisiasi
sum_total_user_df = create_total_user_df(filter_df)
sum_registered_df = create_registered_user_df(filter_df)
sum_casual_df = create_casual_user_df(filter_df)
sum_daily_user_df = create_daily_user_df(filter_df)
sum_user_workingday_df = create_user_workingday_df(filter_df)
sum_user_hour_df = create_user_hour_df(filter_df)


# Dashboard
st.title(':bicyclist: Bike Sharing Dashboard  :bar_chart:')
st.text("")

st.subheader('Users Bike Share')

col1, col2, col3 = st.columns(3)

with col1:
    sum_total_user_df = sum_total_user_df.count_user.sum()
    st.metric("Total User", value=sum_total_user_df)

with col2:
    sum_registered_df = sum_registered_df.registered_user.sum()
    st.metric("Total Registered User", value=sum_registered_df)

with col3:
    sum_casual_df = sum_casual_df.casual_user.sum()
    st.metric("Total Casual User", value=sum_casual_df)
    
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    sum_daily_user_df["date"],
    sum_daily_user_df["count_user"],
    linewidth=2,  # Keep the line width for better visibility
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.text("")
st.text("")
st.text("")

# Visualisasi 1 (Pertanyaan 1)
st.subheader('Casual User Vs Registered User in Working Day')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 15))

sns.barplot(x='month', y='casual_user', data=sum_user_workingday_df.reset_index(), hue='workingday', ax=ax[0])
ax[0].set_ylabel(None)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
ax[0].legend(fontsize=20, loc='upper left', title="Working Day", title_fontsize='20')
ax[0].set_title("Casual User by Workingday", loc="center", fontsize=50)

sns.barplot(x='month', y='registered_user', data=sum_user_workingday_df, hue='workingday', ax=ax[1])
ax[1].tick_params(axis='y', labelsize=35)
ax[1].set_ylabel(None)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].legend(fontsize=20, loc='upper left', title="Working Day", title_fontsize='20') 
ax[1].set_title("Registered User  by Workingday", loc="center", fontsize=50)

st.pyplot(fig)

st.text("")
st.text("")
st.text("")

# Visualisasi 2 (Pertanyaan 2)
st.subheader('Casual User vs Registered User by Hour')

# Menggunakan bar chart yang distack
fig = plt.figure(figsize=(10, 6))
sns.barplot(x='hour', y='casual_user', data=sum_user_hour_df, color='orange', label='Casual User')
sns.barplot(x='hour', y='registered_user', data=sum_user_hour_df, color='green', label='Registered User', bottom=sum_user_hour_df['casual_user'])

plt.xlabel('Hour')
plt.ylabel('Number of Bike Rentals')
plt.title('Total Bike Share by Hour')
plt.legend()
plt.tight_layout()
st.pyplot(fig)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

sns.barplot(x='hour', y='casual_user', data=sum_user_hour_df, color='orange', ax=ax[0])
ax[0].set_ylabel("Casual User")
ax[0].set_xlabel("Hour")
ax[0].set_title("Total Casual User of Bike Share per Hour", loc="center", fontsize=8)

sns.barplot(x='hour', y='registered_user', data=sum_user_hour_df, color='green', ax=ax[1])
ax[1].set_ylabel("Registered User")
ax[1].set_xlabel("Hour")
ax[1].set_title("Total Registered User of Bike Share per Hour", loc="center", fontsize=8)

st.pyplot(fig)

st.text("")
st.text("")
st.text("")

##### Visualisasi 3 (Pertanyaan 3)
st.subheader('Proportion Users by Season')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

season_counts = main_df['season'].value_counts()
ax[0].pie(season_counts, labels=season_counts.index, autopct='%1.1f%%', colors=['skyblue', 'lightgreen', 'lightcoral', 'orange'], textprops={'fontsize': 14})
ax[0].set_title('Proportion of Bike Rentals by Season', fontsize=20)
ax[0].axis('equal')
ax[0].legend(season_counts.index, loc="center left", fontsize=10)

# Proporsi peminjaman sepeda berdasarkan cuaca (weather)
weather_counts = main_df['weather'].value_counts()
ax[1].pie(weather_counts, labels=weather_counts.index, autopct='%1.2f%%', colors=['lightblue', 'lightgreen', 'lightcoral', 'lightgrey'], textprops={'fontsize': 14})
ax[1].set_title('Proportion of Bike Rentals by Weather', fontsize=20)
ax[1].axis('equal')
ax[1].legend(weather_counts.index, loc="center left", fontsize=10)


st.pyplot(fig)

st.caption('Copyright (c) Regi Muhammar')