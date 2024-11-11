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

st.markdown('<h1 class="main-title">PRODUCT VIEW</h1>', unsafe_allow_html=True)

filepath="prospect_sales_data.xlsx"
sheet_name = "Eden - Team 1 LeadSheet (Master"
# Read all sheets into a dictionary of DataFrames
df = pd.read_excel(filepath, sheet_name=sheet_name)



# Ensure the 'Expected Close Date' column is in datetime format
df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'])
df['Last Contact Date'] = pd.to_datetime(df['Last Contact Date'])

df['Days Difference'] = (df['Expected Close Date'] - df['Last Contact Date']).dt.days

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
owner = st.sidebar.multiselect("Select Owner", options=df['Owner'].unique())
broker = st.sidebar.multiselect("Select Broker", options=df['Broker'].unique())
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
if 'Owner' in df.columns and owner:
    df = df[df['Owner'].isin(owner)]
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



    # Filter the concatenated DataFrame to include only endorsements


df_proactiv = df[df['Product'] == 'ProActiv']
df_health = df[df['Product'] == 'Health']



df_closed = df[(df['Status_def'] == 'Closed 💪')]
df_lost = df[df['Status_def'] == 'Lost 😢']
df_progress = df[df['Status_def'] == 'In Progress']


df_closed_health = df_closed[df_closed['Product'] == 'Health']
df_lost_pro = df_lost[df_lost['Product'] == 'ProActiv']
df_closed_pro = df_closed[df_closed['Product'] == 'ProActiv']
df_lost_health = df_lost[df_lost['Product'] == 'Health']



