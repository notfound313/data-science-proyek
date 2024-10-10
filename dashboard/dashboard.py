import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

#function

def create_rental_season_based_df(df):
  rental_based_seasson_df = df.groupby(by="season_hour").agg({
    "cnt_hour" :"sum"
})
  rental_based_seasson_df.rename(columns={
        "cnt_hour": "rental_count"
    }, inplace=True)
  return rental_based_seasson_df


def create_workingday_based_df(df):
  categories = {0:"not work", 1: "work"}
  df["workingday"] = df["workingday_hour"].apply(lambda x : categories[x] )
  workingday_df = df.groupby(["weekday_day","workingday"]).agg({
    "cnt_hour":"sum"
  })
  workingday_df.rename(columns={
        "cnt_hour": "rental_count"
    }, inplace=True)

  return workingday_df

def create_dteday_df(df):
    dteday_df = df.groupby("dteday_hour").agg({
        "casual_hour":"sum",
        "registered_hour":"sum"
    })
    dteday_df.rename(columns={

        "casual_hour":"casual",
        "registered_hour":"registered"
    }, inplace=True)
    return dteday_df

def create_weather_df(df):
  weather_df = df.groupby("weathersit_hour").agg({
    "cnt_hour":"sum"
  })
  weather_df.rename(columns={
      "cnt_hour": "rental_count"
  },inplace=True)

  return weather_df

def create_weather_time_df(df):
  weather_time_df = df.groupby(["weathersit_hour","time_category_hour"]).agg({
    "cnt_hour":"sum"
  },inplace=True)
  weather_time_df.rename(columns={
      "cnt_hour": "rental_count"
  },inplace=True)
  return weather_time_df


def create_time_category_df(df):
  category_time_df = df.groupby("time_category_hour").agg({
    "cnt_hour" : "sum"
  })

  category_time_df.rename(columns={
      "cnt_hour": "rental_count"
  },inplace=True)

  return category_time_df

def create_cluster_df(df):
  cluster_df = df.groupby("dteday_hour").agg({
        "cnt_hour":"sum",
    })
  labels=['low','mid','high','very high']
  cluster_df["cluster_cnt"] =  pd.cut(cluster_df['cnt_hour'], bins=4, labels=labels, right=False)
  return cluster_df

# Load cleaned data

merged_df = pd.read_csv("dashboard/merged_data.csv")
column_date = ["dteday_hour", "dteday_day"]


for column in column_date:
    merged_df[column] = pd.to_datetime(merged_df[column])

# filter date

min_date = merged_df["dteday_hour"].min()
max_date = merged_df["dteday_hour"].max()

with st.sidebar:

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

#prepering data
main_df = merged_df[(merged_df["dteday_hour"] >= str(start_date)) &
                (merged_df["dteday_hour"] <= str(end_date))]

# Menyiapkan berbagai dataframe

rental_season_df = create_rental_season_based_df(main_df)
workingday_based_df = create_workingday_based_df(main_df)
dteday_df = create_dteday_df(main_df)
weathershif_df = create_weather_df(main_df)
weather_time_df = create_weather_time_df(main_df)
category_time_df = create_time_category_df(main_df)
cluster_df = create_cluster_df(main_df)


st.header('Bike Sharing Dashboard :sparkles:')
st.subheader('Daily & Monthly & yearly Rental')


#jumlah rental disetiap season

col1, col2 , col3, col4 = st.columns(4)
seasons = ["fall","summer","winter", "springer"]

emojis = {
    "fall": "🍂",
    "summer": "🌞",
    "winter": "❄️",
    "springer": "🌸"
}

for season in seasons:
   count = rental_season_df.loc[season,"rental_count"]
   with st.container():
        if season == "fall":
            with col1:
                st.markdown(f"### {emojis[season]} {season.capitalize()}")
                st.metric("Total Rental ", value=count)
        elif season == "summer":
            with col2:
                st.markdown(f"### {emojis[season]} {season.capitalize()}")
                st.metric("Total Rental ", value=count)
        elif season == "winter":
            with col3:
                st.markdown(f"### {emojis[season]} {season.capitalize()}")
                st.metric("Total Rental ", value=count)
        elif season == "springer":
            with col4:
                st.markdown(f"### {emojis[season]} {season.capitalize()}")
                st.metric("Total Rental ", value=count)


st.subheader("Musim yang Terbaik untuk Rental") 

fig , ax = plt.subplots(figsize=(10, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]


sns.barplot(x="season_hour", y="rental_count", data=rental_season_df.sort_values(by="rental_count", ascending=False), palette=colors,ax=ax)
ax.set_yticks(ax.get_yticks())
ax.set_yticklabels([f'{int(y / 1000)}k' for y in ax.get_yticks()])

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("Musim yang Terbaik untuk Rental", loc="center", fontsize=18)

ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)



st.subheader("Harian penyewa berdasarkan hari kerja ") 

fig, ax = plt.subplots(figsize=(10, 6))

barplot = sns.barplot(data=workingday_based_df, x="weekday_day", y="rental_count", hue="workingday", errorbar=None, ax=ax)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("Harian penyewa berdasarkan hari kerja ", loc="center", fontsize=18)


for p in barplot.patches:
    barplot.annotate(format(int(p.get_height()), ','),
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                     textcoords='offset points')


ax.legend(title='Working Day', bbox_to_anchor=(1, 0.5), loc='center left')
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


