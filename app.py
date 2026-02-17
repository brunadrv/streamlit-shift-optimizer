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
    .metric-large {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-change {
        font-size: 1rem;
        font-weight: bold;
    }
    .metric-change-up {
        color: #2ca02c;
    }
    .metric-change-down {
        color: #d62728;
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
    .toggle-button {
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 0.5rem;
        margin: 0.25rem;
        cursor: pointer;
    }
    .toggle-button-active {
        background-color: #2ca02c;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = True
    # Initialize view toggle
    st.session_state.current_view = "Weekly Shift Summary"
    
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
    
    # Weekly shift summary data - restructured per user requirements
    st.session_state.weekly_shift_data = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Needed': 35, 'Expected': 28, 'Gap': -7, 'vs Previous Week': '-2%'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Needed': 30, 'Expected': 26, 'Gap': -4, 'vs Previous Week': '+1%'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Needed': 22, 'Expected': 18, 'Gap': -4, 'vs Previous Week': '-3%'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/1st', 'Needed': 38, 'Expected': 30, 'Gap': -8, 'vs Previous Week': '+2%'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/2nd', 'Needed': 28, 'Expected': 24, 'Gap': -4, 'vs Previous Week': '0%'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/3rd', 'Needed': 25, 'Expected': 20, 'Gap': -5, 'vs Previous Week': '-1%'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/1st', 'Needed': 40, 'Expected': 32, 'Gap': -8, 'vs Previous Week': '+3%'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/2nd', 'Needed': 32, 'Expected': 28, 'Gap': -4, 'vs Previous Week': '+1%'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/3rd', 'Needed': 28, 'Expected': 22, 'Gap': -6, 'vs Previous Week': '-2%'},
        {'Week': '2026-W08', 'Day/Shift': 'Thursday/1st', 'Needed': 36, 'Expected': 29, 'Gap': -7, 'vs Previous Week': '+1%'},
        {'Week': '2026-W08', 'Day/Shift': 'Thursday/2nd', 'Needed': 30, 'Expected': 25, 'Gap': -5, 'vs Previous Week': '+2%'},
        {'Week': '2026-W08', 'Day/Shift': 'Thursday/3rd', 'Needed': 24, 'Expected': 19, 'Gap': -5, 'vs Previous Week': '0%'},
        {'Week': '2026-W08', 'Day/Shift': 'Friday/1st', 'Needed': 42, 'Expected': 35, 'Gap': -7, 'vs Previous Week': '+4%'},
        {'Week': '2026-W08', 'Day/Shift': 'Friday/2nd', 'Needed': 35, 'Expected': 30, 'Gap': -5, 'vs Previous Week': '+3%'},
        {'Week': '2026-W08', 'Day/Shift': 'Friday/3rd', 'Needed': 30, 'Expected': 25, 'Gap': -5, 'vs Previous Week': '+1%'},
    ]
    
    # Weekly Expected HC Details - restructured per user requirements
    st.session_state.weekly_hc_details = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'FTE': 25, 'FTE vs Previous Week': '+2', 'TEMP': 3, 'Temp vs Previous Week': '+1', 'NEW HIRES': 2, 'NEW HIRES vs Previous Week': '+2', 'FLEX': 5, 'FLEX vs Previous Week': '-1', 'WW/GS': 'WW'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'FTE': 22, 'FTE vs Previous Week': '+1', 'TEMP': 4, 'Temp vs Previous Week': '0', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 3, 'FLEX vs Previous Week': '+1', 'WW/GS': 'GS'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'FTE': 15, 'FTE vs Previous Week': '-1', 'TEMP': 2, 'Temp vs Previous Week': '+1', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 2, 'FLEX vs Previous Week': '0', 'WW/GS': 'WW'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/1st', 'FTE': 27, 'FTE vs Previous Week': '+3', 'TEMP': 3, 'Temp vs Previous Week': '0', 'NEW HIRES': 2, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 4, 'FLEX vs Previous Week': '+1', 'WW/GS': 'GS'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/2nd', 'FTE': 20, 'FTE vs Previous Week': '+2', 'TEMP': 4, 'Temp vs Previous Week': '+1', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '0', 'FLEX': 3, 'FLEX vs Previous Week': '-1', 'WW/GS': 'WW'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/3rd', 'FTE': 18, 'FTE vs Previous Week': '0', 'TEMP': 2, 'Temp vs Previous Week': '+1', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '0', 'FLEX': 1, 'FLEX vs Previous Week': '0', 'WW/GS': 'GS'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/1st', 'FTE': 28, 'FTE vs Previous Week': '+4', 'TEMP': 4, 'Temp vs Previous Week': '+1', 'NEW HIRES': 3, 'NEW HIRES vs Previous Week': '+2', 'FLEX': 6, 'FLEX vs Previous Week': '+2', 'WW/GS': 'WW'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/2nd', 'FTE': 24, 'FTE vs Previous Week': '+2', 'TEMP': 4, 'Temp vs Previous Week': '+1', 'NEW HIRES': 2, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 4, 'FLEX vs Previous Week': '0', 'WW/GS': 'GS'},
    ]
    
    # Employee details data
    st.session_state.employee_data = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP001', 'Employee Name': 'John Smith', 'Hire Date': '2023-01-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP002', 'Employee Name': 'Mary Davis', 'Hire Date': '2022-08-20', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP101', 'Employee Name': 'Mike Wilson', 'Hire Date': '2026-02-01', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Variable'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP005', 'Employee Name': 'Carlos Rodriguez', 'Hire Date': '2023-11-08', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'EMP003', 'Employee Name': 'Lisa Brown', 'Hire Date': '2021-12-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'NEW HIRES', 'Employee ID': 'NEW001', 'Employee Name': 'David Garcia', 'Hire Date': '2026-02-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Training'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'TEMP', 'Employee ID': 'TMP102', 'Employee Name': 'Amanda Taylor', 'Hire Date': '2026-01-28', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Variable'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'EMP004', 'Employee Name': 'Jennifer Lee', 'Hire Date': '2023-06-05', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FLEX', 'Employee ID': 'FLX201', 'Employee Name': 'Robert Martinez', 'Hire Date': '2024-03-12', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Flexible'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'EMP006', 'Employee Name': 'Patricia White', 'Hire Date': '2022-05-18', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
    ]

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