# Calculate the Basic Premium RWF for endorsements only
# Assuming the column name for the premium is 'Basic Premium RWF'
if not df.empty:
     # Calculate metrics
    scale=1_000_000  # For millions

    total_pre = (df["Basic Premium RWF"].sum())

    # Scale the sums
    total_pre_scaled = total_pre / scale
    # Calculate Basic Premium RWFs for specific combinations
    total_proactiv= (df_proactiv['Basic Premium RWF'].sum()) / scale
    total_health = (df_health['Basic Premium RWF'].sum()) / scale

    # Calculate Basic Premium RWFs for specific combinations
    total_closed = (df_closed['Basic Premium RWF'].sum())/scale
    total_lost = (df_lost['Basic Premium RWF'].sum())/scale
    total_progess = (df_progress['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_closed_health = (df_closed_health['Basic Premium RWF'].sum())/scale
    total_closed_pro = (df_closed_pro['Basic Premium RWF'].sum())/scale

    df["Employee Size"] = pd.to_numeric(df["Employee Size"], errors='coerce').fillna(0).astype(int)
    df["Dependents"] = pd.to_numeric(df["Targeted Lives (depentands) "], errors='coerce').fillna(0).astype(int)

    # Calculate Basic Premium RWFs for specific combinations
    total_lost_health = (df_lost_health['Basic Premium RWF'].sum())/scale
    total_lost_pro = (df_lost_pro['Basic Premium RWF'].sum())/scale
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
    percent_progress = (total_progess/total_pre_scaled)*100

    average_pre_scaled = average_pre/scale
    gwp_average_scaled = gwp_average/scale

    # Create 4-column layout for metric cards

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
    display_metric(col1, f"Total Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, f"Total Expected Sales ({filter_description.strip()})", f"RWF {total_pre_scaled:.0f} M")
    display_metric(col3, "Total Principal Members", total_mem)

    # display_metric(col1, "Average Expected Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    # display_metric(col2, "Average Expected Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")

    display_metric(col1, "Total Closed Sales", f"RWF {total_closed:.0f} M")
    display_metric(col2, "Total Lost Sales", f"RWF {total_lost:.0f} M",)
    display_metric(col3, "Percentage Closed Sales", value=f"{percent_closed:.1f} %")
    display_metric(col1, "Percentage Lost Sales", value=f"{percent_lost:.1f} %")
    display_metric(col2, "Percentage Sales in Progress", value=f"{percent_progress:.1f} %")


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


    df["Expected Close Date"] = pd.to_datetime(df["Expected Close Date"], errors='coerce')
    df["Start Year"] = df["Expected Close Date"].dt.year
    
    cols1, cols2 = st.columns(2)

    custom_colors = ["#006E7F", "#e66c37", "#461b09","#009DAE", "#f8a785", "#CC3636","#C6E7FF","#FFB38E" , "#E4E0E1"]

    
    # Function to format y-axis labels in millions
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)

    # Group by day and Client Segment, then sum the Basic Premium RWF
    area_chart_total_insured = df.groupby([df["Expected Close Date"].dt.strftime("%Y-%m-%d"), 'Product'])['Basic Premium RWF'].sum().reset_index(name='Basic Premium RWF')

    # Sort by the Expected Close Date
    area_chart_total_insured = area_chart_total_insured.sort_values("Expected Close Date")


    with cols1:
        # Create the area chart for Basic Premium RWF
        fig1, ax1 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='Expected Close Date', columns='Product', values='Basic Premium RWF').fillna(0)
        
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
        ax1.set_ylabel("Basic Premium RWF", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Format the y-axis
        formatter = FuncFormatter(millions)
        ax1.yaxis.set_major_formatter(formatter)

        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Sales by Product Over Time</h3>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig1)


    # Group data by "Start Month Year" and "Client Segment" and calculate the average Basic Premium RWF
    yearly_avg_premium = df.groupby(['Start Year', 'Product'])['Basic Premium RWF'].mean().unstack().fillna(0)

    # Define custom colors

    with cols2:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, Client_Segment in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Year",
            yaxis_title="Average Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Yearly Sales by Product per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Basic Premium RWF by Sales Team over Time"):
            st.dataframe(area_chart_total_insured.style.format(precision=2))
        
    with cl2:  
            with st.expander("Yearly average premium"):
                    st.dataframe(yearly_avg_premium.style.format(precision=2))




    # Create the layout columns
    cls1, cls2 = st.columns(2)

    # Group data by "Expected Close Date Month" and "Intermediary" and sum the Basic Premium RWF
    monthly_premium = df.groupby(['Start Month', 'Product'])['Basic Premium RWF'].sum().unstack().fillna(0)


    with cls2:
        # Define custom colors

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



        # Set layout for the Basic Premium RWF chart
        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Month",
            yaxis_title="Basic Premium RWF",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Basic Premium RWF chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Sales Distribution by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)



 # Calculate the Basic Premium RWF by Client Segment
    int_owner = df.groupby("Product")["Basic Premium RWF"].sum().reset_index()
    int_owner.columns = ["Product", "Basic Premium RWF"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Sales by Product</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Product", values="Basic Premium RWF", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 =st.columns(2)


    with cl1:  
            with st.expander("Total Product Premium"):
                    st.dataframe(int_owner.style.format(precision=2))

    with cl2:
        # Create an expandable section for the table
        with st.expander("View Monthly Basic Premium RWF by Product"):
            st.dataframe(monthly_premium.style.format(precision=2))

    # Group data by "Start Year" and "Status" and sum the Basic Premium RWF
    premium_by_year_and_status_health = df_health.groupby(['Start Year', 'Status'])['Basic Premium RWF'].sum().reset_index()
    premium_by_year_and_status_proactiv = df_proactiv.groupby(['Start Year', 'Status'])['Basic Premium RWF'].sum().reset_index()

    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        fig_premium_by_year_and_status_health = go.Figure()

        # Add bar traces for each status with custom colors
        for i, status in enumerate(premium_by_year_and_status_health['Status'].unique()):
            filtered_data = premium_by_year_and_status_health[premium_by_year_and_status_health['Status'] == status]
            fig_premium_by_year_and_status_health.add_trace(go.Bar(
                x=filtered_data['Start Year'],
                y=filtered_data['Basic Premium RWF'],
                text=filtered_data['Basic Premium RWF'],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y',
                name=status,
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        # Set layout for the chart
        fig_premium_by_year_and_status_health.update_layout(
            xaxis_title="Start Year",
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
        st.markdown('<h3 class="custom-subheader">Expected Health Sales by Year and Status</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_year_and_status_health, use_container_width=True)

    with cls2:
        fig_premium_by_year_and_status_proactiv = go.Figure()

        # Add bar traces for each status with custom colors
        for i, status in enumerate(premium_by_year_and_status_proactiv['Status'].unique()):
            filtered_data = premium_by_year_and_status_proactiv[premium_by_year_and_status_proactiv['Status'] == status]
            fig_premium_by_year_and_status_proactiv.add_trace(go.Bar(
                x=filtered_data['Start Year'],
                y=filtered_data['Basic Premium RWF'],
                text=filtered_data['Basic Premium RWF'],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y',
                name=status,
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        # Set layout for the chart
        fig_premium_by_year_and_status_proactiv.update_layout(
            xaxis_title="Start Year",
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
        st.markdown('<h3 class="custom-subheader">Expected ProActiv Sales by Year and Status</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_year_and_status_proactiv, use_container_width=True)

    # Display the grouped dataframes in expanders
    cl1, cl2 = st.columns(2)

    with cl1:
        with st.expander("Total Health sales by cover type"):
            st.dataframe(premium_by_year_and_status_health.style.format(precision=2))
            
    with cl2:
        with st.expander("Total ProActiv sales by cover type"):
            st.dataframe(premium_by_year_and_status_proactiv.style.format(precision=2))

    # Group data by "Start Year" and "Status" and sum the Basic Premium RWF
    premium_by_year_and_status_health = df_health.groupby(['Status', 'Engagement'])['Basic Premium RWF'].sum().reset_index()

    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        fig_premium_by_year_and_status_health = go.Figure()

        # Add bar traces for each status with custom colors
        for i, status in enumerate(premium_by_year_and_status_health['Engagement'].unique()):
            filtered_data = premium_by_year_and_status_health[premium_by_year_and_status_health['Engagement'] == status]
            fig_premium_by_year_and_status_health.add_trace(go.Bar(
                x=filtered_data['Status'],
                y=filtered_data['Basic Premium RWF'],
                text=filtered_data['Basic Premium RWF'],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y',
                name=status,
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        # Set layout for the chart
        fig_premium_by_year_and_status_health.update_layout(
            xaxis_title="Status",
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
        st.markdown('<h3 class="custom-subheader">Expected Sales by Status and Engagement</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_year_and_status_health, use_container_width=True)
