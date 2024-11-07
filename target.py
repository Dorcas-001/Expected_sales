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

st.markdown('<h1 class="main-title">SALES vs TARGET VIEW</h1>', unsafe_allow_html=True)

filepath="prospect_sales_data.xlsx"
sheet_name = "Eden - Team 1 LeadSheet (Master"
sheet_name1="Target"
# Read all sheets into a dictionary of DataFrames
df0 = pd.read_excel(filepath, sheet_name=sheet_name)
df1=pd.read_excel(filepath, sheet_name=sheet_name1)

df0  = df0[(df0['Status'] == 'Closed 💪')]
df0 = df0[df0["Start Year"]==2024]


# Filter rows where the Start Date is in 2024





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
engage = st.sidebar.multiselect("Select Engagement", options=df['Engagement'].unique())
owner = st.sidebar.multiselect("Select Sales Team", options=df['Owner'].unique())






# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Product' in df.columns and product:
    df = df[df['Product'].isin(product)]
if 'Owner' in df.columns and owner:
    df = df[df['Owner'].isin(owner)]


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
target_2024
df_proactiv_target_2024 = df[df['Product'] == 'ProActiv']
df_health_target_2024 = df[df['Product'] == 'Health']
df_renewals_2024 = df[df['Product'] == 'Renewals']

# Calculate Basic Premium RWFs for specific combinations
total_renewals_ytd = df_renewals_2024['Target'].sum() / scaling_factor
total_pro_target_ytd = df_proactiv_target_2024['Target'].sum() / scaling_factor
total_health_target_ytd = df_health_target_2024['Target'].sum() / scaling_factor

# Adjust the 'Target' column
df['Target'] = df['Target'] * (10 / 12) / 10

# Add a 'Month' column for filtering
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
num_months = len(months)

# Calculate the monthly target for each row
df['Target'] = df['Target'] / num_months


df = pd.concat([df]*10, ignore_index=True)
df['Start Month'] = months * (len(df) // len(months))
df['Start Year'] = 2024



# Handle non-finite values in 'Start Year' column
df['Start Year'] = df['Start Year'].fillna(0).astype(int)  # Replace NaN with 0 or any specific value

# Handle non-finite values in 'Start Month' column
df['Start Month'] = df['Start Month'].fillna('Unknown')

# Create a 'Month-Year' column
df['Month-Year'] = df['Start Month'] + ' ' + df['Start Year'].astype(str)

# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order.get(month, 0))  # Use .get() to handle 'Unknown' month

# Extract unique month-year combinations and sort them
month_years = sorted(df['Month-Year'].unique(), key=sort_key)

# Select slider for month-year range
selected_month_year_range = st.select_slider(
    "Select Month-Year Range",
    options=month_years,
    value=(month_years[0], month_years[-1])
)

# Filter DataFrame based on selected month-year range
start_month_year, end_month_year = selected_month_year_range
start_month, start_year = start_month_year.split()
end_month, end_year = end_month_year.split()

start_index = (int(start_year), month_order.get(start_month, 0))
end_index = (int(end_year), month_order.get(end_month, 0))

# Filter DataFrame based on month-year order indices
df = df[
    df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order.get(x.split()[0], 0))).between(start_index, end_index)
]

    # Filter the concatenated DataFrame to include only endorsements

df["Employee Size"] = pd.to_numeric(df["Employee Size"], errors='coerce').fillna(0).astype(int)
df["Dependents"] = pd.to_numeric(df["Targeted Lives (depentands) "], errors='coerce').fillna(0).astype(int)



df_proactiv = df[df['Product'] == 'ProActiv']
df_health = df[df['Product'] == 'Health']


df_closed = df[(df['Status'] == 'Closed 💪')]
df_lost = df[df['Status'] == 'Lost 😢']

df_agent = df[df['Channel'] == 'Agent']
df_direct = df[df['Channel'] == 'Direct']
df_broker = df[df['Channel'] == 'Broker']

df_proactiv_target = df[df['Product'] == 'ProActiv']
df_health_target = df[df['Product'] == 'Health']
df_renewals = df[df['Product'] == 'Renewals']

df_closed_health = df_closed[df_closed['Product'] == 'Health']
df_lost_pro = df_lost[df_lost['Product'] == 'ProActiv']
df_closed_pro = df_closed[df_closed['Product'] == 'ProActiv']
df_lost_health = df_lost[df_lost['Product'] == 'Health']

df_proactiv_target = df[df['Product'] == 'ProActiv']
df_health_target = df[df['Product'] == 'Health']
df_renewals = df[df['Product'] == 'Renewals']

df_agent_pro = df_agent[df_agent['Product'] == 'ProActiv']
df_broker_pro = df_broker[df_broker['Product'] == 'ProActiv']
df_direct_pro = df_direct[df_direct['Product'] == 'ProActiv']

df_agent_health = df_agent[df_agent['Product'] == 'Health']
df_broker_health = df_broker[df_broker['Product'] == 'Health']
df_direct_health = df_direct[df_direct['Product'] == 'Health']

