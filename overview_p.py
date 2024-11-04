
import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain

# Centered and styled main title using inline styles
st.markdown('''
    <style>
        .main-title {
            color: #e66c37; /* Title color */
            text-align: center; /* Center align the title */
            font-size: 3rem; /* Title font size */
            font-weight: bold; /* Title font weight */
            margin-bottom: .5rem; /* Space below the title */
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1); /* Subtle text shadow */
        }
        div.block-container {
            padding-top: 2rem; /* Padding for main content */
        }
    </style>
''', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">KPI METRICS VIEW DASHBOARD</h1>', unsafe_allow_html=True)

data = pd.read_excel('sales Data.xlsx')
# Ensure 'created_time' is a datetime object
data['created_time'] = pd.to_datetime(data['created_time'])
# Drop all rows that have a duplicated value in the 'Employer group' column
df = data.drop_duplicates(subset='Employer group', keep="first")
# Sidebar styling and logo
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content h2 {
        color: #007BFF; /* Change this color to your preferred title color */
        font-size: 1.5em;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-title {
        color: #e66c37;
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-header {
        color: #e66c37; /* Change this color to your preferred header color */
        font-size: 2.5em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-multiselect {
        margin-bottom: 15px;
    }
    .sidebar .sidebar-content .logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content .logo img {
        max-width: 80%;
        height: auto;
        border-radius: 50%;
    }
            
    </style>
    """, unsafe_allow_html=True)

# Extract additional columns for filtering
df['year'] = df['created_time'].dt.year
df['MonthName'] = df['created_time'].dt.strftime('%B')
df['Client Segment'] = df['Client Segment'].astype(str)
df['Engagement'] = df['Engagement'].astype(str)
df['Employer group'] = df['Employer group'].astype(str)



# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['year'].unique()))
month = st.sidebar.multiselect("Select Month", options=sorted(df['MonthName'].unique()))
client_type = st.sidebar.multiselect("Select Client Type", options=sorted(df['Client Segment'].unique()))
eng_type = st.sidebar.multiselect("Select Engagement Type", options=sorted(df['Engagement'].unique()))
em_group = st.sidebar.multiselect("Select Employer group", options=sorted(df['Employer group'].unique()))

## Filter by year
if year:
    df = df[df['year'].isin(year)]

# Filter by client type
if client_type:
    df = df[df['Client Segment'].isin(client_type)]

# Filter by month
if month:
    df = df[df['MonthName'].isin(month)]

# Filter by engagement type
if eng_type:
    df = df[df['Engagement'].isin(eng_type)]
if em_group:
    df = df[df['Employer group'].isin(em_group)]

filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if client_type:
    filter_description += f"{', '.join(map(str, client_type))} "
if month:
    filter_description += f"{', '.join(month)} "
if eng_type:
    filter_description += f"{', '.join(eng_type)} "
if not filter_description:
    filter_description = "All Data"


if not df.empty:
     # Calculate metrics
    scaling_factor = 1_000_000  # For millions
    scaled = 1_000_000_000  # for billions


    total_clients = df["Employer group"].nunique()
    total_lives = df["Employee Size"].sum()
    total_in_val = df["RWF Value"].sum()
    average_pre_per_life = df["RWF Value"].mean()
    gwp_average = total_clients * total_lives * average_pre_per_life
    total_items = len(df)

    partners = len(df[df['Engagement'] == 'Partnership'])
    contract = len(df[df['Engagement'] == 'Contract'])
    priority = len(df[df['Priority'] == 'High'])
    total_items = len(df)
    closed_items = len(df[df['Status'] == 'Closed 💪'])
    percentage_closed = (closed_items / total_items) * 100
    total_val_scaled = total_in_val / scaling_factor
    average_pre_scaled = average_pre_per_life/scaling_factor
    gwp_average_scaled = gwp_average/scaled

    # Create 4-column layout for metric cards# Define CSS for the styled boxes and tooltips
    st.markdown("""
        <style>
        .custom-subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .metric-box {
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin: 10px;
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
            position: relative;
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 1em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1.5em;
        }
        .tooltip {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position the tooltip above the text */
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip::after {
            content: "";
            position: absolute;
            top: 100%; /* Arrow at the bottom */
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #555 transparent transparent transparent;
        }
        .metric-box:hover .tooltip {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """, unsafe_allow_html=True)

    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value, tooltip_text):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                <div class="tooltip">{tooltip_text}</div>
            </div>
            """, unsafe_allow_html=True)



    st.markdown('<h2 class="custom-subheader">For Prospective Sales</h2>', unsafe_allow_html=True)    




    # Display metrics
    cols1, cols2, cols3 = st.columns(3)
    display_metric(cols1, "Total Clients", total_clients, "The total number of potential clients.")
    display_metric(cols2, "Total Premium", f"RWF {total_val_scaled:.0f} M", "The total expected premium in millions of RWF.")
    display_metric(cols3, "Estimated Lives Covered", total_lives, "The total number of lives covered depending on the employee size.")
    display_metric(cols1, "Average Estimated Premium", f"RWF {average_pre_scaled:.0f}M", "The average estimated premium per life in millions of RWF.")
    display_metric(cols2, "Average GWP", f"RWF {gwp_average_scaled:.0f} B", "The average Gross Written Premium in billions of RWF (total number of clients x total lives covered x average Premium per life")
    display_metric(cols3, "Percentage Closed", f"{percentage_closed:.1f} %", "The percentage of propective sales that have been closed.")
    display_metric(cols1, "Estimated Partners", partners, "Clients with Potential Partnership deals")
    display_metric(cols2, "Estimated Contracts", contract, "Clients with Potential contract deals")
    display_metric(cols3, "Highest Priority Clients", priority, "Clients with  High Priority ")



