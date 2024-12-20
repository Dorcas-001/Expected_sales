import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain
from matplotlib.ticker import FuncFormatter


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

filepath="prospect_sales_data.xlsx"
sheet_name = "Eden - Team 1 LeadSheet (Master"
sheet_name1="Target"
# Read all sheets into a dictionary of DataFrames
df0 = pd.read_excel(filepath, sheet_name=sheet_name)
df1=pd.read_excel(filepath, sheet_name=sheet_name1)

df = pd.concat([df0, df1])

# Ensure the 'Start Date' column is in datetime format
df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'])
df['Last Contact Date'] = pd.to_datetime(df['Last Contact Date'])

df['Days Difference'] = df['Expected Close Date'] - df['Last Contact Date']


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




# Get minimum and maximum dates for the date input
startDate = df["Expected Close Date"].min()
endDate = df["Expected Close Date"].max()

# Define CSS for the styled date input boxes
st.markdown("""
    <style>
    .date-input-box {
        border-radius: 10px;
        text-align: left;
        margin: 5px;
        font-size: 1.2em;
        font-weight: bold;
    }
    .date-input-title {
        font-size: 1.2em;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

  
# Create 2-column layout for date inputs
col1, col2 = st.columns(2)

# Function to display date input in styled boxes
def display_date_input(col, title, default_date, min_date, max_date):
    col.markdown(f"""
        <div class="date-input-box">
            <div class="date-input-title">{title}</div>
        </div>
        """, unsafe_allow_html=True)
    return col.date_input("", default_date, min_value=min_date, max_value=max_date)

# Display date inputs
with col1:
    date1 = pd.to_datetime(display_date_input(col1, "Expected Close Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "Expected Close Date", endDate, startDate, endDate))


# Convert dates to datetime
df['Created_date'] = pd.to_datetime(df['Created_date'])
df['Last_update'] = pd.to_datetime(df['Last_update'])

# Calculate the sales cycle length
df['sales_cycle_length'] = (df['Last_update'] - df['Created_date']).dt.days


# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

# Sort months based on their order
sorted_months = sorted(df['Start Month'].dropna().unique(), key=lambda x: month_order[x])


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())
status = st.sidebar.multiselect("Select Status", options=df['Status'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
channel = st.sidebar.multiselect("Select Channel", options=df['Channel'].unique())
team = st.sidebar.multiselect("Select Team", options=df['Owner'].unique())
owner = st.sidebar.multiselect("Select Sales Person", options=df['Sales person'].unique())
engage = st.sidebar.multiselect("Select Engagement", options=df['Engagement'].unique())
broker = st.sidebar.multiselect("Select Broker", options=df['Broker'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Property'].unique())






# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Product' in df.columns and product:
    df = df[df['Product'].isin(product)]
if 'Status' in df.columns and status:
    df = df[df['Status'].isin(status)]
if 'Client Segment' in df.columns and segment:
    df = df[df['Client Segment'].isin(segment)]
if 'Broker' in df.columns and broker:
    df = df[df['Broker'].isin(broker)]
if 'Channel' in df.columns and broker:
    df = df[df['Channel'].isin(channel)]
if 'Owner' in df.columns and team:
    df = df[df['Owner'].isin(team)]
if 'Sales person' in df.columns and owner:
    df = df[df['Sales person'].isin(owner)]
if 'Property' in df.columns and client_name:
    df = df[df['Property'].isin(client_name)]

# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if owner:
    filter_description += f"{', '.join(map(str, owner))} "
if month:
    filter_description += f"{', '.join(month)} "
if product:
    filter_description += f"{', '.join(product)} "
if not filter_description:
    filter_description = "All data"


# Calculate metrics
scaling_factor = 1_000_000

target_2024 = df["Target"].sum() / scaling_factor
df_proactiv_target_2024 = df[df['Product'] == 'ProActiv']
df_health_target_2024 = df[df['Product'] == 'Health']

# Calculate Basic Premium RWFs for specific combinations
total_pro_target_ytd = df_proactiv_target_2024['Target'].sum() / scaling_factor
total_health_target_ytd = df_health_target_2024['Target'].sum() / scaling_factor

# Adjust the 'Target' column
df['Target'] = df['Target'] * (10 / 12)

# Add a 'Month' column for filtering
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
num_months = len(months)

# Create a new DataFrame to hold the replicated data
df_replicated = pd.DataFrame()

# Replicate the dataset for each month
for month in months:
    df_month = df.copy()
    df_month['Month'] = month
    df_replicated = pd.concat([df_replicated, df_month], ignore_index=True)

# Adjust the 'Target' column by dividing by the number of months
df_replicated['Target'] = df_replicated['Target'] / num_months


    # Filter the concatenated DataFrame to include only endorsements
df_hares = df[(df['Client Segment'] == 'Hares')]
df_elephants = df[df['Client Segment'] == 'Elephant']
df_tiger = df[df['Client Segment'] == 'Tigers']
df_whale = df[df['Client Segment'] == 'Whale']


df_proactiv = df[df['Product'] == 'ProActiv']
df_health = df[df['Product'] == 'Health']


df_closed = df[(df['Status_def'] == 'Closed 💪')]
df_lost = df[df['Status_def'] == 'Lost 😢']
df_progress = df[df['Status_def'] == 'In Progress']

df_agent = df[df['Channel'] == 'Agent']
df_direct = df[df['Channel'] == 'Direct']
df_broker = df[df['Channel'] == 'Broker']

df_closed_health = df_closed[df_closed['Product'] == 'Health']
df_lost_pro = df_lost[df_lost['Product'] == 'ProActiv']
df_closed_pro = df_closed[df_closed['Product'] == 'ProActiv']
df_lost_health = df_lost[df_lost['Product'] == 'Health']

df_proactiv_target = df[df['Product'] == 'ProActiv']
df_health_target = df[df['Product'] == 'Health']
df_renewals = df[df['Product'] == 'Renewals']

df["Basic Premium RWF"] = pd.to_numeric(df["Basic Premium RWF"], errors="coerce")

if not df.empty:

    scale=1_000_000  # For millions

    # Number of Opportunities
    number_of_opportunities = len(df)

    # Average Deal Size
    average_deal_size = (df_closed['Basic Premium RWF'].mean())/scale

    won_deals = len(df_closed)
    # Win Rate Percentage
    win_rate_percentage = (won_deals / number_of_opportunities)*100
    win_rate = (won_deals / number_of_opportunities)

    # Average Sales Cycle Length
    average_sales_cycle_length = df_closed['sales_cycle_length'].mean()

    # Calculate Sales Velocity
    sales_velocity = ((won_deals * average_deal_size * win_rate) / average_sales_cycle_length)

# Calculate the Basic Premium RWF for endorsements only


    total_pre = (df["Basic Premium RWF"].sum())

    # Scale the sums
    total_pre_scaled = total_pre /scale 

    total_hares = (df_hares['Basic Premium RWF'].sum())/scale
    total_tiger = (df_tiger['Basic Premium RWF'].sum())/scale
    total_elephant = (df_elephants['Basic Premium RWF'].sum())/scale
    total_whale = (df_whale['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_proactiv= (df_proactiv['Basic Premium RWF'].sum()) / scale
    total_health = (df_health['Basic Premium RWF'].sum()) / scale
    
    # Calculate Basic Premium RWFs for specific combinations
    total_agent = (df_agent['Basic Premium RWF'].sum())/scale
    total_broker = (df_broker['Basic Premium RWF'].sum())/scale
    total_direct = (df_direct['Basic Premium RWF'].sum())/scale


    # Calculate Basic Premium RWFs for specific combinations
    total_closed = (df_closed['Basic Premium RWF'].sum())/scale
    total_lost = (df_lost['Basic Premium RWF'].sum())/scale
    total_progess = (df_progress['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_closed_health = (df_closed_health['Basic Premium RWF'].sum())/scale
    total_closed_pro = (df_closed_pro['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_lost_health = (df_lost_health['Basic Premium RWF'].sum())/scale
    total_lost_pro = (df_lost_pro['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_pro_target = (df_proactiv_target['Target'].sum())/scale
    total_health_target = (df_health_target['Target'].sum())/scale
    health_variance = (total_closed_health-total_health_target)
    health_percent_var = (health_variance/total_health_target) *100
    pro_variance = total_closed_pro-total_pro_target
    pro_percent_var = (pro_variance/total_pro_target) *100

    df["Employee Size"] = pd.to_numeric(df["Employee Size"], errors='coerce').fillna(0).astype(int)
    df["Dependents"] = pd.to_numeric(df["Targeted Lives (depentands) "], errors='coerce').fillna(0).astype(int)

    total_clients = df["Property"].nunique()
    total_mem = df["Employee Size"].sum()
    total_dependents = df["Dependents"].sum()
    total_lives = total_mem +total_dependents
    average_dep = total_mem/total_dependents
    average_pre = df["Basic Premium RWF"].mean()
    average_premium_per_life = total_pre/total_mem
    gwp_average = total_lives * average_premium_per_life / total_clients



    percent_closed_health = (total_closed_health/total_health)*100
    percent_closed_pro = (total_closed_pro/total_proactiv)*100
    percent_lost_health = (total_lost_health/total_health)*100
    percent_lost_pro = (total_lost_pro/total_proactiv)*100
    percent_closed = (total_closed/total_pre_scaled)*100
    percent_lost = (total_lost/total_pre_scaled)*100
    percent_progress = (total_progess/total_pre_scaled)*100
    # Scale the sums
    average_pre_scaled = average_pre/scale
    gwp_average_scaled = gwp_average/scale

    scaled = 1_000

    # Calculate key metrics
    lowest_premium = df['Basic Premium RWF'].min() /scaled
    highest_premium = df['Basic Premium RWF'].max() / scaling_factor

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
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1em;
        }

        </style>
        """, unsafe_allow_html=True)



    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)




    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">Sales Velocity</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Number of Opportunities", number_of_opportunities)
    display_metric(cols2, "Average Deal Size Per client", F"{average_deal_size: .0F} M")
    display_metric(cols3, "Number of Closed Deals", won_deals)
    display_metric(cols1, "Closed Rate Percentage", f"{win_rate_percentage:.1f} %")
    display_metric(cols2, "Average sales cyle length Per Deal", f"{average_sales_cycle_length:.0f} days")
    display_metric(cols3, "Sales Velocity Per Day", f"{sales_velocity:.0f} M")

    st.markdown('<h3 class="custom-subheader">For Expected Health Insurance or ProActiv Sales</h3>', unsafe_allow_html=True)    
    # Display metrics
    col1, col2, col3= st.columns(3)
    display_metric(col1, f"Total Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, f"Total Expected Sales ({filter_description.strip()})", f"RWF {total_pre_scaled:.0f} M")
    display_metric(col3, "Total Principal Members", total_mem)
    display_metric(col1, "Total Target 2024", f"{target_2024:.0f} M")

    # display_metric(col1, "Average Expected Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    # display_metric(col2, "Average Expected Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")

    display_metric(col2, "Total Closed Sales", f"RWF {total_closed:.0f} M")
    display_metric(col3, "Total Lost Sales", f"RWF {total_lost:.0f} M",)
    display_metric(col1, "Percentage Closed Sales", value=f"{percent_closed:.1f} %")
    display_metric(col2, "Percentage Lost Sales", value=f"{percent_lost:.1f} %")
    display_metric(col3, "Percentage Sales in Progress", value=f"{percent_progress:.1f} %")


    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For Expected Lives Covered</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3, cols4 = st.columns(4)

    display_metric(cols1, "Expected Lives Covered", f"{total_lives:.0f}")
    display_metric(cols2, "Total Principal Members", total_mem)
    display_metric(cols3, "Total Dependents", total_dependents)
    display_metric(cols4, "Average Dependents Per Principal Member", f"{average_dep:.0f}")


    st.markdown('<h2 class="custom-subheader">For Expected Health Insurance Sales</h2>', unsafe_allow_html=True) 
    col1, col2, col3 = st.columns(3)
    display_metric(col1, "Total Expected Health Sales", value=f"RWF {total_health:.0f} M")
    display_metric(col2, "Total Closed Health Sales", value=f"RWF {total_closed_health:.0f} M")
    display_metric(col3, "Total Lost Health Sales", value=f"RWF {total_lost_health:.0f} M")

    display_metric(col1, "Percentage Closed Health Sales", value=f" {percent_closed_health:.1f} %")
    display_metric(col2, "Percentage Lost Health Sales", value=f" {percent_lost_health:.1f} %")

    st.markdown('<h2 class="custom-subheader">For Expected ProActiv Sales</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "Total Expected ProActiv Sales", value=f"RWF {total_proactiv:.0f} M")
    display_metric(col2, "Total Closed ProActiv Sales", value=f"RWF {total_closed_pro:.0f} M")
    display_metric(col3, "Total Lost ProActiv Sales", value=f"RWF {total_lost_health:.0f} M")

    display_metric(col1, "Percentage Closed ProActiv Sales", value=f" {percent_closed_pro:.1f} %")
    display_metric(col2, "Percentage Lost ProActiv Sales", value=f" {percent_lost_pro:.1f} %")

    st.markdown('<h2 class="custom-subheader">For Health Insurance Target</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "2024 Target Health Sales", f"RWF {total_health_target_ytd:.0f} M")
    display_metric(col2, "YTD Health Target Sales", f"RWF {total_health_target:.0f} M")
    display_metric(col3, "YTD Closed Health Sales", f"RWF {total_closed_health:.0f} M")
    display_metric(col1, "Variance", f"RWF {health_variance:.1f} M")
    display_metric(col2, "Percentage Variance", value=f"{health_percent_var:.2f} %")

    st.markdown('<h2 class="custom-subheader">For ProActiv Target</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "2024 Target ProActiv Sales", f"RWF {total_pro_target_ytd:.0f} M")
    display_metric(col2, "YTD ProActiv Target Sales", f"RWF {total_pro_target:.0f} M")
    display_metric(col3, "YTD Closed ProActiv Sales", f"RWF {total_closed_pro:.0f} M")
    display_metric(col1, "Variance", f"RWF {pro_variance:.0f} M")
    display_metric(col2, "Percentage Variance", value=f"{pro_percent_var:.0f} %")



