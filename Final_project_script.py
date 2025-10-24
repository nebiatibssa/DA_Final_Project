
import pandas as pd
import streamlit as st
import datetime as dt
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(
    page_title="Electric Consumption Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

[data-testid="stMetric"] {
    background-color: #fFAE42;
    text-align: center;
    padding: 5px 0;
}

[data-testid="stMetricLabel"] {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 14px !important;
 
}

[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: bold;
    color: #000000;
}
            
.date-range {
        font-size: 25px !important;
        color: #1E90FF; 
        text-align: center;
        font-weight: bold;
        padding: 8px;
}
</style>
""", unsafe_allow_html=True)

# Read csv files
df_electricity = pd.read_csv('https://raw.githubusercontent.com/nebiatibssa/DA_Final_Project/refs/heads/main/Electricity_consumption_price.csv')

st.title(':bulb: :orange[Electricity Consumption Dashboard] :bulb:')

min_date = df_electricity['datetime'].min()
max_date = df_electricity['datetime'].max()

with st.sidebar:
    st.markdown(f"<p style='font-size: 55px !important; color: #1E90FF;' > Select date range : </p>",unsafe_allow_html=True)

    start_date = st.date_input(label='Start time: ', value=(min_date),min_value=min_date)
    end_date = st.date_input(label='End time: ', value=(max_date),max_value=max_date)

df_electricity['datetime'] = pd.to_datetime(df_electricity['datetime'])
df_sub_electricity = df_electricity[(df_electricity['datetime'] >= pd.to_datetime(start_date)) & (df_electricity['datetime'] <= pd.to_datetime(end_date))]
df_sub2 = df_electricity[(df_electricity['datetime'] >= pd.to_datetime(start_date)) & (df_electricity['datetime'] <= pd.to_datetime(end_date))]
st.subheader(f"From : {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
       
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label='Total Consumption (kWh)', value=df_sub_electricity['kWh'].sum().round(1))
kpi2.metric(label='Total bill (€)', value=(df_sub_electricity['Bill'].sum()/100).round(1))
kpi3.metric(label='Average hourly price (cents)',value= round(df_sub_electricity['Price'].mean(), 2))#, "cents")
kpi4.metric(label='Average paid price (cents)',value= ((df_sub_electricity['Bill'].sum())/(df_sub_electricity['kWh'].sum())).round(2))#, "cents")

if start_date < end_date:
    grouping_interval = st.multiselect(label= 'Averaging Period:', options=['Daily', 'Weekly', 'Monthly'], default='Weekly', max_selections=1)
    df_visu = None
    if grouping_interval and grouping_interval[0] == 'Daily':
        df_visu = df_sub_electricity.groupby(pd.Grouper(key='datetime', freq='d')).agg(
            total_consumption = ('kWh', 'sum'),
            avg_price = ('Price', 'mean'),
            total_bill = ('Bill', 'sum'),
            avg_temperature = ('Temperature', 'mean')
        ).reset_index()
        df_visu2 = df_sub2.groupby(pd.Grouper(key='datetime', freq='d')).agg(
            total_consumption = ('kWh', 'sum'),
            avg_price = ('Price', 'mean'),
            avg_bill = ('Bill', 'mean'),
            avg_temperature = ('Temperature', 'mean')
        ).reset_index()
    elif grouping_interval and grouping_interval[0] == 'Weekly':
        df_visu = df_sub_electricity.groupby(pd.Grouper(key='datetime', freq='W')).agg(
            total_consumption = ('kWh', 'sum'),
            avg_price = ('Price', 'mean'),
            total_bill = ('Bill', 'sum'),
            avg_temperature = ('Temperature', 'mean')
        ).reset_index()
        df_visu2 = df_sub2.groupby(pd.Grouper(key='datetime', freq='W')).agg(
            total_consumption = ('kWh', 'sum'),
            avg_price = ('Price', 'mean'),
            avg_bill = ('Bill', 'mean'),
            avg_temperature = ('Temperature', 'mean')
        ).reset_index()
    elif grouping_interval and grouping_interval[0] == 'Monthly':
        df_visu = df_sub_electricity.groupby(pd.Grouper(key='datetime', freq='M')).agg(
            total_consumption = ('kWh', 'sum'),
            avg_price = ('Price', 'mean'),
            total_bill = ('Bill', 'sum'),
            avg_temperature = ('Temperature', 'mean')
        ).reset_index()
        df_visu2 = df_sub2.groupby(pd.Grouper(key='datetime', freq='M')).agg(
            total_consumption = ('kWh', 'sum'),
            avg_price = ('Price', 'mean'),
            avg_bill = ('Bill', 'mean'),
            avg_temperature = ('Temperature', 'mean')
        ).reset_index()
    else:
        st.warning("Please select the grouping interval for the visualization")
       
    if df_visu is not None:
        # Total bill in euros
        df_visu['total_bill'] = df_visu['total_bill']/100

        # Round all numeric columns to 2 decimal places
        df_visu = df_visu.round(2)

        st.subheader("📈 Electricity Consumption Over Time")
        area_chart = (
            alt.Chart(df_visu)
            .mark_area(color='steelblue', opacity=0.4)
            .encode(
                x=alt.X('datetime:T', title='Time'),
                y=alt.Y('total_consumption:Q', title='Electricity Consumption (kWh)'),
                tooltip=['datetime:T', 'total_consumption:Q']
            )
            .properties(height=300)
        )
        st.altair_chart(area_chart, use_container_width=True)

        st.subheader("💰 Electricity Price Over Time")
        st.line_chart(df_visu, x= 'datetime', y='avg_price', y_label= 'Electricity Price [cents]',x_label='Time')
        
        st.subheader("💰 Electricity Bill Over Time")
        st.line_chart(df_visu, x= 'datetime', y=['total_bill'], y_label= 'Electricity bill [€]',x_label='Time')
        
        st.subheader("🌡️ Temperature Over Time")
        st.line_chart(df_visu, x= 'datetime', y='avg_temperature', y_label= 'Temperature',x_label='Time')
        
        st.divider()
        col= st.columns(2)

        with col[0]:

            # Scatter plot: Temperature vs Consumption
            st.subheader("🌡️ Impact of Temperature on Consumption")
            scatter_chart1 = (
                alt.Chart(df_visu)
                .mark_circle(size=60, color='teal')
                .encode(
                    x=alt.X('avg_temperature:Q', title='Temperature (°C)'),
                    y=alt.Y('total_consumption:Q', title='Total Consumption (Kwh)'),
                    tooltip=['datetime:T', 'avg_temperature:Q', 'total_consumption:Q']
                )
            )
            st.altair_chart(scatter_chart1, use_container_width=True)

            # Scatter plot: Temperature vs Bill
            st.subheader("💰 Electricity Bill vs Temperature")
            scatter_chart2 = (
                alt.Chart(df_visu)
                .mark_circle(size=60, opacity=0.6, color='steelblue')
                .encode(
                    x=alt.X('avg_temperature:Q', title='Temperature (°C)'),
                    y=alt.Y('total_bill:Q', title='Total Bill (€)'),
                    tooltip=['datetime:T', 'avg_temperature:Q', 'total_bill:Q', 'total_consumption:Q']
                )
            )

            # Regression line
            trend = scatter_chart2.transform_regression('avg_temperature', 'total_bill').mark_line(color='orange', strokeWidth=2)
            st.altair_chart(scatter_chart2 + trend, use_container_width=True)

        with col[1]:
            # Extract Month and Assign Season
            df_visu['month'] = df_visu['datetime'].dt.month

            def get_season(month):
                if month in [12, 1, 2]:
                    return 'Winter'
                elif month in [3, 4, 5]:
                    return 'Spring'
                elif month in [6, 7, 8]:
                    return 'Summer'
                else:
                    return 'Autumn'
            df_visu['season'] = df_visu['month'].apply(get_season)

            st.subheader("🧭  Electricity Consumption by Season")

            # Aggregate by Season
            season_summary = df_visu.groupby('season', as_index=False)['total_consumption'].sum()
            
            # Order the seasons
            season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
            season_summary['season'] = pd.Categorical(season_summary['season'], categories=season_order, ordered=True)
            season_summary = season_summary.sort_values('season')

            # Bar Chart
            bar_chart = (
                alt.Chart(season_summary)
                .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                .encode(
                    x=alt.X('season:N', sort=season_order, title='Season'),
                    y=alt.Y('total_consumption:Q', title='Total Consumption (kWh)'),
                    color=alt.Color('season:N', legend=None, sort=season_order),
                    tooltip=['season:N', alt.Tooltip('total_consumption:Q', title='Total Consumption')]
                )
            )
            st.altair_chart(bar_chart, use_container_width=True)
            
            # Price vs Bill
         
            st.subheader("💰 Electricity Price vs Cost")
            scatter_chart2 = (
                alt.Chart(df_visu)
                .mark_circle(size=60, opacity=0.6, color='steelblue')
                .encode(
                    x=alt.X('avg_price:Q', title='Electricity Price (€)'),
                    y=alt.Y('total_bill:Q', title='Total Bill (€)'),
                    tooltip=['datetime:T', 'avg_price:Q', 'total_bill:Q', 'total_consumption:Q']
                )  
            )

            # Regression line
            trend = scatter_chart2.transform_regression('avg_price', 'total_bill').mark_line(color='orange', strokeWidth=2)
            st.altair_chart(scatter_chart2 + trend, use_container_width=True)
else:
    st.warning("Start time cannot be bigger than end time. Please select again")
