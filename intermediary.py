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

st.markdown('<h1 class="main-title">CHANNEL VIEW</h1>', unsafe_allow_html=True)

filepath="prospect_sales_data.xlsx"
sheet_name = "Eden - Team 1 LeadSheet (Master"
sheet_name1="Target"
# Read all sheets into a dictionary of DataFrames
df0 = pd.read_excel(filepath, sheet_name=sheet_name)
df1=pd.read_excel(filepath, sheet_name=sheet_name1)



# Filter rows where the Expected Close Date is in 2024

# Calculate metrics
scaling_factor = 1_000_000

target_2024 = (df1["Target"].sum())/scaling_factor
df_proactiv_target_2024 = df1[df1['Product'] == 'ProActiv']
df_health_target_2024 = df1[df1['Product'] == 'Health']
df_renewals_2024 = df1[df1['Product'] == 'Renewals']

    # Calculate Basic Premium RWFs for specific combinations
total_renewals_ytd = (df_renewals_2024['Target'].sum())/scaling_factor
total_pro_target_ytd = (df_proactiv_target_2024['Target'].sum())/scaling_factor
total_health_target_ytd = (df_health_target_2024['Target'].sum())/scaling_factor


df1['Target'] = df1['Target'] * (9 / 12)

df1['Target'] = df1['Target'] / 9

# Add a 'Month' column for filtering
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']

# Create a DataFrame for each month from January to September
expanded_rows = []
for _, row in df1.iterrows():
    for month in months:
        expanded_rows.append([row['Product'], row['Owner'], month, row['Target']])

# Create the expanded DataFrame
df_expanded = pd.DataFrame(expanded_rows, columns=['Product', 'Owner', 'Start Month', 'Target'])



