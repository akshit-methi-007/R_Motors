# -*- coding: utf-8 -*-
"""
Rajesh Karegaar's Lead Management System
3-in-1 Dashboard: Telecaller | Sales | Supervisor
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# Page configuration
st.set_page_config(
    page_title="RK Lead Management System",
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
        margin-bottom: 1rem;
    }
    .hot-lead {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: pulse 2s infinite;
    }
    .warm-lead {
        background: linear-gradient(135deg, #ffd93d 0%, #ffe066 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .cold-lead {
        background: linear-gradient(135deg, #a8dadc 0%, #c7ecee 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    .metric-big {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-active { background-color: #51cf66; color: white; }
    .status-idle { background-color: #ffd93d; color: #333; }
    .status-break { background-color: #ff6b6b; color: white; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# Generate sample data
@st.cache_data
def generate_sample_leads():
    """Generate sample lead data"""
    states = ['Maharashtra', 'Gujarat', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Uttar Pradesh']
    machines = ['Excavator', 'Bulldozer', 'Loader', 'Crane', 'Forklift', 'Grader']
    hp_ranges = ['50-100', '100-200', '200-300', '300-500', '500+']
    statuses = ['Hot', 'Warm', 'Cold']
    outcomes = ['Pending', 'Closed', 'Follow-up', 'Lost', 'Pivoted']
    
    leads = []
    for i in range(50):
        lead_date = datetime.now() - timedelta(hours=random.randint(0, 72))
        leads.append({
            'Lead_ID': f'LD{1000+i}',
            'Customer_Name': f'Customer {i+1}',
            'Phone': f'+91{random.randint(7000000000, 9999999999)}',
            'State': random.choice(states),
            'Machine_Type': random.choice(machines),
            'HP': random.choice(hp_ranges),
            'Lead_Tag': random.choice(statuses),
            'Transfer_Type': random.choice(['Instant', 'Callback']),
            'Sales_Outcome': random.choice(outcomes),
            'Created_At': lead_date,
            'Assigned_To': random.choice(['Sales Rep 1', 'Sales Rep 2', 'Sales Rep 3', 'Unassigned']),
            'Wait_Time': random.randint(5, 180),  # minutes
            'TC_Duration': random.randint(60, 300),  # seconds
            'Sales_Duration': random.randint(120, 600),  # seconds
            'Notes': f'Sample notes for lead {i+1}'
        })
    
    return pd.DataFrame(leads)

@st.cache_data
def generate_team_status():
    """Generate team availability status"""
    team = [
        {'Name': 'Telecaller 1', 'Role': 'Telecaller', 'Status': 'Active', 'Current_Task': 'On Call'},
        {'Name': 'Telecaller 2', 'Role': 'Telecaller', 'Status': 'Idle', 'Current_Task': 'Available'},
        {'Name': 'Telecaller 3', 'Role': 'Telecaller', 'Status': 'Break', 'Current_Task': 'Break'},
        {'Name': 'Sales Rep 1', 'Role': 'Sales', 'Status': 'Active', 'Current_Task': 'On Call'},
        {'Name': 'Sales Rep 2', 'Role': 'Sales', 'Status': 'Idle', 'Current_Task': 'Available'},
        {'Name': 'Sales Rep 3', 'Role': 'Sales', 'Status': 'Active', 'Current_Task': 'Follow-up'},
    ]
    return pd.DataFrame(team)

# Login Function
def show_login():
    """Display login interface"""
    st.markdown('<h1 class="main-header">🏢 RK Lead Management System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        user_role = st.selectbox(
            "Select Your Role",
            ["Telecaller", "Sales Team", "Supervisor"],
            help="Choose your role to access the appropriate dashboard"
        )
        
        if user_role == "Telecaller":
            names = ["Telecaller 1", "Telecaller 2", "Telecaller 3"]
        elif user_role == "Sales Team":
            names = ["Sales Rep 1", "Sales Rep 2", "Sales Rep 3"]
        else:
            names = ["Supervisor", "Admin"]
        
        user_name = st.selectbox("Username", names)
        password = st.text_input("Password", type="password", value="demo123")
        
        st.info("💡 Demo Mode: Use any password to login")
        
        if st.button("🚀 Login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = user_role
            st.session_state.user_name = user_name
            st.rerun()

# Telecaller Dashboard
def show_telecaller_dashboard():
    """Dashboard for Telecaller - The Gatekeeper"""
    st.markdown('<h1 class="main-header">📞 Telecaller Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"**Welcome, {st.session_state.user_name}** | Role: Telecaller")
    
    # Incoming Call Simulator
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔔 Incoming Call")
        
        if st.button("🎧 Simulate Incoming Call", use_container_width=True):
            with st.spinner("📞 Call incoming..."):
                time.sleep(1)
                
                # Simulated IVR data
                ivr_data = {
                    'State': random.choice(['Maharashtra', 'Gujarat', 'Karnataka']),
                    'Machine_Type': random.choice(['Excavator', 'Bulldozer', 'Loader']),
                    'HP': random.choice(['50-100', '100-200', '200-300']),
                    'Phone': f'+91{random.randint(7000000000, 9999999999)}'
                }
                
                st.session_state.current_call = ivr_data
        
        # Show current call
        if 'current_call' in st.session_state:
            st.markdown('<div class="hot-lead">', unsafe_allow_html=True)
            st.markdown("### 🎯 Active Call - IVR Data Captured")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("📍 State", st.session_state.current_call['State'])
            with col_b:
                st.metric("🚜 Machine", st.session_state.current_call['Machine_Type'])
            with col_c:
                st.metric("⚡ HP", st.session_state.current_call['HP'])
            
            st.markdown(f"**📱 Phone:** {st.session_state.current_call['Phone']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Lead Qualification Form
            st.markdown("### ✍️ Lead Qualification")
            
            customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
            
            col1, col2 = st.columns(2)
            with col1:
                lead_tag = st.selectbox("Lead Category", ["Hot", "Warm", "Cold"], 
                                       help="Hot: Ready to buy | Warm: Interested | Cold: Not interested")
            with col2:
                transfer_type = st.radio("Action", ["Instant Transfer", "Queue for Callback"])
            
            notes = st.text_area("Notes", placeholder="Add any important notes about the conversation...")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✅ Save Lead", use_container_width=True, type="primary"):
                    st.success(f"✅ Lead saved as **{lead_tag}** with {transfer_type}!")
                    if lead_tag == "Hot" and transfer_type == "Instant Transfer":
                        st.balloons()
                        st.success("🔄 Call transferred to Sales Team!")
                    elif lead_tag == "Hot":
                        st.success("📋 Lead added to Hot Queue for Sales callback!")
                    del st.session_state.current_call
                    time.sleep(2)
                    st.rerun()
            
            with col_btn2:
                if st.button("❌ End Call", use_container_width=True):
                    st.warning("Call ended without saving")
                    del st.session_state.current_call
                    st.rerun()
    
    with col2:
        st.markdown("### 📊 Today's Stats")
        
        st.metric("📞 Calls Handled", random.randint(15, 35))
        st.metric("🔥 Hot Leads", random.randint(5, 12))
        st.metric("🌡️ Warm Leads", random.randint(8, 18))
        st.metric("❄️ Cold Leads", random.randint(2, 8))
        
        st.markdown("---")
        st.markdown("### ⏱️ Avg Call Duration")
        st.metric("", f"{random.randint(120, 240)} sec")

# Sales Dashboard
def show_sales_dashboard():
    """Dashboard for Sales Team - The Closer"""
    st.markdown('<h1 class="main-header">💼 Sales Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"**Welcome, {st.session_state.user_name}** | Role: Sales Team")
    
    df = generate_sample_leads()
    my_leads = df[df['Assigned_To'] == st.session_state.user_name].copy()
    if len(my_leads) == 0:
        my_leads = df.head(15).copy()  # Show some leads for demo
    
    # Hot Leads Section
    st.markdown("### 🔥 HOT LEADS - Call Now!")
    hot_leads = my_leads[my_leads['Lead_Tag'] == 'Hot'].sort_values('Wait_Time', ascending=False)
    
    if len(hot_leads) > 0:
        for idx, lead in hot_leads.head(3).iterrows():
            st.markdown('<div class="hot-lead">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.markdown(f"**👤 {lead['Customer_Name']}**")
                st.markdown(f"📱 {lead['Phone']}")
            
            with col2:
                st.markdown(f"🚜 {lead['Machine_Type']}")
                st.markdown(f"📍 {lead['State']} | ⚡ {lead['HP']} HP")
            
            with col3:
                st.markdown(f"⏱️ **{lead['Wait_Time']} min**")
                st.markdown("waiting")
            
            with col4:
                if st.button(f"📞 Call", key=f"call_hot_{idx}"):
                    st.success(f"📞 Calling {lead['Customer_Name']}...")
                if st.button(f"🎧 Listen", key=f"listen_hot_{idx}"):
                    st.info("🎧 Playing Telecaller recording...")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("")
    else:
        st.info("No hot leads at the moment")
    
    st.markdown("---")
    
    # Warm & Cold Leads in Tabs
    tab1, tab2 = st.tabs(["🌡️ Warm Leads", "❄️ Cold Leads"])
    
    with tab1:
        warm_leads = my_leads[my_leads['Lead_Tag'] == 'Warm']
        if len(warm_leads) > 0:
            for idx, lead in warm_leads.head(5).iterrows():
                with st.expander(f"👤 {lead['Customer_Name']} - {lead['Machine_Type']} ({lead['State']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Phone:** {lead['Phone']}")
                        st.write(f"**HP Range:** {lead['HP']}")
                        st.write(f"**Created:** {lead['Created_At'].strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        outcome = st.selectbox("Outcome", ["Pending", "Closed", "Follow-up", "Lost", "Pivoted"], 
                                             key=f"outcome_warm_{idx}")
                        if st.button("💾 Update", key=f"update_warm_{idx}"):
                            st.success(f"✅ Lead updated: {outcome}")
        else:
            st.info("No warm leads")
    
    with tab2:
        cold_leads = my_leads[my_leads['Lead_Tag'] == 'Cold']
        if len(cold_leads) > 0:
            st.dataframe(
                cold_leads[['Customer_Name', 'Phone', 'Machine_Type', 'State', 'Created_At']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No cold leads")
    
    # Stats Sidebar
    with st.sidebar:
        st.markdown("### 📊 My Performance")
        st.metric("Total Leads", len(my_leads))
        st.metric("Closed Today", len(my_leads[my_leads['Sales_Outcome'] == 'Closed']))
        st.metric("Pending", len(my_leads[my_leads['Sales_Outcome'] == 'Pending']))
        st.metric("Conversion %", f"{random.randint(15, 35)}%")

# Supervisor Dashboard
def show_supervisor_dashboard():
    """Dashboard for Supervisor - The Command Center"""
    st.markdown('<h1 class="main-header">👨‍💼 Supervisor Command Center</h1>', unsafe_allow_html=True)
    st.markdown(f"**Welcome, {st.session_state.user_name}** | Role: Supervisor")
    
    df = generate_sample_leads()
    team_df = generate_team_status()
    
    # Live Insights
    st.markdown("### 📡 Live Team Status")
    
    cols = st.columns(len(team_df))
    for idx, (col, member) in enumerate(zip(cols, team_df.itertuples())):
        with col:
            status_class = f"status-{member.Status.lower()}"
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 8px;">
                <div style="font-weight: bold;">{member.Name}</div>
                <div style="font-size: 0.875rem; color: #666;">{member.Role}</div>
                <div style="margin-top: 0.5rem;">
                    <span class="status-badge {status_class}">{member.Status}</span>
                </div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem; color: #888;">{member.Current_Task}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📞 Total Leads Today", len(df[df['Created_At'] > datetime.now() - timedelta(days=1)]))
    with col2:
        hot_count = len(df[df['Lead_Tag'] == 'Hot'])
        st.metric("🔥 Hot Leads", hot_count)
    with col3:
        closed = len(df[df['Sales_Outcome'] == 'Closed'])
        st.metric("✅ Closed Deals", closed)
    with col4:
        conversion = (closed / len(df) * 100) if len(df) > 0 else 0
        st.metric("📈 Conversion Rate", f"{conversion:.1f}%")
    
    st.markdown("---")
    
    # Analytics Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Conversion Funnel", "⏱️ Performance Metrics", "🎯 Lead Distribution", "📋 Audit Log"])
    
    with tab1:
        # Conversion Funnel
        st.markdown("### 📊 Lead Conversion Funnel")
        
        funnel_data = pd.DataFrame({
            'Stage': ['IVR Calls', 'Telecaller Qualified', 'Sales Contacted', 'Deals Closed'],
            'Count': [len(df), len(df)*0.8, len(df)*0.5, len(df[df['Sales_Outcome']=='Closed'])]
        })
        
        fig = go.Figure(go.Funnel(
            y = funnel_data['Stage'],
            x = funnel_data['Count'],
            textinfo = "value+percent initial"
        ))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Performance Metrics
        st.markdown("### ⏱️ Team Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average response time
            fig = px.bar(
                df.groupby('Lead_Tag')['Wait_Time'].mean().reset_index(),
                x='Lead_Tag',
                y='Wait_Time',
                title='Average Wait Time by Lead Category',
                labels={'Wait_Time': 'Wait Time (min)', 'Lead_Tag': 'Lead Category'},
                color='Lead_Tag',
                color_discrete_map={'Hot': '#ff6b6b', 'Warm': '#ffd93d', 'Cold': '#a8dadc'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sales velocity
            outcome_counts = df['Sales_Outcome'].value_counts()
            fig = px.pie(
                values=outcome_counts.values,
                names=outcome_counts.index,
                title='Sales Outcomes Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Lead Distribution
        st.markdown("### 🎯 Lead Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # By State
            state_dist = df.groupby('State').size().reset_index(name='Count')
            fig = px.bar(state_dist, x='State', y='Count', title='Leads by State')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # By Machine Type
            machine_dist = df.groupby('Machine_Type').size().reset_index(name='Count')
            fig = px.bar(machine_dist, x='Machine_Type', y='Count', title='Leads by Machine Type')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Audit Log
        st.markdown("### 📋 Audit Log - Recent Activities")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_tag = st.multiselect("Lead Category", ['Hot', 'Warm', 'Cold'], default=['Hot', 'Warm', 'Cold'])
        with col2:
            filter_outcome = st.multiselect("Outcome", df['Sales_Outcome'].unique())
        with col3:
            filter_assigned = st.multiselect("Assigned To", df['Assigned_To'].unique())
        
        # Apply filters
        filtered_df = df.copy()
        if filter_tag:
            filtered_df = filtered_df[filtered_df['Lead_Tag'].isin(filter_tag)]
        if filter_outcome:
            filtered_df = filtered_df[filtered_df['Sales_Outcome'].isin(filter_outcome)]
        if filter_assigned:
            filtered_df = filtered_df[filtered_df['Assigned_To'].isin(filter_assigned)]
        
        # Display table
        st.dataframe(
            filtered_df[['Lead_ID', 'Customer_Name', 'Phone', 'State', 'Machine_Type', 
                        'Lead_Tag', 'Sales_Outcome', 'Assigned_To', 'Created_At']].sort_values('Created_At', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Audit Log",
            data=csv,
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Main App Logic
def main():
    """Main application logic"""
    
    # Sidebar
    with st.sidebar:
        if st.session_state.logged_in:
            st.markdown(f"### 👤 {st.session_state.user_name}")
            st.markdown(f"**Role:** {st.session_state.user_role}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.user_name = None
                st.rerun()
            
            st.markdown("---")
            st.markdown("### ℹ️ About")
            st.info("""
            **RK Lead Management System**
            
            🎯 **3-in-1 Dashboard**
            - Telecaller: Lead qualification
            - Sales: Priority-driven queue
            - Supervisor: Analytics & monitoring
            
            💡 Demo mode with sample data
            """)
        else:
            st.markdown("### 🏢 RK CRM")
            st.info("Please login to access the dashboard")
    
    # Show appropriate dashboard
    if not st.session_state.logged_in:
        show_login()
    else:
        if st.session_state.user_role == "Telecaller":
            show_telecaller_dashboard()
        elif st.session_state.user_role == "Sales Team":
            show_sales_dashboard()
        else:
            show_supervisor_dashboard()

if __name__ == "__main__":
    main()
