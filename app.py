import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, List
import os
from dotenv import load_dotenv
from ivr_database import IVRDatabase

# Load environment variables
load_dotenv()

def get_config(key: str, default: str = '') -> str:
    """Get configuration from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets.get(key, default)
    except (AttributeError, FileNotFoundError):
        # Fall back to environment variables (for local development)
        return os.getenv(key, default)


# Page configuration
st.set_page_config(
    page_title="Exotel IVR Dashboard",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Exotel API Configuration
EXOTEL_API_KEY = get_config('EXOTEL_API_KEY', '')
EXOTEL_API_TOKEN = get_config('EXOTEL_API_TOKEN', '')
EXOTEL_SID = get_config('EXOTEL_SID', '')
EXOTEL_BASE_URL = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}"

class ExotelAPI:
    """Handler for Exotel API interactions"""
    
    def __init__(self, api_key: str, api_token: str, sid: str):
        self.api_key = api_key
        self.api_token = api_token
        self.sid = sid
        self.base_url = f"https://api.exotel.com/v1/Accounts/{sid}"
        self.auth = (api_key, api_token)
    
    def get_calls(self, start_date: str = None, end_date: str = None, limit: int = 100) -> pd.DataFrame:
        """Fetch call logs from Exotel API and return as DataFrame"""
        try:
            url = f"{self.base_url}/Calls.json"
            params = {"PageSize": limit}
            
            if start_date:
                params["StartTime"] = start_date
            if end_date:
                params["EndTime"] = end_date
            
            response = requests.get(url, auth=self.auth, params=params, timeout=10)
            
            if response.status_code == 200:
                calls_data = response.json().get('Calls', [])
                if calls_data:
                    # Convert to DataFrame and normalize field names
                    df = pd.DataFrame(calls_data)
                    # Map Exotel fields to our expected format
                    if 'Sid' in df.columns:
                        df['CallSid'] = df['Sid']
                    if 'Price' not in df.columns:
                        df['Price'] = 0.0
                    
                    # Add IVR columns if they don't exist (API doesn't provide IVR data yet)
                    if 'IVRPath' not in df.columns:
                        df['IVRPath'] = None
                    if 'IVRSelections' not in df.columns:
                        df['IVRSelections'] = None
                    
                    return df
                return pd.DataFrame()
            else:
                st.error(f"API Error: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching calls: {str(e)}")
            return pd.DataFrame()
    
    def get_call_details(self, call_sid: str) -> Dict:
        """Get detailed information for a specific call"""
        try:
            url = f"{self.base_url}/Calls/{call_sid}.json"
            response = requests.get(url, auth=self.auth, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            st.error(f"Error fetching call details: {str(e)}")
            return {}

def generate_sample_data(days: int = 7) -> pd.DataFrame:
    """Generate sample call data for demonstration"""
    import random
    from datetime import datetime, timedelta
    
    statuses = ['completed', 'busy', 'no-answer', 'failed', 'canceled']
    call_types = ['inbound', 'outbound']
    
    # Actual IVR flow based on business requirements
    ivr_flows = [
        # Language + State + Service flows
        ['1', '1', '1'],  # Hindi -> Rajasthan -> Sell Machine
        ['1', '1', '2'],  # Hindi -> Rajasthan -> Buy Old
        ['1', '1', '3'],  # Hindi -> Rajasthan -> Buy New
        ['1', '1', '4'],  # Hindi -> Rajasthan -> Finance
        ['1', '1', '5'],  # Hindi -> Rajasthan -> Other Info
        ['1', '2', '1'],  # Hindi -> MP -> Sell
        ['1', '2', '2'],  # Hindi -> MP -> Buy Old
        ['1', '2', '4'],  # Hindi -> MP -> Finance
        ['1', '3', '1'],  # Hindi -> Maharashtra -> Sell
        ['1', '3', '2'],  # Hindi -> Maharashtra -> Buy Old
        ['1', '4'],       # Hindi -> Other State (ends)
        ['2', '1', '1'],  # English -> Rajasthan -> Sell
        ['2', '1', '2'],  # English -> Rajasthan -> Buy Old
        ['2', '2', '2'],  # English -> MP -> Buy Old
        ['2', '3', '4'],  # English -> Maharashtra -> Finance
        
        # Complete flows - Buy Old Machine
        ['1', '1', '2', '1'],  # Buy Old -> 2020+ models
        ['1', '1', '2', '2'],  # Buy Old -> 2018-2020
        ['1', '1', '2', '3'],  # Buy Old -> 2015-2017
        ['1', '1', '2', '4'],  # Buy Old -> Before 2014
        ['1', '2', '2', '1', '1'],  # Buy Old 2020+ -> 49 HP
        ['1', '2', '2', '1', '2'],  # Buy Old 2020+ -> 74 HP
        
        # Complete flows - Sell Machine
        ['1', '1', '1', '1'],  # Sell -> Before 2014
        ['1', '1', '1', '2'],  # Sell -> 2015-2017
        ['1', '1', '1', '3'],  # Sell -> 2018-2020
        ['1', '1', '1', '4'],  # Sell -> After 2020
        ['2', '2', '1', '2'],  # English -> MP -> Sell -> 2015-2017
        
        # Finance flows
        ['1', '1', '4', '1'],  # Finance -> Refinance
        ['1', '1', '4', '2'],  # Finance -> New Finance
        ['2', '1', '4', '1'],  # English -> Rajasthan -> Finance -> Refinance
        
        # Consultant requests
        ['1', '1', '9'],  # Talk to consultant
        ['2', '2', '9'],  # Talk to consultant
        
        None,  # No IVR interaction (dropped early)
    ]
    
    data = []
    for i in range(200):
        date = datetime.now() - timedelta(days=random.randint(0, days), 
                                         hours=random.randint(0, 23),
                                         minutes=random.randint(0, 59))
        
        ivr_selection = random.choice(ivr_flows)
        ivr_path = '-'.join(ivr_selection) if ivr_selection else None
        
        data.append({
            'CallSid': f'CA{i:08d}',
            'DateCreated': date,
            'From': f'+91{random.randint(6000000000, 9999999999)}',
            'To': f'+91{random.randint(6000000000, 9999999999)}',
            'Status': random.choice(statuses),
            'Duration': random.randint(10, 600) if random.choice([True, False, False]) else 0,
            'Direction': random.choice(call_types),
            'Price': round(random.uniform(0.5, 5.0), 2),
            'RecordingUrl': f'https://example.com/recording/{i}.mp3' if random.choice([True, False]) else None,
            'IVRPath': ivr_path,
            'IVRSelections': ivr_selection
        })
    
    return pd.DataFrame(data)

def get_ivr_label(path: str) -> str:
    """Get human-readable label for IVR path"""
    if not path:
        return "No IVR"
    
    parts = path.split('-')
    labels = []
    
    # Step 1: Language
    if len(parts) >= 1:
        lang = {'1': 'Hindi', '2': 'English'}.get(parts[0], f'Lang-{parts[0]}')
        labels.append(lang)
    
    # Step 2: State
    if len(parts) >= 2:
        state = {
            '1': 'Rajasthan',
            '2': 'MP',
            '3': 'Maharashtra',
            '4': 'Other State'
        }.get(parts[1], f'State-{parts[1]}')
        labels.append(state)
    
    # Step 3: Service
    if len(parts) >= 3:
        service = {
            '1': 'Sell Machine',
            '2': 'Buy Old',
            '3': 'Buy New',
            '4': 'Finance',
            '5': 'Other Info',
            '9': 'Consultant'
        }.get(parts[2], f'Service-{parts[2]}')
        labels.append(service)
    
    # Step 4: Additional details based on service
    if len(parts) >= 4:
        if parts[2] == '2':  # Buy Old Machine
            model = {
                '1': '2020+',
                '2': '2018-2020',
                '3': '2015-2017',
                '4': 'Before 2014'
            }.get(parts[3], f'Model-{parts[3]}')
            labels.append(model)
        elif parts[2] == '1':  # Sell Machine
            model = {
                '1': 'Before 2014',
                '2': '2015-2017',
                '3': '2018-2020',
                '4': '2020+'
            }.get(parts[3], f'Model-{parts[3]}')
            labels.append(model)
        elif parts[2] == '4':  # Finance
            fin = {
                '1': 'Refinance',
                '2': 'New Finance'
            }.get(parts[3], f'Finance-{parts[3]}')
            labels.append(fin)
    
    # Step 5: HP selection for 2020+ old machines
    if len(parts) >= 5 and parts[2] == '2' and parts[3] == '1':
        hp = {'1': '49 HP', '2': '74 HP'}.get(parts[4], f'HP-{parts[4]}')
        labels.append(hp)
    
    return ' → '.join(labels)

def create_metrics_section(df: pd.DataFrame):
    """Display key metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_calls = len(df)
    completed_calls = len(df[df['Status'] == 'completed'])
    avg_duration = df[df['Duration'] > 0]['Duration'].mean()
    total_cost = df['Price'].sum()
    
    with col1:
        st.metric("Total Calls", f"{total_calls:,}")
    
    with col2:
        completion_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0
        st.metric("Completed Calls", f"{completed_calls:,}", 
                 f"{completion_rate:.1f}%")
    
    with col3:
        st.metric("Avg Duration", f"{avg_duration:.0f}s" if pd.notna(avg_duration) else "N/A")
    
    with col4:
        st.metric("Total Cost", f"₹{total_cost:.2f}")

