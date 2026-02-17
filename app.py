import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Labor Planning Shift Optimizer",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E4057;
        text-align: left;
        margin-bottom: 1rem;
    }
    .location-info {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .week-info {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .shift-info {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-large {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-change {
        font-size: 1rem;
        color: #2ca02c;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .gap-negative {
        color: #d62728;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .gap-status {
        color: #d62728;
        font-size: 1rem;
        font-weight: bold;
    }
    .department-table {
        margin: 1rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E4057;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #ddd;
        padding-bottom: 0.5rem;
    }
    .department-detail {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = True
    # Sample data based on the mockup - exact values from PDF
    st.session_state.departments = {
        'Kitchen': -7,
        'Production': 7,
        'Sanitation': 10,
        'Quality': 0,
        'Warehouse': -2,
        'Fulfillment': 0,
        'Shipping': 5
    }
    
    # Weekly shift summary data
    st.session_state.weekly_shift_data = [
        {'Day': 'Monday', 'Date': '2026-02-17', '1st': 28, '2nd': 26, '3rd': 18, 'Total': 72},
        {'Day': 'Tuesday', 'Date': '2026-02-18', '1st': 30, '2nd': 24, '3rd': 20, 'Total': 74},
        {'Day': 'Wednesday', 'Date': '2026-02-19', '1st': 32, '2nd': 28, '3rd': 22, 'Total': 82},
        {'Day': 'Thursday', 'Date': '2026-02-20', '1st': 29, '2nd': 25, '3rd': 19, 'Total': 73},
        {'Day': 'Friday', 'Date': '2026-02-21', '1st': 35, '2nd': 30, '3rd': 25, 'Total': 90},
        {'Day': 'Saturday', 'Date': '2026-02-22', '1st': 25, '2nd': 20, '3rd': 15, 'Total': 60},
        {'Day': 'Sunday', 'Date': '2026-02-23', '1st': 20, '2nd': 18, '3rd': 12, 'Total': 50},
    ]
    
    # Weekly Expected HC Details by Department
    st.session_state.dept_weekly_details = {
        'Kitchen': [12, 13, 14, 12, 16, 10, 8],
        'Production': [35, 36, 38, 34, 42, 28, 22],
        'Sanitation': [8, 9, 10, 8, 12, 6, 5],
        'Quality': [6, 6, 7, 6, 8, 5, 4],
        'Warehouse': [15, 16, 18, 15, 20, 12, 9],
        'Fulfillment': [18, 19, 20, 18, 22, 15, 12],
        'Shipping': [12, 13, 15, 13, 18, 10, 8]
    }

def create_department_gap_table():
    """Create department gap table matching the mockup"""
    departments = ['Department'] + list(st.session_state.departments.keys())
    gaps = ['Gap in HC'] + [str(gap) for gap in st.session_state.departments.values()]
    
    # Create DataFrame for better formatting
    df = pd.DataFrame({
        'Metric': ['Department', 'Gap in HC'],
        'Kitchen': ['Kitchen', -7],
        'Production': ['Production', 7],
        'Sanitation': ['Sanitation', 10],
        'Quality': ['Quality', 0],
        'Warehouse': ['Warehouse', -2],
        'Fulfillment': ['Fulfillment', 0],
        'Shipping': ['Shipping', 5]
    })
    
    return df

def create_weekly_shift_summary_table():
    """Create weekly shift summary table"""
    df = pd.DataFrame(st.session_state.weekly_shift_data)
    return df

def create_weekly_hc_details_table():
    """Create weekly HC details by department"""
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dept_data = []
    
    for dept, values in st.session_state.dept_weekly_details.items():
        row = {'Department': dept}
        for i, day in enumerate(days):
            row[day] = values[i]
        row['Total'] = sum(values)
        dept_data.append(row)
    
    return pd.DataFrame(dept_data)

def calculate_metrics():
    """Calculate key metrics for the dashboard"""
    expected_hc = 80
    needed_hc = 100
    gap = expected_hc - needed_hc
    gap_percentage = (gap / needed_hc) * 100
    
    return {
        'expected_hc': expected_hc,
        'needed_hc': needed_hc,
        'gap': gap,
        'gap_percentage': gap_percentage
    }

def create_department_chart():
    """Create department gap chart"""
    departments = list(st.session_state.departments.keys())
    gaps = list(st.session_state.departments.values())
    colors = ['red' if gap < 0 else 'green' if gap > 0 else 'gray' for gap in gaps]
    
    fig = go.Figure(data=[
        go.Bar(
            x=departments,
            y=gaps,
            marker_color=colors,
            text=[f"{gap:+d}" for gap in gaps],
            textposition="outside"
        )
    ])
    
    fig.update_layout(
        title="Gap in HC by Department",
        xaxis_title="Department",
        yaxis_title="Gap in HC",
        showlegend=False,
        height=400
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    return fig

def create_weekly_overview_chart():
    """Create weekly overview chart"""
    df = load_sample_data()
    
    fig = px.line(df, x='Date', y='Expected_HC', 
                  title='Weekly Expected HC Trend',
                  markers=True)
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Expected HC",
        height=300
    )
    
    return fig

def main():
    # Header section - matching mockup layout
    st.markdown('<h1 class="main-header">Labor Planning Shift Optimizer</h1>', unsafe_allow_html=True)
    
    # Location, Week, Shift info - exactly as in mockup
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown('<div class="location-info"><strong>Location</strong><br>AZ Goodyear</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="week-info"><strong>Week</strong><br>2026-W08</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="shift-info"><strong>Shift</strong><br>1st, 2nd, 3rd</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key metrics row - matching mockup exactly
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-label">Expected HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">80</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">25% vs last week</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Scheduled * Historical Attendance Rate</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Needed HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">100</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">5% vs last week</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Target HC to fulfill orders</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-label">Gap in HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="gap-negative">20</div>', unsafe_allow_html=True)
        st.markdown('<div class="gap-status">Understaffed by 20%</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Expected - Needed</div>', unsafe_allow_html=True)
    
    # Warning alert - matching the "!" in mockup
    st.markdown("""
    <div class="alert-warning">
        ⚠️ <strong>Alert:</strong> Critical staffing shortage detected. Immediate action required.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Department gap table - exactly as shown in mockup
    st.markdown('<div class="section-header">Department Gap Analysis</div>', unsafe_allow_html=True)
    
    # Create the department table exactly like in mockup
    dept_cols = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1])
    
    headers = ['Department', 'Kitchen', 'Production', 'Sanitation', 'Quality', 'Warehouse', 'Fulfillment', 'Shipping']
    gaps = ['Gap in HC', '-7', '7', '10', '0', '-2', '0', '5']
    
    # Header row
    for i, (col, header) in enumerate(zip(dept_cols, headers)):
        with col:
            st.markdown(f'<div style="font-weight: bold; padding: 0.5rem; background-color: #f1f1f1; text-align: center; border: 1px solid #ddd;">{header}</div>', unsafe_allow_html=True)
    
    # Data row
    for i, (col, gap) in enumerate(zip(dept_cols, gaps)):
        with col:
            if i == 0:  # First column is label
                st.markdown(f'<div style="font-weight: bold; padding: 0.5rem; background-color: #f9f9f9; text-align: center; border: 1px solid #ddd;">{gap}</div>', unsafe_allow_html=True)
            else:
                # Color code the gaps
                color = "#d62728" if gap.startswith('-') else "#2ca02c" if gap != '0' else "#666"
                st.markdown(f'<div style="padding: 0.5rem; background-color: #f9f9f9; text-align: center; border: 1px solid #ddd; color: {color}; font-weight: bold;">{gap}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Two-column section for Weekly Shift Summary and Weekly Expected HC Details
    st.markdown('<div class="section-header">Weekly Overview</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Weekly Shift Summary")
        weekly_shift_df = create_weekly_shift_summary_table()
        st.dataframe(weekly_shift_df, use_container_width=True, hide_index=True)
        
        # Chart for weekly shift summary
        fig_shifts = go.Figure()
        fig_shifts.add_trace(go.Bar(name='1st Shift', x=weekly_shift_df['Day'], y=weekly_shift_df['1st'], marker_color='#1f77b4'))
        fig_shifts.add_trace(go.Bar(name='2nd Shift', x=weekly_shift_df['Day'], y=weekly_shift_df['2nd'], marker_color='#ff7f0e'))
        fig_shifts.add_trace(go.Bar(name='3rd Shift', x=weekly_shift_df['Day'], y=weekly_shift_df['3rd'], marker_color='#2ca02c'))
        
        fig_shifts.update_layout(
            barmode='stack',
            title='Weekly Shift Distribution',
            xaxis_title='Day',
            yaxis_title='Head Count',
            height=400
        )
        st.plotly_chart(fig_shifts, use_container_width=True)
    
    with col2:
        st.markdown("### Weekly Expected HC Details")
        weekly_hc_df = create_weekly_hc_details_table()
        st.dataframe(weekly_hc_df, use_container_width=True, hide_index=True)
        
        # Chart for department trends
        fig_dept_trend = go.Figure()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        for i, (dept, values) in enumerate(st.session_state.dept_weekly_details.items()):
            fig_dept_trend.add_trace(go.Scatter(
                x=days, y=values, mode='lines+markers', 
                name=dept, line_color=colors[i % len(colors)]
            ))
        
        fig_dept_trend.update_layout(
            title='Department HC Trends',
            xaxis_title='Day',
            yaxis_title='Expected HC',
            height=400
        )
        st.plotly_chart(fig_dept_trend, use_container_width=True)
    
    # Department detail section - showing "Kitchen" as selected in mockup
    st.markdown("---")
    st.markdown('<div class="section-header">Department Details</div>', unsafe_allow_html=True)
    
    selected_dept = st.selectbox("Department", list(st.session_state.departments.keys()), index=0)  # Kitchen is first
    
    st.markdown(f'<div class="department-detail">', unsafe_allow_html=True)
    st.markdown(f"### {selected_dept} Department Analysis")
    
    gap = st.session_state.departments[selected_dept]
    if gap < 0:
        st.error(f"⚠️ {selected_dept} is understaffed by {abs(gap)} people")
        st.markdown("**Recommended Actions:**")
        st.markdown("- Consider overtime for existing staff")
        st.markdown("- Transfer staff from overstaffed departments")
        st.markdown("- Schedule temporary workers")
    elif gap > 0:
        st.success(f"✅ {selected_dept} has {gap} extra people")
        st.markdown("**Optimization Opportunities:**")
        st.markdown("- Consider transferring staff to understaffed departments")
        st.markdown("- Reduce overtime costs")
        st.markdown("- Plan for additional production capacity")
    else:
        st.info(f"✅ {selected_dept} staffing is balanced")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer - matching mockup pagination
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div style="text-align: center; color: #666;">-- 1 of 1 --</div>', unsafe_allow_html=True)
    
    st.markdown("**Labor Planning Shift Optimizer** | Data as of " + datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    main()