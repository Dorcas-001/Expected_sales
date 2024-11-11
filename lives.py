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

st.markdown('<h1 class="main-title">LIVES COVERED VIEW</h1>', unsafe_allow_html=True)

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

    total_clients = df["Property"].nunique()
    total_mem = df["Employee Size"].sum()
    total_dependents = df["Dependents"].sum()
    total_lives = total_mem +total_dependents
    average_dep = total_mem/total_dependents
    average_pre = df["Basic Premium RWF"].mean()
    average_premium_per_life = total_pre/total_mem
    gwp_average = total_lives * average_premium_per_life / total_clients


    total_health_pm = (df_health['Employee Size'].sum())
    total_pro_dep = (df_proactiv['Dependents'].sum())
    total_pro_pm = (df_proactiv['Employee Size'].sum())
    total_health_dep = (df_health['Dependents'].sum())
    
    average_dep_health = (total_health_pm/total_health_dep)
    average_dep_pro = total_pro_pm/total_pro_dep

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

    st.markdown('<h3 class="custom-subheader">For All Expected Sales</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Display metrics
    display_metric(col1, f"Total Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, f"Total Expected Lives Covered ({filter_description.strip()})", f"{total_lives:.0f} ")
    display_metric(col3, "Total Expected Principal Members", total_mem)
    display_metric(col1, "Total Expected Dependents", f" {total_dependents:.0f} ")

    # display_metric(col2, "Average Expected Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    display_metric(col2, "Average Dependents Per Principal Member", f"{average_dep:.0f}")


    st.markdown('<h3 class="custom-subheader">For Expected Health Insurance Lives Covered</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    display_metric(col1, "Total Expected Health Principal Members", total_health_pm)
    display_metric(col2, "Total Expected Health Dependents", total_health_dep)
    display_metric(col3, "Average Dependents Per Principal Member", f"{average_dep_health:.0f}")

    st.markdown('<h3 class="custom-subheader">For Expected ProActiv Lives Covered</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    display_metric(col1, "Total ExpectedProActiv Principal Members", total_pro_pm)
    display_metric(col2, "Total ExpectedProActiv Dependents", total_pro_dep)
    display_metric(col3, "Average Dependents Per Principal Member", f"{average_dep_pro:.0f}")


    

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
    
    custom_colors = ["#006E7F", "#e66c37", "#461b09","#009DAE", "#f8a785", "#CC3636","#C6E7FF","#FFB38E" , "#E4E0E1"]

    cul1, cul2 =st.columns(2)
# Group by day and intermediary, then sum the Total Premium
    area_chart_total_insured = df.groupby([df["Expected Close Date"].dt.strftime("%Y-%m-%d"), 'Product'])['Total lives'].sum().reset_index(name='Total lives')

    # Sort by the Expected Close Date
    area_chart_total_insured = area_chart_total_insured.sort_values("Expected Close Date")

    with cul1:
        # Set the figure size to a height of 450
        fig1, ax1 = plt.subplots(figsize=(10, 9))  # Adjust the width and height as needed

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='Expected Close Date', columns='Product', values='Total lives').fillna(0)
            
        # Plot the stacked area chart
        pivot_df_insured.plot(kind='area', stacked=True, ax=ax1, color=custom_colors[:len(pivot_df_insured.columns)])

        # Remove the border around the chart
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        # Set x-axis title
        ax1.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax1.set_ylabel("Total Lives Covered", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Set chart title
        st.markdown('<h2 class="custom-subheader">Total Expected Lives Covered by Product over Time</h2>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig1)

 
    # Group data by "Expected Close Date Year" and calculate the total number of Principal Members and Dependents
    yearly_totals = df.groupby(['Start Year']).agg({
        'Employee Size': 'sum',
        'Dependents': 'sum'
    }).reset_index()

    with cul2:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Principal Members
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Year'],
            y=yearly_totals['Employee Size'],
            name='Principal Member',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]  # Custom color for Principal Member
        ))

        # Add bars for Dependents
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Year'],
            y=yearly_totals['Dependents'],
            name='Dependents',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]  # Custom color for Dependents
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Expected Lives by Year and Member Type</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)

   
    colus1,colus2 = st.columns(2)

 # Group data by "Expected Close Date Month" and calculate the total number of Principal Members and Dependents
    yearly_totals = df.groupby(['Start Month']).agg({
        'Employee Size': 'sum',
        'Dependents': 'sum'
    }).reset_index()

    # Calculate total lives for sorting
    yearly_totals['Total Lives'] = yearly_totals['Employee Size'] + yearly_totals['Dependents']

    # Sort the DataFrame by total lives in descending order
    yearly_totals = yearly_totals.sort_values('Total Lives', ascending=False)

    with colus1:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Principal Members
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Month'],
            y=yearly_totals['Employee Size'],
            name='Principal Member',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]  # Custom color for Principal Member
        ))

        # Add bars for Dependents
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Month'],
            y=yearly_totals['Dependents'],
            name='Dependents',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]  # Custom color for Dependents
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=400
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Expected Lives by Month and Member Type</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)

  


    # Get the top 10 clients by Total Premium
    top_10_clients = df.groupby('Property')['Total lives'].sum().nlargest(20).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    top_employer_groups = df[df['Property'].isin(top_10_clients['Property'])]
    # Sort the client_df by Total Premium in descending order
    top_employer_groups = top_employer_groups.sort_values(by='Total lives', ascending=False)

    with colus2:
        fig_employer_groups = go.Figure()

        fig_employer_groups.add_trace(go.Bar(
            x=top_employer_groups['Property'],
            y=top_employer_groups['Total lives'],
            marker=dict(color='#009DAE'),
            text=top_employer_groups["Total lives"],
            textposition='outside', 
            textfont=dict(color='black'),  
            hoverinfo='y+text'
        ))

        fig_employer_groups.update_layout(
            xaxis_title="Employer Group",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Top 20 Expected Clients By Total Lives </h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_employer_groups, use_container_width=True)

    
    cls1, cls2 = st.columns(2)
    
    # Group data by "Expected Close Date Month" and "Client Segment" and sum the Total Lives
    monthly_lives_by_segment = df.groupby(['Start Month', 'Client Segment'])['Total lives'].sum().unstack().fillna(0)


    with cls2:
        # Create the stacked bar chart
        fig_monthly_lives_by_segment = go.Figure()

        for i, segment in enumerate(monthly_lives_by_segment.columns):
            fig_monthly_lives_by_segment.add_trace(go.Bar(
                x=monthly_lives_by_segment.index,
                y=monthly_lives_by_segment[segment],
                name=segment,
                text=monthly_lives_by_segment[segment],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        fig_monthly_lives_by_segment.update_layout(
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Monthly Expected Total Lives by Client Segment</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives_by_segment, use_container_width=True)

 # Group data by "Expected Close Date Month" and "Intermediary" and sum the Total Lives
    monthly_lives_by_intermediary = df.groupby(['Start Month', 'Channel'])['Total lives'].sum().unstack().fillna(0)

    with cls1:

        # Create the stacked bar chart
        fig_monthly_lives_by_intermediary = go.Figure()

        for i, intermediary in enumerate(monthly_lives_by_intermediary.columns):
            fig_monthly_lives_by_intermediary.add_trace(go.Bar(
                x=monthly_lives_by_intermediary.index,
                y=monthly_lives_by_intermediary[intermediary],
                name=intermediary,
                text=monthly_lives_by_intermediary[intermediary],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        fig_monthly_lives_by_intermediary.update_layout(
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Monthly Total Lives by Intermediary</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives_by_intermediary, use_container_width=True)


    # Calculate the total insured premium by intermediary
    int_premiums = df.groupby("Channel")["Total lives"].sum().reset_index()
    int_premiums.columns = ["Channel", "Total lives"]


    cols1, cols2 = st.columns(2)

    with cols1:
        # Display the header
        st.markdown('<h2 class="custom-subheader">Total Expected Lives by Channel</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Channel", values="Total lives", hole=0.4, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True, height=200)

        # Calculate the total insured premium by client segment
    int_premiums = df.groupby("Client Segment")["Total lives"].sum().reset_index()
    int_premiums.columns = ["Client Segment", "Total lives"]

    with cols2:    
        # Display the header
        st.markdown('<h2 class="custom-subheader">Total Expected Lives by Client Segment</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Client Segment", values="Total lives",  template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

          




    st.markdown('<h3 class="custom-subheader">Month-Wise Lives Distribution By Client Segment Table</h3>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=df,
            values="Total lives",
            index=["Client Segment"],
            columns="Start Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
        
else:
    st.error("No data available for this selection")