def create_call_status_chart(df: pd.DataFrame):
    """Create call status distribution chart"""
    status_counts = df['Status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Call Status Distribution",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_call_volume_chart(df: pd.DataFrame):
    """Create call volume over time chart"""
    df['Date'] = pd.to_datetime(df['DateCreated']).dt.date
    daily_calls = df.groupby('Date').size().reset_index(name='Calls')
    
    fig = px.line(
        daily_calls,
        x='Date',
        y='Calls',
        title="Call Volume Over Time",
        markers=True
    )
    
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(height=400, hovermode='x unified')
    
    return fig

def create_duration_distribution(df: pd.DataFrame):
    """Create call duration distribution"""
    df_with_duration = df[df['Duration'] > 0].copy()
    
    fig = px.histogram(
        df_with_duration,
        x='Duration',
        nbins=30,
        title="Call Duration Distribution",
        labels={'Duration': 'Duration (seconds)', 'count': 'Number of Calls'}
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    return fig

def create_hourly_heatmap(df: pd.DataFrame):
    """Create hourly call pattern heatmap"""
    df['Hour'] = pd.to_datetime(df['DateCreated']).dt.hour
    df['Day'] = pd.to_datetime(df['DateCreated']).dt.day_name()
    
    # Define day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    pivot_table = df.pivot_table(
        values='CallSid',
        index='Day',
        columns='Hour',
        aggfunc='count',
        fill_value=0
    ).reindex(day_order)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='Blues',
        text=pivot_table.values,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Call Pattern Heatmap (Hour vs Day)",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400
    )
    
    return fig

