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
    # Initialize view toggle - updated to 4 views
    st.session_state.current_view = "Shift Summary"
    
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
    
    # Shift Summary data (same structure as before)
    st.session_state.shift_summary_data = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Needed': 35, 'Expected': 28, 'Gap': -7, 'vs Previous Week': '-2%'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Needed': 30, 'Expected': 26, 'Gap': -4, 'vs Previous Week': '+1%'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Needed': 22, 'Expected': 18, 'Gap': -4, 'vs Previous Week': '-3%'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/1st', 'Needed': 38, 'Expected': 30, 'Gap': -8, 'vs Previous Week': '+2%'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/2nd', 'Needed': 28, 'Expected': 24, 'Gap': -4, 'vs Previous Week': '0%'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/3rd', 'Needed': 25, 'Expected': 20, 'Gap': -5, 'vs Previous Week': '-1%'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/1st', 'Needed': 40, 'Expected': 32, 'Gap': -8, 'vs Previous Week': '+3%'},
        {'Week': '2026-W08', 'Day/Shift': 'Wednesday/2nd', 'Needed': 32, 'Expected': 28, 'Gap': -4, 'vs Previous Week': '+1%'},
    ]
    
    # Roster HC Summary data - new section from mockup
    st.session_state.roster_hc_summary = {
        'total_needed': 100,
        'vs_previous_week': '+5%',
        'departments': {
            'Kitchen': {'needed': 25, 'vs_previous': '-2'},
            'Production': {'needed': 20, 'vs_previous': '+3'},
            'Sanitation': {'needed': 15, 'vs_previous': '+1'},
            'Quality': {'needed': 12, 'vs_previous': '0'},
            'Warehouse': {'needed': 18, 'vs_previous': '+2'},
            'Fulfillment': {'needed': 10, 'vs_previous': '+1'}
        }
    }
    
    # Roster HC Details data - new section from mockup
    st.session_state.roster_hc_details = {
        'attendance_assumption': '92%',
        'vs_previous_week': '-6 workers',
        'breakdown': [
            {'Category': 'FTE', 'Count': 43, 'Attendance': '95%'},
            {'Category': 'TEMP', 'Count': 35, 'Attendance': '82%'},
            {'Category': 'WW', 'Count': 20, 'Attendance': '88%'},
            {'Category': 'FLEX', 'Count': 0, 'Attendance': 'N/A'}
        ]
    }
    
    # Attendance Assumption data - new section from mockup
    st.session_state.attendance_assumptions = {
        'vs_previous_week': '+20 vs Previous Week',
        'breakdown': [
            {'Type': 'FTE', 'Percentage': '95%', 'Count': 43},
            {'Type': 'TEMP', 'Percentage': '82%', 'Count': 35},
            {'Type': 'WW', 'Percentage': '88%', 'Count': 20},
            {'Type': 'FLEX', 'Percentage': '0%', 'Count': 0}
        ]
    }
    
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

def create_shift_summary_table():
    """Create shift summary table"""
    df = pd.DataFrame(st.session_state.shift_summary_data)
    return df

def create_roster_hc_summary_view(selected_dept=None):
    """Create roster HC summary view with department filtering"""
    if selected_dept and selected_dept != "All":
        # Show detailed view for selected department vs others
        dept_data = []
        for dept, data in st.session_state.roster_hc_summary['departments'].items():
            status = "Selected Dept" if dept == selected_dept else "Other Dept"
            dept_data.append({
                'Department': dept,
                'Status': status,
                'Needed HC': data['needed'],
                'vs Previous Week': data['vs_previous']
            })
        return pd.DataFrame(dept_data)
    else:
        # Show summary view
        summary_data = []
        for dept, data in st.session_state.roster_hc_summary['departments'].items():
            summary_data.append({
                'Department': dept,
                'Needed HC': data['needed'],
                'vs Previous Week': data['vs_previous']
            })
        return pd.DataFrame(summary_data)

def create_roster_hc_details_view():
    """Create roster HC details view"""
    df = pd.DataFrame(st.session_state.roster_hc_details['breakdown'])
    return df