df["Basic Premium RWF"] = pd.to_numeric(df["Basic Premium RWF"], errors="coerce")



if not df.empty:

# Calculate the Basic Premium RWF for endorsements only


    scale=1_000_000  # For millions

    total_pre = (df["Basic Premium RWF"].sum())

    # Scale the sums
    total_pre_scaled = total_pre /scale 



    # Calculate Basic Premium RWFs for specific combinations
    total_proactiv= (df_proactiv['Basic Premium RWF'].sum()) / scale
    total_health = (df_health['Basic Premium RWF'].sum()) / scale

    # Calculate Basic Premium RWFs for specific combinations
    total_closed = (df_closed['Basic Premium RWF'].sum())/scale
    total_lost = (df_lost['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_closed_health = (df_closed_health['Basic Premium RWF'].sum())/scale
    total_closed_pro = (df_closed_pro['Basic Premium RWF'].sum())/scale


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

    percent_closed = (total_closed/total_pre_scaled)*100


    # Scale the sums
    average_pre_scaled = average_pre/scale
    gwp_average_scaled = gwp_average/scale

    scaled = 1_000

    # Calculate key metrics
    lowest_premium = df['Basic Premium RWF'].min() /scaled
    highest_premium = df['Basic Premium RWF'].max() / scaling_factor

  

    # Create 4-column layout for metric cards
    col1, col2, col3 = st.columns(3)

    # Define CSS for the styled boxes
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
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 1em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1.2em;
        }
        </style>
        """, unsafe_allow_html=True)

    # Function to display metrics in styled boxes
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)
        

    st.markdown('<h3 class="custom-subheader">For Expected Health Insurance or ProActiv Sales</h3>', unsafe_allow_html=True)  
    # Display metrics
    col1, col2, col3= st.columns(3)
    display_metric(col1, f"Total Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, "Total Closed Sales", f"RWF {total_closed:.0f} M")
    display_metric(col3, "Total Target 2024", f"RWF {target_2024:.0f} M")

    display_metric(col1, "Total Principal Members", total_mem)

    display_metric(col2, "Average Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    display_metric(col3, "Average Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")



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

   
    # Sidebar styling and logo
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content h3 {
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

    cols1, cols2 = st.columns(2)

    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]


    # Group data by "Owner" and calculate the total Target and Basic Premium RWF
    yearly_totals = df.groupby('Owner')[['Target', 'Basic Premium RWF']].sum().fillna(0)

    with cols1:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Target
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals.index,
            y=yearly_totals['Target'],
            name='Target',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0],  # Use the first custom color for Target
            offsetgroup=0
        ))

        # Add bars for Basic Premium RWF
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals.index,
            y=yearly_totals['Basic Premium RWF'],
            name='Basic Premium RWF',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1],  # Use the second custom color for Basic Premium RWF
            offsetgroup=1
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Owner",
            yaxis_title="Total Values",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Target Sales vs Actual Sales by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)


    # Group data by "Owner" and calculate the total Target and Basic Premium RWF
    product_totals = df.groupby('Product')[['Target', 'Basic Premium RWF']].sum().fillna(0)

    with cols2:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Target
        fig_yearly_totals.add_trace(go.Bar(
            x=product_totals.index,
            y=product_totals['Target'],
            name='Target',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0],  # Use the first custom color for Target
            offsetgroup=0
        ))

        # Add bars for Basic Premium RWF
        fig_yearly_totals.add_trace(go.Bar(
            x=product_totals.index,
            y=product_totals['Basic Premium RWF'],
            name='Basic Premium RWF',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1],  # Use the second custom color for Basic Premium RWF
            offsetgroup=1
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Product",
            yaxis_title="Total Values",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Target Sales vs Actual Sales  by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)

 

    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Target and premuim by Owner"):
            st.dataframe(yearly_totals.style.format(precision=2))
        
    with ccl2:
        # Expander for IQR table
        with st.expander("Target and premuim by Product"):
            st.dataframe(product_totals.style.format(precision=2))

    cls1, cls2 = st.columns(2)

 # Calculate the Basic Premium RWF by Client Segment
    int_owner = df.groupby("Sales person")["Basic Premium RWF"].sum().reset_index()
    int_owner.columns = ["Owner", "Basic Premium RWF"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Sales by Sales Team</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig_owner = px.pie(int_owner, names="Owner", values="Basic Premium RWF", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig_owner.update_traces(textposition='inside', textinfo='value+percent')
        fig_owner.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig_owner, use_container_width=True)

# Count the occurrences of each Status
    prod_counts = df["Sales person"].value_counts().reset_index()
    prod_counts.columns = ["Owner", "Count"]

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Number of Sales By Sales Team</h3>', unsafe_allow_html=True)

        # Create a donut chart
        fig = px.pie(prod_counts, names="Owner", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("TotalPremium by Sales Team"):
            st.dataframe(prod_counts.style.format(precision=2))
        
    with cl2:
        with st.expander("Number of Sales by Sales Team"):
            st.dataframe(int_owner.style.format(precision=2))