def create_weekly_shift_summary_table():
    """Create weekly shift summary table with new structure"""
    df = pd.DataFrame(st.session_state.weekly_shift_data)
    return df

def create_weekly_hc_details_table():
    """Create weekly HC details table with new structure"""
    df = pd.DataFrame(st.session_state.weekly_hc_details)
    return df

def create_employee_details_table(selected_dept):
    """Create employee details table for selected department"""
    # Filter employees by department
    filtered_data = [emp for emp in st.session_state.employee_data if emp['Department'] == selected_dept]
    df = pd.DataFrame(filtered_data)
    return df

def main():
    # Header section - matching mockup layout
    st.markdown('<h1 class="main-header">Labor Planning Shift Optimizer</h1>', unsafe_allow_html=True)
    
    # Location, Week, Shift filters - now user selectable
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown("**Location**")
        location = st.selectbox("", ["AZ Goodyear", "TX Houston", "CA Los Angeles", "FL Tampa", "NY Buffalo"], 
                               index=0, label_visibility="collapsed")
    
    with col2:
        st.markdown("**Week**")
        week = st.selectbox("", ["2026-W08", "2026-W07", "2026-W09", "2026-W06", "2026-W10"], 
                           index=0, label_visibility="collapsed")
    
    with col3:
        st.markdown("**Shift**")
        shifts = st.multiselect("", ["1st", "2nd", "3rd"], 
                               default=["1st", "2nd", "3rd"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # Key metrics row - reordered: Needed HC, Expected HC, Gap in HC
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-label">Needed HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">100</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change metric-change-up">↗️ 5% vs last week</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Target HC to fulfill orders</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Expected HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">80</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change metric-change-up">↗️ 25% vs last week</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Scheduled * Historical Attendance Rate</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-label">Gap in HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="gap-negative">20</div>', unsafe_allow_html=True)
        st.markdown('<div class="gap-status">↘️ Understaffed by 20%</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Expected - Needed</div>', unsafe_allow_html=True)
        
        # Warning alert - only under Gap in HC
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
    
    # Weekly Overview with toggle buttons
    st.markdown('<div class="section-header">Weekly Overview</div>', unsafe_allow_html=True)
    
    # Toggle buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Weekly Shift Summary", use_container_width=True):
            st.session_state.current_view = "Weekly Shift Summary"
    
    with col2:
        if st.button("👥 Weekly Expected HC Details", use_container_width=True):
            st.session_state.current_view = "Weekly Expected HC Details"
    
    # Display selected view
    if st.session_state.current_view == "Weekly Shift Summary":
        st.markdown("### Weekly Shift Summary")
        weekly_shift_df = create_weekly_shift_summary_table()
        st.dataframe(weekly_shift_df, use_container_width=True, hide_index=True)
    
    else:  # Weekly Expected HC Details
        st.markdown("### Weekly Expected HC Details")
        weekly_hc_df = create_weekly_hc_details_table()
        st.dataframe(weekly_hc_df, use_container_width=True, hide_index=True)
    
    # Department detail section with employee table
    st.markdown("---")
    st.markdown('<div class="section-header">Department Details</div>', unsafe_allow_html=True)
    
    selected_dept = st.selectbox("Department", list(st.session_state.departments.keys()), index=0)  # Kitchen is first
    
    # Show gap analysis
    gap = st.session_state.departments[selected_dept]
    if gap < 0:
        st.error(f"⚠️ {selected_dept} is understaffed by {abs(gap)} people")
    elif gap > 0:
        st.success(f"✅ {selected_dept} has {gap} extra people")
    else:
        st.info(f"✅ {selected_dept} staffing is balanced")
    
    # Employee details table
    st.markdown(f"### {selected_dept} Employee List")
    employee_df = create_employee_details_table(selected_dept)
    
    if not employee_df.empty:
        st.dataframe(employee_df, use_container_width=True, hide_index=True)
    else:
        st.info("No employee data available for this department.")
    
    # Footer - matching mockup pagination
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div style="text-align: center; color: #666;">-- 1 of 1 --</div>', unsafe_allow_html=True)
    
    st.markdown("**Labor Planning Shift Optimizer** | Data as of " + datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    main()