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
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E4057;
        text-align: left;
        margin-bottom: 1rem;
    }
    .location-info {
        font-size: 1rem;
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
    .metric-change-up {
        font-size: 1rem;
        color: #2ca02c;
        font-weight: bold;
    }
    .metric-change-down {
        font-size: 1rem;
        color: #d62728;
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
    .gap-positive {
        color: #28a745;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .gap-neutral {
        color: #666;
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
        font-size: 1.7rem;
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
    .combined-table {
        width: 100%; 
        border-collapse: collapse; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 12px;
        margin: 10px 0;
    }
    .combined-table th {
        background-color: #f1f1f1; 
        color: #2E4057; 
        font-weight: bold; 
        padding: 8px; 
        text-align: center; 
        border: 1px solid #ddd;
        font-size: 11px;
    }
    .combined-table td {
        padding: 6px 8px; 
        text-align: center; 
        border: 1px solid #ddd; 
        position: relative;
        cursor: help;
    }
    .combined-table td.row-header {
        background-color: #f9f9f9; 
        font-weight: bold;
        text-align: left;
        cursor: default;
    }
    .combined-table td.data-cell:hover {
        background-color: #e8f5e8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = True
    
    # Sample data based on the mockup
    st.session_state.departments = {
        'Kitchen': -7,
        'Production': 7,
        'Sanitation': 10,
        'Quality': 0,
        'Warehouse': -2,
        'Fulfillment': 0,
        'Shipping': 5
    }
    
    # Employee data
    st.session_state.employee_data = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP001', 'Employee Name': 'John Smith', 'Hire Date': '2023-01-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP002', 'Employee Name': 'Mary Davis', 'Hire Date': '2022-08-20', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP101', 'Employee Name': 'Mike Wilson', 'Hire Date': '2026-02-01', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
    ]

def create_combined_headcount_attendance_table():
    """Create simplified combined table"""
    
    html_content = """
    <table class='combined-table'>
        <thead>
            <tr>
                <th>Employee Type</th>
                <th colspan='2'>2026-02-12 Thu Shift 1</th>
                <th colspan='2'>2026-02-12 Thu Shift 2</th>
                <th colspan='2'>2026-02-12 Thu Shift 3</th>
            </tr>
            <tr>
                <th></th>
                <th>Scheduled Headcount</th>
                <th>Attendance Assumption</th>
                <th>Scheduled Headcount</th>
                <th>Attendance Assumption</th>
                <th>Scheduled Headcount</th>
                <th>Attendance Assumption</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class='row-header'>FTE</td>
                <td class='data-cell'>48</td>
                <td class='data-cell'>90%</td>
                <td class='data-cell'>58</td>
                <td class='data-cell'>90%</td>
                <td class='data-cell'>12</td>
                <td class='data-cell'>83%</td>
            </tr>
            <tr>
                <td class='row-header'>TEMP</td>
                <td class='data-cell'>30</td>
                <td class='data-cell'>84%</td>
                <td class='data-cell'>15</td>
                <td class='data-cell'>83%</td>
                <td class='data-cell'>7</td>
                <td class='data-cell'>81%</td>
            </tr>
            <tr>
                <td class='row-header'>NEW HIRES</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
            </tr>
            <tr>
                <td class='row-header'>Day Labor (Flex)</td>
                <td class='data-cell'>1</td>
                <td class='data-cell'>50%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
            </tr>
            <tr>
                <td class='row-header'>Day Labor (WW/GS)</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>100%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>100%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>100%</td>
            </tr>
            <tr>
                <td class='row-header'>Overtime (VEH/MEH)</td>
                <td class='data-cell'>2</td>
                <td class='data-cell'>80%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>80%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>80%</td>
            </tr>
            <tr>
                <td class='row-header'>Time Off (VER/MTO)</td>
                <td class='data-cell'>1</td>
                <td class='data-cell'>50%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
                <td class='data-cell'>0</td>
                <td class='data-cell'>50%</td>
            </tr>
        </tbody>
    </table>
    """
    
    return html_content

def main():
    # Header section
    st.markdown('<h1 class="main-header">Labor Planning Shift Optimizer</h1>', unsafe_allow_html=True)
    
    # All filters at the top
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1.5])
    
    with col1:
        st.markdown("**Location**")
        location = st.selectbox("", ["AZ Goodyear", "IL Aurora", "AZ Phoenix", "IL Lake Zurich", "IL Burr Ridge"], 
                               index=0, label_visibility="collapsed")
    
    with col2:
        st.markdown("**Department**")
        selected_department = st.selectbox("", list(st.session_state.departments.keys()), 
                                         index=0, label_visibility="collapsed")
    
    with col3:
        st.markdown("**Week**")
        # Order weeks chronologically
        week = st.selectbox("", ["2026-W06", "2026-W07", "2026-W08", "2026-W09", "2026-W10"], 
                           index=2, label_visibility="collapsed")  # Default to W08
    
    with col4:
        st.markdown("**Date**")
        # Generate date range for the selected production week (Thursday-Wednesday)
        def get_production_week_range(week_str):
            """Get start (Thursday) and end (Wednesday) dates for production week"""
            week_mappings = {
                "2026-W06": datetime(2026, 1, 30),  # Thursday Jan 30 - Wednesday Feb 5
                "2026-W07": datetime(2026, 2, 6),   # Thursday Feb 6 - Wednesday Feb 12
                "2026-W08": datetime(2026, 2, 13),  # Thursday Feb 13 - Wednesday Feb 19
                "2026-W09": datetime(2026, 2, 20),  # Thursday Feb 20 - Wednesday Feb 26
                "2026-W10": datetime(2026, 2, 27)   # Thursday Feb 27 - Wednesday Mar 5
            }
            thursday = week_mappings.get(week_str, datetime(2026, 2, 13))
            wednesday = thursday + timedelta(days=6)
            return thursday, wednesday
        
        # Get the production week range
        week_start, week_end = get_production_week_range(week)
        
        # Use date_input for calendar-like date range selection
        selected_date_range = st.date_input(
            "",
            value=(week_start, week_end),  # Default to full production week
            min_value=week_start,
            max_value=week_end,
            format="MM/DD/YYYY",
            label_visibility="collapsed",
            help=f"Select date range within production week {week} (Thu-Wed)"
        )
        
        # Convert to list of dates for compatibility with rest of app
        if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
            selected_dates = []
            current_date = start_date
            while current_date <= end_date:
                selected_dates.append(current_date)
                current_date += timedelta(days=1)
        elif isinstance(selected_date_range, datetime):
            # Single date selected
            selected_dates = [selected_date_range]
        else:
            # Fallback to full week
            selected_dates = [week_start + timedelta(days=i) for i in range(7)] 
    
    with col5:
        st.markdown("**Shift**")
        shifts = st.multiselect("", ["1st", "2nd", "3rd"], 
                               default=["1st", "2nd", "3rd"], label_visibility="collapsed") 
    
    # CHANGE 1 & 4: Overview Section with 4 pills including Total Punches + Shift Breakdown
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    
    # Key metrics row - All four KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-label">Needed HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">100</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📊 5% vs last week</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Expected HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">69</div>', unsafe_allow_html=True)
        
        # CHANGE 1: Add shift breakdown under Expected HC
        st.markdown("""
        <div style="background-color: #f8f9fa; border-radius: 6px; padding: 8px; margin-top: 8px;">
            <div style="margin-bottom: 4px; font-size: 0.75rem; color: #666;">Thu</div>
            <div style="margin-bottom: 6px;">
                <span style="background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 12px; font-size: 0.7rem; margin: 0 2px; display: inline-block; min-width: 20px; text-align: center; font-weight: 500;">S1<br>26</span>
                <span style="background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 12px; font-size: 0.7rem; margin: 0 2px; display: inline-block; min-width: 20px; text-align: center; font-weight: 500;">S2<br>25</span>
                <span style="background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 12px; font-size: 0.7rem; margin: 0 2px; display: inline-block; min-width: 20px; text-align: center; font-weight: 500;">S3<br>18</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="metric-change">📈 20% vs last week</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-label">Gap in HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="gap-negative">31</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📉 3% vs last week</div>', unsafe_allow_html=True)

    with col4:
        # CHANGE 4: Add Total Punches pill
        st.markdown('<div class="metric-label">Total Punches</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">79</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📊 4% vs last week</div>', unsafe_allow_html=True)
    
    # CHANGE 3: Rename section header
    department_expected = 69
    st.markdown(f'<div class="section-header">{selected_department} Expected HC ({department_expected})</div>', unsafe_allow_html=True)
    
    # Legend
    st.markdown("""
    <div style="margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f8f9fa;">
        <strong>Legend:</strong>
        <span style="margin-left: 20px; padding: 4px 8px; background-color: #ffcccc; border-radius: 3px;">>20% variance from last week</span>
        <span style="margin-left: 10px; padding: 4px 8px; background-color: #fff3cd; border-radius: 3px;">10-20% variance from last week</span>
    </div>
    """, unsafe_allow_html=True)
    
    # CHANGE 5 & 6: Combined table (no more separate views)
    html_table = create_combined_headcount_attendance_table()
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Employee List section
    st.markdown(f'<div class="section-header">{selected_department} Employee List ({department_expected})</div>', unsafe_allow_html=True)
    
    # Employee data table
    df = pd.DataFrame(st.session_state.employee_data)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()