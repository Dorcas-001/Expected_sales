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

st.markdown('<h1 class="main-title">Sales Status View</h1>', unsafe_allow_html=True)

filepath="prospect_sales_data.xlsx"
sheet_name = "Eden - Team 1 LeadSheet (Master"
# Read all sheets into a dictionary of DataFrames
df = pd.read_excel(filepath, sheet_name=sheet_name)



# Ensure the 'Start Date' column is in datetime format
df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'])
df['Last Contact Date'] = pd.to_datetime(df['Last Contact Date'])

df['Days Difference'] = (df['Expected Close Date'] - df['Last Contact Date']).dt.days

df
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
owner = st.sidebar.multiselect("Select Sales Person", options=df['Owner'].unique())
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


df_closed = df[(df['Status'] == 'Closed 💪')]
df_lost = df[df['Status'] == 'Lost 😢']


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

    display_metric(col1, "Average Expected Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    display_metric(col2, "Average Expected Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")

    display_metric(col3, "Total Closed Sales", f"RWF {total_closed:.0f} M")
    display_metric(col1, "Total Lost Sales", f"RWF {total_lost:.0f} M",)
    display_metric(col2, "Percentage Closed Sales", value=f"{percent_closed:.1f} %")
    display_metric(col3, "Percentage Lost Sales", value=f"{percent_lost:.1f} %")


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

    cols1, cols2 = st.columns(2)

    custom_colors = ["#006E7F", "#e66c37", "#461b09","#009DAE", "#f8a785", "#CC3636"]

  
    # Group data by "Owner" and sum the Basic Premium RWF
    premium_by_intermediary = df.groupby('Owner')['Basic Premium RWF'].sum().reset_index()

    # Calculate the number of sales by "Owner"
    sales_by_cover = df.groupby('Owner').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_df = premium_by_intermediary.merge(sales_by_cover, on='Owner')

    # Sort the merged data by Basic Premium RWF in descending order and select the top 10 owners
    top_10_owners = merged_df.sort_values(by='Basic Premium RWF', ascending=False).head(10)



    with cols1:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Basic Premium RWF
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=top_10_owners['Owner'],
            y=top_10_owners['Basic Premium RWF'],
            text=top_10_owners['Basic Premium RWF'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Basic Premium RWF'
        ))

        # Add scatter trace for Number of Sales on secondary y-axis
        fig_premium_by_intermediary.add_trace(go.Scatter(
            x=top_10_owners['Owner'],
            y=top_10_owners['Number of Sales'],
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            marker=dict(color='red', size=10),
            line=dict(color='red', width=2)
        ))

        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Intermediary Name",
            yaxis=dict(
                title="Basic Premium RWF",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),
            yaxis2=dict(
                title="Number of Sales",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Sales and Number of Sales by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)
 
    # Group data by "Start Month", "Owner", and sum the Basic Premium RWF
    premium_by_intermediary = df.groupby(['Start Month', 'Owner'])['Basic Premium RWF'].sum().reset_index()

    # Calculate the number of sales by "Start Month" and "Owner"
    sales_by_cover = df.groupby(['Start Month', 'Owner']).size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_df = premium_by_intermediary.merge(sales_by_cover, on=['Start Month', 'Owner'])

    # Sort the merged data by Basic Premium RWF in descending order and select the top 10 owners
    top_10_owners = merged_df.sort_values(by='Basic Premium RWF', ascending=False).head(10)

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#009DAE", "#f8a785", "#CC3636"]

    with cols2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for each owner with custom colors
        for i, owner in enumerate(top_10_owners['Owner'].unique()):
            owner_data = top_10_owners[top_10_owners['Owner'] == owner]
            fig_premium_by_intermediary.add_trace(go.Bar(
                x=owner_data['Start Month'],
                y=owner_data['Basic Premium RWF'],
                text=owner_data['Basic Premium RWF'],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y',
                name=owner,
                marker_color=custom_colors[i % len(custom_colors)]  # Cycle through custom colors
            ))

        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Month",
            yaxis_title="Basic Premium RWF",
            barmode='group',
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3>Total Sales and Number of Sales by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)

    # Group data by "Intermediary name" and sum the Basic Premium RWF
    premium_by_intermediary = eden_care_df.groupby('Intermediary name')['Basic Premium RWF'].sum().reset_index()

    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = eden_care_df.groupby('Intermediary name').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_data = premium_by_intermediary.merge(sales_by_intermediary, on='Intermediary name')



    with colc2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Basic Premium RWF
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged_data['Intermediary name'],
            y=merged_data['Basic Premium RWF'],
            text=merged_data['Basic Premium RWF'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Basic Premium RWF'
        ))

        # Add scatter trace for Number of Sales on secondary y-axis
        fig_premium_by_intermediary.add_trace(go.Scatter(
            x=merged_data['Intermediary name'],
            y=merged_data['Number of Sales'],
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            marker=dict(color='red', size=10),
            line=dict(color='red', width=2)
        ))

        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Intermediary Name",
            yaxis=dict(
                title="Basic Premium RWF",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),
            yaxis2=dict(
                title="Number of Sales",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Sales and Number of Sales by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)



    cl1, cl2 =st.columns(2)

    with cl2:
        with st.expander("Premium for Sales Team"):
            st.dataframe(sales_by_intermediary.style.format(precision=2))
        
    with cl1:  
            with st.expander("Basic Premium RWF by Sales Team over Time"):
                    st.dataframe(area_chart_total_lives.style.format(precision=2))



    # Group data by "Start Date Month" and "Client Segment" and sum the Basic Premium RWF
    monthly_premium = eden_care_df.groupby(['Start Month', 'Intermediary name'])['Basic Premium RWF'].sum().unstack().fillna(0)



    fig_monthly_premium = go.Figure()

    for idx, Client_Segment in enumerate(monthly_premium.columns):
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))


        # Set layout for the Basic Premium RWF chart
    fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Basic Premium RWF",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Basic Premium RWF chart in Streamlit
    st.markdown('<h3 class="custom-subheader">Monthly Sales Distribution by Sales Team</h3>', unsafe_allow_html=True)
    st.plotly_chart(fig_monthly_premium, use_container_width=True)


  
        # Expander for IQR table
    with st.expander("Target and premuim by Product"):
            st.dataframe(monthly_premium.style.format(precision=2))



    colc1, colc2 = st.columns(2)
    

    # Group data by "Intermediary name" and "Cover Type" and sum the Basic Premium RWF
    cover_type_by_intermediary = eden_care_df.groupby(['Intermediary name', 'Cover Type'])['Basic Premium RWF'].sum().unstack().fillna(0)


    with colc1:
        fig_cover_type_by_intermediary = go.Figure()

        for idx, cover_type in enumerate(cover_type_by_intermediary.columns):
            fig_cover_type_by_intermediary.add_trace(go.Bar(
                x=cover_type_by_intermediary.index,
                y=cover_type_by_intermediary[cover_type],
                name=cover_type,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Set layout for the Basic Premium RWF chart
        fig_cover_type_by_intermediary.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Intermediary Name",
            yaxis_title="Basic Premium RWF",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Basic Premium RWF chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Sales Distribution by Cover Type by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_cover_type_by_intermediary, use_container_width=True)



    # Group by Client Name and Client Segment, then sum the Basic Premium RWF
    df_grouped = eden_care_df.groupby(['Client Name', 'Intermediary name'])['Basic Premium RWF'].sum().nlargest(15).reset_index()

    # Get the top 10 clients by Basic Premium RWF
    top_10_clients = df_grouped.groupby('Client Name')['Basic Premium RWF'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]
    # Sort the client_df by Basic Premium RWF in descending order
    client_df = client_df.sort_values(by='Basic Premium RWF', ascending=False)


    with colc2:
        # Create the bar chart
        fig = go.Figure()


                # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Intermediary name'].unique()):
                    Client_Segment_data = client_df[client_df['Intermediary name'] == Client_Segment]
                    fig.add_trace(go.Bar(
                        x=Client_Segment_data['Client Name'],
                        y=Client_Segment_data['Basic Premium RWF'],
                        name=Client_Segment,
                        text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Basic Premium RWF']],
                        textposition='auto',
                        marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                    ))

        fig.update_layout(
                    barmode='stack',
                    yaxis_title="Basic Premium RWF",
                    xaxis_title="Client Name",
                    font=dict(color='Black'),
                    xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    margin=dict(l=0, r=0, t=30, b=50)
                )

                # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Client Sales by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    colc1, colc2 = st.columns(2)
    with colc2:  
        with st.expander("Client Premium by Sales Team"):
                st.dataframe(client_df.style.format(precision=2))

    with colc1:
        # Expander for IQR table
        with st.expander("Premium for Sales Team"):
            st.dataframe(cover_type_by_intermediary.style.format(precision=2))