def create_attendance_assumption_view():
    """Create attendance assumption view"""
    df = pd.DataFrame(st.session_state.attendance_assumptions['breakdown'])
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
    
    # All filters at the top - Location, Week, Shift, Department, Date
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 1])
    
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
    
    with col4:
        st.markdown("**Department**")
        selected_department = st.selectbox("", list(st.session_state.departments.keys()), 
                                         index=0, label_visibility="collapsed")  # Kitchen is first
    
    with col5:
        st.markdown("**Date**")
        selected_date = st.date_input("", value=pd.to_datetime("2026-02-12"), label_visibility="collapsed")
    
    st.markdown("---")
    
    # Weekly Overview section title - appears above KPIs
    st.markdown('<div class="section-header">Weekly Overview</div>', unsafe_allow_html=True)
    
    # Key metrics row - All three KPIs: Needed HC, Expected HC, Gap in HC
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
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Scheduled x Attendance Assumption</div>', unsafe_allow_html=True)
    
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
    
    # Department Gap Comparison - dynamic highlighting based on selected department
    st.markdown('<div class="section-header">Department Gap Comparison</div>', unsafe_allow_html=True)
    
    # Create the department table with dynamic highlighting
    dept_cols = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1])
    
    headers = ['Department', 'Kitchen', 'Production', 'Sanitation', 'Quality', 'Warehouse', 'Fulfillment', 'Shipping']
    gaps = ['Gap in HC', '-7', '7', '10', '0', '-2', '0', '5']
    
    # Header row
    for i, (col, header) in enumerate(zip(dept_cols, headers)):
        with col:
            # Highlight selected department
            bg_color = "#e3f2fd" if header == selected_department else "#f1f1f1"
            st.markdown(f'<div style="font-weight: bold; padding: 0.5rem; background-color: {bg_color}; text-align: center; border: 1px solid #ddd;">{header}</div>', unsafe_allow_html=True)
    
    # Data row
    for i, (col, gap) in enumerate(zip(dept_cols, gaps)):
        with col:
            if i == 0:  # First column is label
                st.markdown(f'<div style="font-weight: bold; padding: 0.5rem; background-color: #f9f9f9; text-align: center; border: 1px solid #ddd;">{gap}</div>', unsafe_allow_html=True)
            else:
                # Highlight selected department and color code the gaps
                dept_name = headers[i]
                bg_color = "#e3f2fd" if dept_name == selected_department else "#f9f9f9"
                color = "#d62728" if gap.startswith('-') else "#2ca02c" if gap != '0' else "#666"
                st.markdown(f'<div style="padding: 0.5rem; background-color: {bg_color}; text-align: center; border: 1px solid #ddd; color: {color}; font-weight: bold;">{gap}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Four toggle buttons in the order from mockup
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Shift Summary", use_container_width=True):
            st.session_state.current_view = "Shift Summary"
    
    with col2:
        if st.button("👥 Roster HC Summary", use_container_width=True):
            st.session_state.current_view = "Roster HC Summary"
    
    with col3:
        if st.button("📋 Roster HC Details", use_container_width=True):
            st.session_state.current_view = "Roster HC Details"
    
    with col4:
        if st.button("📈 Attendance Assumption", use_container_width=True):
            st.session_state.current_view = "Attendance Assumption"
    
    # Display selected view
    if st.session_state.current_view == "Shift Summary":
        st.markdown("### Shift Summary")
        shift_df = create_shift_summary_table()
        st.dataframe(shift_df, use_container_width=True, hide_index=True)
    
    elif st.session_state.current_view == "Roster HC Summary":
        st.markdown("### Roster HC Summary")
        
        # Department filter for showing selected vs others
        dept_filter = st.selectbox("Shows Filtered Dept vs Other Depts", ["All"] + list(st.session_state.departments.keys()))
        
        roster_summary_df = create_roster_hc_summary_view(dept_filter)
        st.dataframe(roster_summary_df, use_container_width=True, hide_index=True)
    
    elif st.session_state.current_view == "Roster HC Details":
        st.markdown("### Roster HC Details")
        
        # Show key metrics from mockup
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**● Att.Assumption: 92%**")
        with col2:
            st.markdown("**● Vs Prev. Week: -6 workers**")
        
        roster_details_df = create_roster_hc_details_view()
        st.dataframe(roster_details_df, use_container_width=True, hide_index=True)
    
    else:  # Attendance Assumption
        st.markdown("### Attendance Assumption")
        
        # Show key metric exactly as in mockup
        st.markdown(f'<div class="metric-change metric-change-up" style="font-size: 1.2rem;">+20 vs Previous Week</div>', unsafe_allow_html=True)
        
        # Show bullet points exactly as in mockup
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**● FTE: 95%**")
            st.markdown("**● TEMP: 82%**")
        with col2:
            st.markdown("**● FTE: 43**")
            st.markdown("**● TEMP: 35**")
            st.markdown("**● WW: 20**")
            st.markdown("**● FLEX: 0**")
    
    # Weekly Department Details section
    st.markdown("---")
    st.markdown('<div class="section-header">Weekly Department Details</div>', unsafe_allow_html=True)
    
    # Show gap analysis for selected department
    gap = st.session_state.departments[selected_department]
    if gap < 0:
        st.error(f"⚠️ {selected_department} is understaffed by {abs(gap)} people")
    elif gap > 0:
        st.success(f"✅ {selected_department} has {gap} extra people")
    else:
        st.info(f"✅ {selected_department} staffing is balanced")
    
    # Create detailed tables with tooltips for the selected department
    st.markdown(f"### {selected_department} Department Details")
    
    # Sample data for the selected department with tooltip information
    dept_detail_data = [
        {
            'Day/Shift': 'Monday/1st', 
            'Needed HC': '20',
            'Expected HC': '15',
            'Gap': '-5',
            'Attendance %': '85%',
            'vs_prev_needed': '+2 vs prev week',
            'vs_prev_expected': '+1 vs prev week',
            'vs_prev_gap': '-1 vs prev week',
            'vs_prev_attendance': '-2% vs prev week'
        },
        {
            'Day/Shift': 'Monday/2nd', 
            'Needed HC': '18',
            'Expected HC': '16',
            'Gap': '-2',
            'Attendance %': '88%',
            'vs_prev_needed': '+1 vs prev week',
            'vs_prev_expected': '0 vs prev week',
            'vs_prev_gap': '-1 vs prev week',
            'vs_prev_attendance': '+1% vs prev week'
        },
        {
            'Day/Shift': 'Monday/3rd', 
            'Needed HC': '12',
            'Expected HC': '10',
            'Gap': '-2',
            'Attendance %': '82%',
            'vs_prev_needed': '0 vs prev week',
            'vs_prev_expected': '-1 vs prev week',
            'vs_prev_gap': '-1 vs prev week',
            'vs_prev_attendance': '-3% vs prev week'
        },
        {
            'Day/Shift': 'Tuesday/1st', 
            'Needed HC': '22',
            'Expected HC': '18',
            'Gap': '-4',
            'Attendance %': '86%',
            'vs_prev_needed': '+3 vs prev week',
            'vs_prev_expected': '+2 vs prev week',
            'vs_prev_gap': '-1 vs prev week',
            'vs_prev_attendance': '+1% vs prev week'
        }
    ]
    
    # Create a more detailed display with tooltips (using help parameter)
    st.markdown("#### Detailed Schedule Breakdown")
    
    for row in dept_detail_data:
        with st.expander(f"📅 {row['Day/Shift']} - Gap: {row['Gap']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Needed HC",
                    value=row['Needed HC'],
                    help=row['vs_prev_needed']
                )
            
            with col2:
                st.metric(
                    label="Expected HC",
                    value=row['Expected HC'],
                    help=row['vs_prev_expected']
                )
            
            with col3:
                st.metric(
                    label="Gap",
                    value=row['Gap'],
                    help=row['vs_prev_gap']
                )
            
            with col4:
                st.metric(
                    label="Attendance %",
                    value=row['Attendance %'],
                    help=row['vs_prev_attendance']
                )
    
    # Also show as a regular dataframe
    display_df = pd.DataFrame([{
        'Day/Shift': row['Day/Shift'],
        'Needed HC': row['Needed HC'], 
        'Expected HC': row['Expected HC'],
        'Gap': row['Gap'],
        'Attendance %': row['Attendance %']
    } for row in dept_detail_data])
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Footer - matching mockup pagination
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div style="text-align: center; color: #666;">-- 1 of 1 --</div>', unsafe_allow_html=True)
    
    st.markdown("**Labor Planning Shift Optimizer** | Data as of " + datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    main()