df1 = pd.concat([df1]*9, ignore_index=True)
df1['Start Month'] = months * (len(df1) // len(months))
df1['Start Year'] = 2024



df = pd.concat([df0, df1])




# Ensure the 'Expected Close Date' column is in datetime format
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
status = st.sidebar.multiselect("Select Status", options=df['Status'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
channel = st.sidebar.multiselect("Select Channel", options=df['Channel'].unique())

engage = st.sidebar.multiselect("Select Engagement", options=df['Engagement'].unique())
owner = st.sidebar.multiselect("Select Sales Person", options=df['Sales person'].unique())
broker = st.sidebar.multiselect("Select Broker/Intermediary", options=df['Broker'].unique())
client_name = st.sidebar.multiselect("Select Property", options=df['Property'].unique())






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
    total_agent = (df_agent['Basic Premium RWF'].sum())/scale
    total_broker = (df_broker['Basic Premium RWF'].sum())/scale
    total_direct = (df_direct['Basic Premium RWF'].sum())/scale

    total_agent_pro = (df_agent_pro['Basic Premium RWF'].sum())/scaling_factor
    total_broker_pro= (df_broker_pro['Basic Premium RWF'].sum())/scaling_factor
    total_direct_pro = (df_direct_pro['Basic Premium RWF'].sum())/scaling_factor

    total_agent_health = (df_agent_health['Basic Premium RWF'].sum())/scaling_factor
    total_broker_health= (df_broker_health['Basic Premium RWF'].sum())/scaling_factor
    total_direct_health = (df_direct_health['Basic Premium RWF'].sum())/scaling_factor

    # Calculate Basic Premium RWFs for specific combinations
    total_closed = (df_closed['Basic Premium RWF'].sum())/scale
    total_lost = (df_lost['Basic Premium RWF'].sum())/scale

    
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



    tot_lost =  total_lost/total_pre
    tot_closed = total_closed/total_pre
    percent_closed_health = (total_closed_health/total_health)*100
    percent_closed_pro = (total_closed_pro/total_proactiv)*100
    percent_lost_health = (total_lost_health/total_health)*100
    percent_lost_pro = (total_lost_pro/total_proactiv)*100
    percent_closed = (total_closed/total_pre_scaled)*100
    percent_lost = (total_lost/total_pre_scaled)*100


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

    # Function to display metrics in styled boxes
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<h3 class="custom-subheader">For All Sales</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Display metrics
    display_metric(col1, f"Total Expected Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, f"Total Expected Sales ({filter_description.strip()})", f"RWF {total_pre_scaled:.0f} M")
    display_metric(col3, "Total Expected Principal Members", total_mem)

    # display_metric(col1, "Average Expected Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    # display_metric(col2, "Average Expected Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")

    display_metric(col1, "Total Closed Sales", f"RWF {total_closed:.0f} M")
    display_metric(col2, "Total Lost Sales", f"RWF {total_lost:.0f} M",)
    display_metric(col3, "Percentage Closed Sales", value=f"{percent_closed:.1f} %")
    display_metric(col1, "Percentage Lost Sales", value=f"{percent_lost:.1f} %")

    st.markdown('<h3 class="custom-subheader">For Expected Health Insurance Sales by Channel</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    display_metric(col1, "Expected Agent Sales", value=f"RWF {total_agent_health:.0f} M")
    display_metric(col2, "Expected Direct Sales", value=f"RWF {total_direct_health:.0f} M")
    display_metric(col3, "Expected Broker Sales", value=f"RWF {total_broker_health:.0f} M")

    st.markdown('<h3 class="custom-subheader">For Expected ProActiv Sales by Channel</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    display_metric(col1, "Expected Agent Sales", value=f"RWF {total_agent_pro:.0f} M")
    display_metric(col2, "Expected Direct Sales", value=f"RWF {total_direct_pro:.0f} M")
    display_metric(col3, "Expected Broker Sales", value=f"RWF {total_broker_pro:.0f} M")




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

    custom_colors = ["#006E7F", "#e66c37", "#461b09","#009DAE", "#f8a785", "#CC3636","#C6E7FF","#FFB38E" , "#E4E0E1"]

    # Group by day and intermediary, then sum the Basic Premium RWF
    area_chart_total_insured = df.groupby([df["Expected Close Date"].dt.strftime("%Y-%m-%d"), 'Channel'])['Basic Premium RWF'].sum().reset_index(name='Basic Premium RWF')

    # Sort by the Expected Close Date
    area_chart_total_insured = area_chart_total_insured.sort_values("Expected Close Date")

    custom_colors_insured = ["brown", "#e66c37", "#009DAE"]

    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)

    with cols1:
        # Create the area chart for Basic Premium RWF
        fig1, ax1 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='Expected Close Date', columns='Channel', values='Basic Premium RWF').fillna(0)
        
        # Plot the stacked area chart
        pivot_df_insured.plot(kind='area', stacked=True, ax=ax1, color=custom_colors_insured[:len(pivot_df_insured.columns)])

        # Remove the border around the chart
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        # Set x-axis title
        ax1.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax1.set_ylabel("Basic Premium RWF", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Expected Sales by Channel over Time</h3>', unsafe_allow_html=True)

        # Format the y-axis
        formatter = FuncFormatter(millions)
        ax1.yaxis.set_major_formatter(formatter)

        # Display the chart in Streamlit
        st.pyplot(fig1)



    # Group by day and intermediary, then sum the Total Lives
    area_chart_total_lives = df.groupby([df["Expected Close Date"].dt.strftime("%Y-%m-%d"), 'Channel'])['Total lives'].sum().reset_index(name='Total lives')

    # Sort by the Expected Close Date
    area_chart_total_lives = area_chart_total_lives.sort_values("Expected Close Date")


    with cols2:
        # Create the area chart for Total Lives
        fig2, ax2 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_lives = area_chart_total_lives.pivot(index='Expected Close Date', columns='Channel', values='Total lives').fillna(0)
        
        # Plot the stacked area chart
        pivot_df_lives.plot(kind='area', stacked=True, ax=ax2, color=custom_colors_insured[:len(pivot_df_lives.columns)])


        # Remove the border around the chart
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        
        # Set x-axis title
        ax2.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax2.set_ylabel("Total Lives Covered", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")


        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Expected Lives Covered by Channel over Time</h3>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig2)

    cols1,cols2 = st.columns(2)

    # Group data by "Expected Close Date Year" and "Intermediary" and calculate the average Basic Premium RWF
    yearly_avg_premium = df.groupby(['Start Year', 'Channel'])['Basic Premium RWF'].sum().unstack().fillna(0)

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

    with cols1:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, intermediary in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[intermediary],
                name=intermediary,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Expected Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Expected Yearly Sales per Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)

 # Calculate the Basic Premium RWF by intermediary
    int_premiums = df.groupby("Channel")["Basic Premium RWF"].sum().reset_index()
    int_premiums.columns = ["Channel", "Basic Premium RWF"]    

    with cols2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Expected Sales per Channel</h3>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Channel", values="Basic Premium RWF", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
   
    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Yearly Average Premium by Channel"):
            st.dataframe(yearly_avg_premium.style.format(precision=2))
    
    # Function to find the closest client to a given value
    with ccl2:
        with st.expander("Average Premium by Channel"):
            st.dataframe(int_premiums.style.format(precision=2))

    cul1, cul2 = st.columns(2)



    # Group data by "Broker" and "Status" and sum the Basic Premium RWF
    premium_by_broker_and_status_health = df_health.groupby(['Broker', 'Status'])['Basic Premium RWF'].sum().reset_index()

    # Calculate the number of sales by "Broker"
    sales_by_broker = df_health.groupby('Broker').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_df = premium_by_broker_and_status_health.merge(sales_by_broker, on='Broker')

    # Sort the merged data by Basic Premium RWF in descending order and select the top 10 brokers
    top_10_brokers = merged_df.groupby('Broker')['Basic Premium RWF'].sum().reset_index().sort_values(by='Basic Premium RWF', ascending=False).head(10)

    # Filter the original premium_by_broker_and_status_health to include only the top 10 brokers
    top_10_broker_data = premium_by_broker_and_status_health[premium_by_broker_and_status_health['Broker'].isin(top_10_brokers['Broker'])]

    # Create the layout columns

    with cul2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar traces for each status with custom colors
        for i, status in enumerate(top_10_broker_data['Status'].unique()):
            filtered_data = top_10_broker_data[top_10_broker_data['Status'] == status]
            fig_premium_by_intermediary.add_trace(go.Bar(
                x=filtered_data['Broker'],
                y=filtered_data['Basic Premium RWF'],
                text=filtered_data['Basic Premium RWF'],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y',
                name=status,
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Broker",
            yaxis=dict(
                title="Basic Premium RWF",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),
            barmode='group',
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Expected Sales by Brokers and Status</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)




    # Group by Property and Intermediary, then sum the Basic Premium RWF
    df_grouped = df.groupby(['Broker', 'Channel'])['Basic Premium RWF'].sum().reset_index()

    # Get the top 10 clients by Basic Premium RWF
    top_10_clients = df_grouped.groupby('Broker')['Basic Premium RWF'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Broker'].isin(top_10_clients['Broker'])]
    # Sort the client_df by Basic Premium RWF in descending order
    client_df = client_df.sort_values(by='Basic Premium RWF', ascending=False)
   
    with cul1:
            # Create the bar chart
        fig = go.Figure()

            # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

            # Add bars for each intermediary
        for idx, intermediary in enumerate(client_df['Channel'].unique()):
                intermediary_data = client_df[client_df['Channel'] == intermediary]
                fig.add_trace(go.Bar(
                    x=intermediary_data['Broker'],
                    y=intermediary_data['Basic Premium RWF'],
                    name=intermediary,
                    text=[f'{value/1e6:.0f}M' for value in intermediary_data['Basic Premium RWF']],
                    textposition='auto',
                    marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                ))

        fig.update_layout(
                barmode='stack',
                yaxis_title="Basic Premium RWF",
                xaxis_title="Intermediaries",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )

            # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Expected Sales by Intermediaries and Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


    cul1, cul2 = st.columns(2)


    with cul1:
        with st.expander("Intermedirary premium by Channel"):
            st.dataframe(client_df.style.format(precision=2))
    # Display the grouped dataframes in expanders

    with cul2:
        with st.expander("Total Health sales by broker and status"):
            st.dataframe(premium_by_broker_and_status_health.style.format(precision=2))


    # Group by Property and Intermediary, then sum the Basic Premium RWF
    df_grouped = df.groupby(['Property', 'Channel'])['Basic Premium RWF'].sum().reset_index()

    # Get the top 10 clients by Basic Premium RWF
    top_10_clients = df_grouped.groupby('Property')['Basic Premium RWF'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    int = df_grouped[df_grouped['Property'].isin(top_10_clients['Property'])]
    # Sort the client_df by Basic Premium RWF in descending order
    int_df = int.sort_values(by='Basic Premium RWF', ascending=False)
   

            # Create the bar chart
    fig = go.Figure()

            # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

            # Add bars for each intermediary
    for idx, intermediary in enumerate(int_df['Channel'].unique()):
                intermediary_data = int_df[int_df['Channel'] == intermediary]
                fig.add_trace(go.Bar(
                    x=intermediary_data['Property'],
                    y=intermediary_data['Basic Premium RWF'],
                    name=intermediary,
                    text=[f'{value/1e6:.0f}M' for value in intermediary_data['Basic Premium RWF']],
                    textposition='auto',
                    marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                ))

    fig.update_layout(
                barmode='stack',
                yaxis_title="Basic Premium RWF",
                xaxis_title="Property",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )

            # Display the chart in Streamlit
    st.markdown('<h3 class="custom-subheader">Top 15 Expected Client Sales by Channel</h3>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Client Premium by Channel"):
            st.dataframe(int_df.style.format(precision=2))




    cls1, cls2 = st.columns(2)

    # Group data by "Start Month" and "Channel" and sum the Basic Premium RWF
    monthly_premium = df.groupby(['Start Month', 'Channel'])['Basic Premium RWF'].sum().unstack().fillna(0)

    # Group data by "Start Month" to count the number of sales
    monthly_sales_count = df.groupby(['Start Month']).size()

    with cls1:
        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

        fig_monthly_premium = go.Figure()

        for idx, intermediary in enumerate(monthly_premium.columns):
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[intermediary],
                name=intermediary,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))


        # Add a secondary y-axis for the count of sales
        fig_monthly_premium.add_trace(go.Scatter(
            x=monthly_sales_count.index,
            y=monthly_sales_count,
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            line=dict(width=2, color='red'),
            marker=dict(size=6, symbol='circle', color='red')
        ))

        # Set layout for the Basic Premium RWF chart
        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Month",
            yaxis_title="Basic Premium RWF",
            yaxis2=dict(
                title="Number of Sales",
                overlaying='y',
                side='right'
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Basic Premium RWF chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Expected Sales by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    # Group by Expected Close Date Month and Intermediary and sum the Total lives
    monthly_lives = df.groupby(['Start Month', 'Channel'])['Total lives'].sum().unstack().fillna(0)

    with cls2:
        fig_monthly_lives = go.Figure()

        for idx, intermediary in enumerate(monthly_lives.columns):
            fig_monthly_lives.add_trace(go.Bar(
                x=monthly_lives.index,
                y=monthly_lives[intermediary],
                name=intermediary,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))



        # Add a secondary y-axis for the count of sales
        fig_monthly_lives.add_trace(go.Scatter(
            x=monthly_sales_count.index,
            y=monthly_sales_count,
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            line=dict(width=2, color='red'),
            marker=dict(size=6, symbol='circle', color='red')
        ))

        # Set layout for the Total Lives chart
        fig_monthly_lives.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Month",
            yaxis_title="Total Lives Covered",
            yaxis2=dict(
                title="Number of Sales",
                overlaying='y',
                side='right'
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Lives chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Expected Lives Covered by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives, use_container_width=True)

    clm1, clm2 = st.columns(2)

    with clm1:
        # Create an expandable section for the table
        with st.expander("View Monthly Basic Premium RWF by Channel"):
            st.dataframe(monthly_premium.style.format(precision=2))

    with clm2:
        with st.expander("View Monthly Total Live covered by Channel"):
            st.dataframe(monthly_lives.style.format(precision=2))



    # summary table
    st.markdown('<h3 class="custom-subheader">Month-Wise Expected Sales By Channel Table</h3>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=df,
            values="Basic Premium RWF",
            index=["Channel"],
            columns="Start Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
    

        
else:
    st.error("No data available for this selection")