def create_ivr_flow_chart(df: pd.DataFrame):
    """Create IVR option selection distribution chart"""
    ivr_data = df[df['IVRPath'].notna()].copy()
    
    if len(ivr_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No IVR data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    path_counts = ivr_data['IVRPath'].value_counts().head(10)
    labels = [get_ivr_label(path) for path in path_counts.index]
    
    fig = px.bar(
        x=path_counts.values,
        y=labels,
        orientation='h',
        title="Top 10 IVR Paths Selected",
        labels={'x': 'Number of Calls', 'y': 'IVR Path'},
        color=path_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    return fig

def create_ivr_funnel(df: pd.DataFrame):
    """Create IVR navigation funnel"""
    ivr_data = df[df['IVRSelections'].notna()].copy()
    
    if len(ivr_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No IVR data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Count calls at each level
    total_calls = len(ivr_data)
    level_1 = len(ivr_data[ivr_data['IVRSelections'].apply(lambda x: len(x) >= 1)])
    level_2 = len(ivr_data[ivr_data['IVRSelections'].apply(lambda x: len(x) >= 2)])
    level_3 = len(ivr_data[ivr_data['IVRSelections'].apply(lambda x: len(x) >= 3)])
    
    fig = go.Figure(go.Funnel(
        y=['Entered IVR', 'Level 1 Selection', 'Level 2 Selection', 'Level 3 Selection'],
        x=[total_calls, level_1, level_2, level_3],
        textinfo="value+percent initial",
        marker=dict(color=['#4472C4', '#70AD47', '#FFC000', '#C55A11'])
    ))
    
    fig.update_layout(
        title="IVR Navigation Funnel",
        height=400
    )
    
    return fig

def create_ivr_first_option_pie(df: pd.DataFrame):
    """Create pie chart for first IVR option selected"""
    ivr_data = df[df['IVRSelections'].notna()].copy()
    
    if len(ivr_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No IVR data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Extract first selection (Language)
    ivr_data['FirstOption'] = ivr_data['IVRSelections'].apply(lambda x: x[0] if x and len(x) > 0 else None)
    first_option_counts = ivr_data['FirstOption'].value_counts()
    
    option_labels = {
        '1': 'Hindi (1)',
        '2': 'English (2)'
    }
    
    labels = [option_labels.get(opt, f'Option {opt}') for opt in first_option_counts.index]
    
    fig = px.pie(
        values=first_option_counts.values,
        names=labels,
        title="First IVR Option Selected",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_ivr_completion_rate(df: pd.DataFrame):
    """Show IVR completion vs drop-off rates"""
    ivr_data = df[df['IVRSelections'].notna()].copy()
    no_ivr = len(df[df['IVRSelections'].isna()])
    
    if len(ivr_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No IVR data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Consider completion as reaching level 2 or 3
    completed = len(ivr_data[ivr_data['IVRSelections'].apply(lambda x: len(x) >= 2)])
    dropped = len(ivr_data[ivr_data['IVRSelections'].apply(lambda x: len(x) < 2)])
    
    fig = go.Figure(data=[
        go.Bar(
            x=['Completed IVR', 'Dropped Early', 'No IVR Interaction'],
            y=[completed, dropped, no_ivr],
            marker=dict(color=['#70AD47', '#FFC000', '#C55A11']),
            text=[completed, dropped, no_ivr],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="IVR Completion Analysis",
        yaxis_title="Number of Calls",
        height=400,
        showlegend=False
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📞 Exotel IVR Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Date range selector
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
        
        # Data source selector
        use_live_data = st.checkbox("Use Live Exotel Data", value=False, 
                                    help="Enable to fetch real data from Exotel API")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # API Status
        st.subheader("API Configuration")
        if EXOTEL_API_KEY and EXOTEL_API_TOKEN and EXOTEL_SID:
            st.success("✅ Exotel API Configured")
        else:
            st.warning("⚠️ Configure API credentials in .env file")
        
        # IVR Database Status
        try:
            ivr_db = IVRDatabase()
            ivr_paths = ivr_db.get_ivr_paths()
            if not ivr_paths.empty:
                st.success(f"✅ IVR Database: {len(ivr_paths)} records")
            else:
                st.info("📊 IVR Database: No data yet")
        except Exception as e:
            st.info("📊 IVR Database: Not initialized")
    
    # Load data
    if use_live_data and EXOTEL_API_KEY and EXOTEL_API_TOKEN and EXOTEL_SID:
        with st.spinner("Fetching data from Exotel..."):
            api = ExotelAPI(EXOTEL_API_KEY, EXOTEL_API_TOKEN, EXOTEL_SID)
            
            # Format dates for API
            start_date = None
            end_date = None
            if len(date_range) == 2:
                start_date = date_range[0].strftime('%Y-%m-%d')
                end_date = date_range[1].strftime('%Y-%m-%d')
            
            df = api.get_calls(start_date=start_date, end_date=end_date, limit=1000)
            
            if df.empty:
                st.warning("No data available from Exotel API for the selected date range. Using sample data.")
                df = generate_sample_data()
            else:
                # Try to merge with IVR database
                try:
                    ivr_db = IVRDatabase()
                    df = ivr_db.merge_with_call_data(df)
                    st.success("✅ IVR data merged from local database")
                except Exception as e:
                    st.info(f"ℹ️ Using API data only (no IVR database data)")
                    # Ensure IVR columns exist
                    if 'IVRPath' not in df.columns:
                        df['IVRPath'] = None
                        df['IVRSelections'] = None
    else:
        df = generate_sample_data()
    
    # Filter by date range (for sample data)
    if len(date_range) == 2 and not use_live_data and not df.empty:
        df['DateCreated'] = pd.to_datetime(df['DateCreated'])
        mask = (df['DateCreated'].dt.date >= date_range[0]) & (df['DateCreated'].dt.date <= date_range[1])
        df = df[mask].copy()
    
    # Metrics Section
    st.header("📊 Key Metrics")
    create_metrics_section(df)
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Analytics", "📋 Call Logs", "🔥 Heatmap", "💰 Cost Analysis", "🔀 IVR Flow", "📄 Raw Data"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_call_status_chart(df), width='stretch')
        
        with col2:
            st.plotly_chart(create_duration_distribution(df), width='stretch')
        
        st.plotly_chart(create_call_volume_chart(df), width='stretch')
    
    with tab2:
        st.subheader("Recent Call Logs")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=df['Status'].unique(),
                default=df['Status'].unique()
            )
        
        with col2:
            direction_filter = st.multiselect(
                "Filter by Direction",
                options=df['Direction'].unique(),
                default=df['Direction'].unique()
            )
        
        with col3:
            search_number = st.text_input("Search Phone Number", "")
        
        # Apply filters
        filtered_df = df[
            (df['Status'].isin(status_filter)) &
            (df['Direction'].isin(direction_filter))
        ]
        
        if search_number:
            filtered_df = filtered_df[
                (filtered_df['From'].str.contains(search_number)) |
                (filtered_df['To'].str.contains(search_number))
            ]
        
        # Display table
        st.dataframe(
            filtered_df[['DateCreated', 'From', 'To', 'Status', 'Duration', 'Direction', 'Price']].sort_values('DateCreated', ascending=False),
            width='stretch',
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Call Logs",
            data=csv,
            file_name=f"call_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.plotly_chart(create_hourly_heatmap(df), width='stretch')
        
        # Additional insights
        col1, col2 = st.columns(2)
        
        with col1:
            peak_hour = df.groupby(pd.to_datetime(df['DateCreated']).dt.hour).size().idxmax()
            st.info(f"🕐 Peak Hour: {peak_hour}:00 - {peak_hour+1}:00")
        
        with col2:
            peak_day = df.groupby(pd.to_datetime(df['DateCreated']).dt.day_name()).size().idxmax()
            st.info(f"📅 Busiest Day: {peak_day}")
    
    with tab4:
        st.subheader("Cost Analysis")
        
        # Cost metrics
        col1, col2, col3 = st.columns(3)
        
        total_cost = df['Price'].sum()
        avg_cost = df['Price'].mean()
        cost_per_completed = df[df['Status'] == 'completed']['Price'].sum()
        
        with col1:
            st.metric("Total Cost", f"₹{total_cost:.2f}")
        
        with col2:
            st.metric("Avg Cost/Call", f"₹{avg_cost:.2f}")
        
        with col3:
            st.metric("Cost (Completed)", f"₹{cost_per_completed:.2f}")
        
        # Daily cost chart
        df['Date'] = pd.to_datetime(df['DateCreated']).dt.date
        daily_cost = df.groupby('Date')['Price'].sum().reset_index()
        
        fig = px.bar(
            daily_cost,
            x='Date',
            y='Price',
            title="Daily Cost Breakdown",
            labels={'Price': 'Cost (₹)'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
    
    with tab5:
        st.subheader("IVR Flow Analysis")
        
        # Check if IVR data is available
        if 'IVRPath' not in df.columns or df['IVRPath'].isna().all():
            st.info("📌 **IVR data is not available in the current dataset.**\n\n"
                   "This feature works with sample data or when IVR tracking is configured in your Exotel flow. "
                   "Disable 'Use Live Exotel Data' in the sidebar to see sample IVR analysis.")
        else:
            # IVR Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            ivr_data = df[df['IVRPath'].notna()]
            total_ivr_calls = len(ivr_data)
            ivr_completion = len(ivr_data[ivr_data['IVRSelections'].apply(lambda x: len(x) >= 2 if x else False)])
            completion_rate = (ivr_completion / total_ivr_calls * 100) if total_ivr_calls > 0 else 0
            avg_selections = ivr_data['IVRSelections'].apply(lambda x: len(x) if x else 0).mean()
            
            with col1:
                st.metric("IVR Interactions", f"{total_ivr_calls:,}")
            
            with col2:
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            with col3:
                st.metric("Avg Selections", f"{avg_selections:.1f}")
            
            with col4:
                drop_off_rate = 100 - completion_rate
                st.metric("Drop-off Rate", f"{drop_off_rate:.1f}%")
            
            st.divider()
            
            # IVR visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_ivr_first_option_pie(df), width='stretch')
            
            with col2:
                st.plotly_chart(create_ivr_funnel(df), width='stretch')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_ivr_flow_chart(df), width='stretch')
            
            with col2:
                st.plotly_chart(create_ivr_completion_rate(df), width='stretch')
            
            # IVR Path Details Table
            st.subheader("Detailed IVR Path Analysis")
            
            if len(ivr_data) > 0:
                path_analysis = ivr_data.groupby('IVRPath').agg({
                    'CallSid': 'count',
                    'Duration': 'mean',
                    'Status': lambda x: (x == 'completed').sum()
                }).reset_index()
                
                path_analysis.columns = ['IVR Path', 'Total Calls', 'Avg Duration (s)', 'Completed Calls']
                path_analysis['Completion %'] = (path_analysis['Completed Calls'] / path_analysis['Total Calls'] * 100).round(1)
                path_analysis['Path Label'] = path_analysis['IVR Path'].apply(get_ivr_label)
                path_analysis['Avg Duration (s)'] = path_analysis['Avg Duration (s)'].round(0)
                
                # Reorder columns
                path_analysis = path_analysis[['Path Label', 'IVR Path', 'Total Calls', 'Avg Duration (s)', 'Completed Calls', 'Completion %']]
                path_analysis = path_analysis.sort_values('Total Calls', ascending=False)
                
                st.dataframe(path_analysis, width='stretch', hide_index=True)
                
                # Raw IVR Data Section
                st.divider()
                st.subheader("📋 Raw IVR Selection Data")
                
                # Create detailed view with individual call IVR selections
                raw_ivr_display = ivr_data[['CallSid', 'DateCreated', 'From', 'IVRPath', 'IVRSelections', 'Duration', 'Status']].copy()
                raw_ivr_display['Path Description'] = raw_ivr_display['IVRPath'].apply(get_ivr_label)
                raw_ivr_display['Selections'] = raw_ivr_display['IVRSelections'].apply(lambda x: ' → '.join(x) if x else '')
                
                # Reorder for display
                raw_ivr_display = raw_ivr_display[['CallSid', 'DateCreated', 'From', 'Path Description', 'Selections', 'Duration', 'Status']]
                raw_ivr_display = raw_ivr_display.sort_values('DateCreated', ascending=False)
                
                st.dataframe(raw_ivr_display, width='stretch', hide_index=True)
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_analysis = path_analysis.to_csv(index=False)
                    st.download_button(
                        label="📥 Download IVR Analysis",
                        data=csv_analysis,
                        file_name=f"ivr_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    csv_raw = raw_ivr_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Raw IVR Data",
                        data=csv_raw,
                        file_name=f"raw_ivr_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No IVR interaction data available.")
    
    with tab6:
        st.subheader("📄 Raw API Data")
        
        # Important note about IVR data
        st.warning("⚠️ **Important: IVR Digit Inputs Not Available in Standard API**\n\n"
                  "The Exotel Calls API (`/Calls.json`) does **not** return IVR digit inputs (button presses). "
                  "To capture what digits users pressed during IVR:\n\n"
                  "1. Add a **Passthru applet** after each Gather/IVR applet in your Exotel flow\n"
                  "2. Configure the Passthru to send data to your webhook URL\n"
                  "3. The `digits` parameter will contain the user's input\n"
                  "4. Store this data in your database and link it to the CallSid\n\n"
                  "📚 [Learn more about Passthru applet](https://support.exotel.com/support/solutions/articles/48283-working-with-passthru-applet)")
        
        # Display data source
        if use_live_data and EXOTEL_API_KEY and EXOTEL_API_TOKEN and EXOTEL_SID:
            st.info("📡 Showing **Live Data** from Exotel API")
            
            # Show API endpoint being used
            st.code(f"GET https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls.json", language="bash")
            
            # Show what fields are available
            st.info("**Available Fields:** CallSid, DateCreated, From, To, Status, Duration, Direction, Price, RecordingUrl\n\n"
                   "**Missing Fields:** IVR digit inputs (requires Passthru applet setup)")
            
            # Setup guide
            with st.expander("📖 How to Capture IVR Inputs - Setup Guide"):
                st.markdown("""
                ### Step-by-Step Guide to Capture IVR Digit Inputs
                
                **Current Situation:**
                - ❌ The `/Calls.json` API does NOT return IVR digits
                - ✅ IVR digits are available through Passthru applet callbacks
                
                **Solution: Set up Passthru Applets**
                
                1. **Go to Exotel Dashboard** → [Flows/Applets](https://my.exotel.com/apps)
                
                2. **Edit your IVR Flow:**
                   - After each **Gather** or **IVR Menu** applet
                   - Add a **Passthru** applet
                   
                3. **Configure Passthru:**
                   - URL: `https://your-server.com/exotel/callback`
                   - The callback will receive a `digits` parameter
                   
                4. **Capture the Data:**
                   ```python
                   # Example Flask/FastAPI endpoint
                   @app.get("/exotel/callback")
                   def exotel_callback(CallSid: str, digits: str):
                       # Store in database
                       db.save_ivr_data(CallSid, digits)
                       return "OK"
                   ```
                
                5. **Link to Call Data:**
                   - Use `CallSid` to match IVR inputs with call records
                   - Store in your database with timestamp
                
                **Parameters you'll receive in Passthru:**
                - `CallSid` - Unique call identifier
                - `digits` - The numbers pressed by user (e.g., "1", "12", "123")
                - `CallFrom`, `CallTo` - Phone numbers
                - `CallStatus` - Call status
                
                **Alternative: Use CustomField**
                If you're making API calls to trigger the flow, you can pass a `CustomField`:
                ```bash
                curl -X POST https://api.exotel.com/v1/Accounts/{SID}/Calls/connect \\
                  -u API_KEY:API_TOKEN \\
                  -d "From=<number>&To=<number>&CustomField=user_id_123"
                ```
                The CustomField will be available in Passthru callbacks.
                """)
            
            # Option to fetch fresh data
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🔄 Fetch Fresh Data", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            
            with col2:
                test_call_sid = st.text_input("Test Single Call Details", placeholder="Enter CallSid")
            
            with col3:
                if test_call_sid and st.button("📞 Get Call Details"):
                    with st.spinner("Fetching call details..."):
                        api = ExotelAPI(EXOTEL_API_KEY, EXOTEL_API_TOKEN, EXOTEL_SID)
                        call_details = api.get_call_details(test_call_sid)
                        if call_details:
                            st.json(call_details)
                            st.caption("💡 **Note:** The 'digits' field will only appear if you have a Passthru applet configured in your flow")
                        else:
                            st.error("Failed to fetch call details")
        else:
            st.info("🎲 Showing **Sample Data** for demonstration\n\n"
                   "Sample data includes simulated IVR selections. In production, you need to set up Passthru applets to capture real IVR inputs.")
        
        # Display total records
        st.metric("Total Records", len(df))
        
        st.divider()
        
        # Sample JSON Response (if available)
        if use_live_data and len(df) > 0:
            with st.expander("📋 View Sample API Response (First Record)"):
                sample_record = df.iloc[0].to_dict()
                # Convert timestamps to strings for JSON display
                for key, value in sample_record.items():
                    if pd.isna(value):
                        sample_record[key] = None
                    elif hasattr(value, 'isoformat'):
                        sample_record[key] = str(value)
                st.json(sample_record)
        
        # Show all columns
        st.subheader("All Columns")
        st.write(f"**Available columns:** {', '.join(df.columns.tolist())}")
        
        # Display full dataframe
        st.dataframe(
            df.sort_values('DateCreated', ascending=False),
            width='stretch',
            hide_index=True,
            height=600
        )
        
        # Download raw data
        col1, col2 = st.columns([1, 3])
        with col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Raw Data (CSV)",
                data=csv_data,
                file_name=f"raw_api_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Show data summary
        st.divider()
        st.subheader("Data Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Numeric Columns Summary:**")
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if numeric_cols:
                st.dataframe(df[numeric_cols].describe(), width='stretch')
            else:
                st.info("No numeric columns available")
        
        with col2:
            st.write("**Data Types:**")
            dtypes_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(dtypes_df, width='stretch', hide_index=True)

if __name__ == "__main__":
    main()