st.subheader("Performance tren bike-sharing")

fig, ax = plt.subplots(figsize=(12, 6))

# Plot Casual and Registered rentals
sns.lineplot(data=dteday_df, x='dteday_hour', y='casual', label='Casual', color='blue', ax=ax)
sns.lineplot(data=dteday_df, x='dteday_hour', y='registered', label='Registered', color='orange', ax=ax)


ax.set_title("Jumlah Penyewa Casual dan Registered per Tanggal", fontsize=18)
ax.set_xlabel("Tanggal", fontsize=14)
ax.set_ylabel("Jumlah", fontsize=14)


ax.tick_params(axis='x', rotation=45)


ax.grid(True)
ax.legend()

plt.tight_layout()
st.pyplot(fig)


#performace berdasrkan cuaca
st.subheader("Total Rental Berdasarkan Kondisi Cuaca")
col1, col2, col3, col4 = st.columns(4)


weather_conditions = {
    1: ('Cerah', '☀️'),
    2: ('kabut dan Berawan', '🌫️'),
    3: ('Salju/Hujan Tipis', '🌧️'),
    4: ('Hujan Lebat+Petir', '⛈️')
}

weather_items = []


for key in weather_conditions:
    weather, emoji = weather_conditions[key]
    count = weathershif_df.loc[key, 'rental_count']
    weather_items.append((emoji, weather, count))

for index, (emoji, weather, count) in enumerate(weather_items):
    with st.container():
        if index % 4 == 0:
            with col1:
                st.markdown(f"### {emoji} ")
                st.markdown(f"### {weather}")
                st.metric("Total Rental", value=count)
        elif index % 4 == 1:
            with col2:
                st.markdown(f"### {emoji}")
                st.markdown(f"### {weather}")
                st.metric("Total Rental", value=count)
        elif index % 4 == 2:
            with col3:
                st.markdown(f"### {emoji} ")
                st.markdown(f"### {weather}")
                st.metric("Total Rental", value=count)
        elif index % 4 == 3:
            with col4:
                st.markdown(f"### {emoji} ")
                st.markdown(f"### {weather}")
                st.metric("Total Rental", value=count)


fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(data=weathershif_df, x="weathersit_hour", y="rental_count", palette=colors, ax=ax)

ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['Cerah', 'kabut dan Berawan', 'Salju Tipis/Hujan Tipis', 'Hujan Lebat, Salju Lebat + Petir'], rotation=45)

ax.set_yticks(ax.get_yticks())
ax.set_yticklabels([f'{int(y)}' for y in ax.get_yticks()])

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("Jumlah Penyewa Berdasarkan Cuaca", fontsize=16)

plt.tight_layout()

st.pyplot(fig)


st.subheader("Performance Berdasarkan Kategori Waktu dan Cuaca")

fig, ax = plt.subplots(figsize=(10, 6))
barplot = sns.barplot(data=weather_time_df, x="weathersit_hour", y="rental_count", hue="time_category_hour", errorbar=None, ax=ax)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("Jumlah penyewa berdasarkan Cuaca dan Kategori Waktu", loc="center", fontsize=18)

for p in barplot.patches:
    barplot.annotate(format(int(p.get_height()), ','),
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                     textcoords='offset points')

ax.legend(title='Time Categories', bbox_to_anchor=(1, 0.5), loc='center left')
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['Cerah', 'kabut dan Berawan', 'Salju Tipis/Hujan Tipis', 'Hujan Lebat, Salju Lebat + Petir'], rotation=45)

plt.tight_layout()
st.pyplot(fig)


st.subheader("Performace Berdasarkan Kategori Waktu")

col1, col2, col3, col4 = st.columns(4)
times_of_day = ["afternoon", "evening", "morning", "night"]

emojis = {
    "afternoon": "☀️",
    "evening": "🌆",
    "morning": "🌅",
    "night": "🌙"
}

for time in times_of_day:
    count = category_time_df.loc[time, "rental_count"]
    with st.container():
        if time == "afternoon":
            with col1:
                st.markdown(f"### {emojis[time]} {time.capitalize()}")
                st.metric("Total Rental", value=count)
        elif time == "evening":
            with col2:
                st.markdown(f"### {emojis[time]} {time.capitalize()}")
                st.metric("Total Rental", value=count)
        elif time == "morning":
            with col3:
                st.markdown(f"### {emojis[time]} {time.capitalize()}")
                st.metric("Total Rental", value=count)
        elif time == "night":
            with col4:
                st.markdown(f"### {emojis[time]} {time.capitalize()}")
                st.metric("Total Rental", value=count)


fig, ax = plt.subplots(figsize=(10, 6))
barplot = sns.barplot(data=category_time_df, x="time_category_hour", y="rental_count", palette=colors, ax=ax)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_yticks(ax.get_yticks())
ax.set_yticklabels([f'{int(y)}' for y in ax.get_yticks()])
ax.set_title("Jumlah penyewa berdasarkan Kategori Waktu", loc="center", fontsize=12)
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)


st.subheader("Clustering Jumlah Penyewa Dalam Harian")

fig, ax = plt.subplots(figsize=(10, 6))
barplot = sns.barplot(data=cluster_df, x="cluster_cnt", y="cnt_hour", palette=colors, ax=ax)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("Clustering jumlah penyewa dalam satu bulan", loc="center", fontsize=12)
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)
