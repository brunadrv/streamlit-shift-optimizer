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
    
    # Shift Summary: Transposed structure with Date, Week Day, Shift, Total Needed, Total Expected, Total Gap, Total Attendance Assumption, Total Punches as ROWS
    st.session_state.shift_summary_transposed = {
        '2026-02-12 Thu Shift 1': {
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 1',
            'Total Needed': 91,
            'Total Expected': 79,
            'Total Gap': -12,
            'Total Attendance Assumption': '89%',
            'Total Punches': 106,
            'tooltip_needed': '• FTE: 35\n• TEMP: 35\n• WW: 20\n• FLEX: 0',
            'tooltip_expected': 'Previous Week: 83\n• FTE: 14%',
            'tooltip_gap': 'Previous Week: -8\n• Improvement: -4',
            'tooltip_attendance': 'Previous Week: 91%\n• Change: -2%',
            'tooltip_punches': 'Previous Week: 98\n• Change: +8'
        },
        '2026-02-12 Thu Shift 2': {
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 2',
            'Total Needed': 86,
            'Total Expected': 73,
            'Total Gap': -13,
            'Total Attendance Assumption': '88%',
            'Total Punches': 88,
            'tooltip_needed': '• FTE: 28\n• TEMP: 30\n• WW: 15\n• FLEX: 13',
            'tooltip_expected': 'Previous Week: 76\n• FTE: 18%',
            'tooltip_gap': 'Previous Week: -10\n• Change: -3',
            'tooltip_attendance': 'Previous Week: 85%\n• Change: +3%',
            'tooltip_punches': 'Previous Week: 85\n• Change: +3'
        },
        '2026-02-12 Thu Shift 3': {
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 3',
            'Total Needed': 15,
            'Total Expected': 18,
            'Total Gap': 3,
            'Total Attendance Assumption': '0%',
            'Total Punches': 0,
            'tooltip_needed': '• FTE: 8\n• TEMP: 4\n• WW: 3\n• FLEX: 0',
            'tooltip_expected': 'Previous Week: 15\n• FTE: 20%',
            'tooltip_gap': 'Previous Week: 0\n• Change: +3',
            'tooltip_attendance': 'Previous Week: 0%\n• Change: 0%',
            'tooltip_punches': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-13 Fri Shift 1': {
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 1',
            'Total Needed': 79,
            'Total Expected': 83,
            'Total Gap': 4,
            'Total Attendance Assumption': '78%',
            'Total Punches': 91,
            'tooltip_needed': '• FTE: 40\n• TEMP: 25\n• WW: 12\n• FLEX: 2',
            'tooltip_expected': 'Previous Week: 80\n• FTE: 16%',
            'tooltip_gap': 'Previous Week: 1\n• Change: +3',
            'tooltip_attendance': 'Previous Week: 75%\n• Change: +3%',
            'tooltip_punches': 'Previous Week: 88\n• Change: +3'
        },
        '2026-02-13 Fri Shift 2': {
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 2',
            'Total Needed': 65,
            'Total Expected': 53,
            'Total Gap': -12,
            'Total Attendance Assumption': '85%',
            'Total Punches': 101,
            'tooltip_needed': '• FTE: 30\n• TEMP: 20\n• WW: 10\n• FLEX: 5',
            'tooltip_expected': 'Previous Week: 50\n• FTE: 22%',
            'tooltip_gap': 'Previous Week: -15\n• Change: +3',
            'tooltip_attendance': 'Previous Week: 82%\n• Change: +3%',
            'tooltip_punches': 'Previous Week: 95\n• Change: +6'
        },
        '2026-02-13 Fri Shift 3': {
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 3',
            'Total Needed': 13,
            'Total Expected': 17,
            'Total Gap': 4,
            'Total Attendance Assumption': '0%',
            'Total Punches': 0,
            'tooltip_needed': '• FTE: 10\n• TEMP: 3\n• WW: 0\n• FLEX: 0',
            'tooltip_expected': 'Previous Week: 15\n• FTE: 12%',
            'tooltip_gap': 'Previous Week: 2\n• Change: +2',
            'tooltip_attendance': 'Previous Week: 0%\n• Change: 0%',
            'tooltip_punches': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-14 Sat Shift 1': {
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 1',
            'Total Needed': 76,
            'Total Expected': 78,
            'Total Gap': 2,
            'Total Attendance Assumption': '76%',
            'Total Punches': 98,
            'tooltip_needed': '• FTE: 45\n• TEMP: 18\n• WW: 8\n• FLEX: 5',
            'tooltip_expected': 'Previous Week: 75\n• FTE: 20%',
            'tooltip_gap': 'Previous Week: -1\n• Change: +3',
            'tooltip_attendance': 'Previous Week: 74%\n• Change: +2%',
            'tooltip_punches': 'Previous Week: 95\n• Change: +3'
        },
        '2026-02-14 Sat Shift 2': {
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 2',
            'Total Needed': 55,
            'Total Expected': 79,
            'Total Gap': 24,
            'Total Attendance Assumption': '77%',
            'Total Punches': 73,
            'tooltip_needed': '• FTE: 35\n• TEMP: 15\n• WW: 5\n• FLEX: 0',
            'tooltip_expected': 'Previous Week: 60\n• FTE: 32%',
            'tooltip_gap': 'Previous Week: 5\n• Change: +19',
            'tooltip_attendance': 'Previous Week: 75%\n• Change: +2%',
            'tooltip_punches': 'Previous Week: 70\n• Change: +3'
        },
        '2026-02-14 Sat Shift 3': {
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 3',
            'Total Needed': 14,
            'Total Expected': 16,
            'Total Gap': 2,
            'Total Attendance Assumption': '0%',
            'Total Punches': 0,
            'tooltip_needed': '• FTE: 12\n• TEMP: 2\n• WW: 0\n• FLEX: 0',
            'tooltip_expected': 'Previous Week: 14\n• FTE: 14%',
            'tooltip_gap': 'Previous Week: 0\n• Change: +2',
            'tooltip_attendance': 'Previous Week: 0%\n• Change: 0%',
            'tooltip_punches': 'Previous Week: 0\n• Change: 0'
        }
    }
    
    # EXACT COLUMNS FROM YOUR ORIGINAL REQUEST:
    # Weekly Expected HC Details: Week, Day/Shift, FTE, FTE vs Previous Week, TEMP, Temp vs Previous Week, NEW HIRES, NEW HIRES vs Previous Week, FLEX, FLEX vs Previous Week, WW/GS
    st.session_state.weekly_hc_details = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'FTE': 25, 'FTE vs Previous Week': '+2', 'TEMP': 3, 'Temp vs Previous Week': '+1', 'NEW HIRES': 2, 'NEW HIRES vs Previous Week': '+2', 'FLEX': 5, 'FLEX vs Previous Week': '-1', 'WW/GS': 'WW'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'FTE': 22, 'FTE vs Previous Week': '+1', 'TEMP': 4, 'Temp vs Previous Week': '0', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 3, 'FLEX vs Previous Week': '+1', 'WW/GS': 'GS'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'FTE': 15, 'FTE vs Previous Week': '-1', 'TEMP': 2, 'Temp vs Previous Week': '+1', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 2, 'FLEX vs Previous Week': '0', 'WW/GS': 'WW'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/1st', 'FTE': 27, 'FTE vs Previous Week': '+3', 'TEMP': 3, 'Temp vs Previous Week': '0', 'NEW HIRES': 2, 'NEW HIRES vs Previous Week': '+1', 'FLEX': 4, 'FLEX vs Previous Week': '+1', 'WW/GS': 'GS'},
        {'Week': '2026-W08', 'Day/Shift': 'Tuesday/2nd', 'FTE': 20, 'FTE vs Previous Week': '+2', 'TEMP': 4, 'Temp vs Previous Week': '+1', 'NEW HIRES': 1, 'NEW HIRES vs Previous Week': '0', 'FLEX': 3, 'FLEX vs Previous Week': '-1', 'WW/GS': 'WW'},
    ]
    
    # Employee details data (existing structure)
    st.session_state.employee_data = [
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP001', 'Employee Name': 'John Smith', 'Hire Date': '2023-01-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP002', 'Employee Name': 'Mary Davis', 'Hire Date': '2022-08-20', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP101', 'Employee Name': 'Mike Wilson', 'Hire Date': '2026-02-01', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Variable'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'EMP003', 'Employee Name': 'Lisa Brown', 'Hire Date': '2021-12-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'NEW HIRES', 'Employee ID': 'NEW001', 'Employee Name': 'David Garcia', 'Hire Date': '2026-02-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Training'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'EMP004', 'Employee Name': 'Jennifer Lee', 'Hire Date': '2023-06-05', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Core'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FLEX', 'Employee ID': 'FLX201', 'Employee Name': 'Robert Martinez', 'Hire Date': '2024-03-12', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Flexible'},
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

def create_plotly_table_with_tooltips(df, hover_data=None):
    """Create a Plotly table with hover tooltips"""
    
    # Prepare header values
    headers = list(df.columns)
    
    # Prepare cell values
    values = []
    hover_texts = []
    
    for col in headers:
        values.append(df[col].tolist())
        
        # Create hover text for each cell
        if hover_data and col in hover_data:
            hover_texts.append([hover_data[col].get(i, '') for i in range(len(df))])
        else:
            hover_texts.append([''] * len(df))
    
    # Create the table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=headers,
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=12, color='#2E4057'),
            height=40
        ),
        cells=dict(
            values=values,
            fill_color='white',
            align='center',
            font=dict(size=11),
            height=35,
        )
    )])
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    return fig

def create_transposed_shift_summary_table_with_tooltips():
    """Create transposed shift summary table matching the screenshot structure"""
    
    # Prepare the transposed structure
    columns = list(st.session_state.shift_summary_transposed.keys())
    rows = ['Date', 'Week Day', 'Shift', 'Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']
    
    # Create the data structure for Plotly table
    header_values = [''] + columns  # Empty first cell, then column headers
    
    # Prepare data for each row
    table_data = []
    hover_data = {}
    
    for row_name in rows:
        row_data = [row_name]  # First cell is the row label
        hover_texts = ['']  # No hover for row labels
        
        for col in columns:
            value = st.session_state.shift_summary_transposed[col][row_name]
            row_data.append(str(value))
            
            # Add tooltip data based on the row type
            if row_name == 'Total Needed':
                hover_texts.append(st.session_state.shift_summary_transposed[col]['tooltip_needed'])
            elif row_name == 'Total Expected':
                hover_texts.append(st.session_state.shift_summary_transposed[col]['tooltip_expected'])
            elif row_name == 'Total Gap':
                hover_texts.append(st.session_state.shift_summary_transposed[col]['tooltip_gap'])
            elif row_name == 'Total Attendance Assumption':
                hover_texts.append(st.session_state.shift_summary_transposed[col]['tooltip_attendance'])
            elif row_name == 'Total Punches':
                hover_texts.append(st.session_state.shift_summary_transposed[col]['tooltip_punches'])
            else:
                hover_texts.append('')  # No tooltip for Date, Week Day, Shift
        
        table_data.append(row_data)
        hover_data[row_name] = hover_texts
    
    # Create color coding for cells
    fill_colors = []
    for i, row_name in enumerate([''] + rows):  # Include header row
        if i == 0:  # Header row
            fill_colors.append(['#f1f1f1'] * len(header_values))
        else:
            row_colors = ['#f9f9f9']  # Row label color
            for col in columns:
                if row_name == 'Total Gap':
                    gap_value = st.session_state.shift_summary_transposed[col]['Total Gap']
                    if gap_value < 0:
                        row_colors.append('#ffebee')  # Light red for negative gap
                    elif gap_value > 0:
                        row_colors.append('#e8f5e8')  # Light green for positive gap
                    else:
                        row_colors.append('white')
                else:
                    row_colors.append('white')
            fill_colors.append(row_colors)
    
    # Flatten the data for Plotly
    cell_values = []
    cell_colors = []
    
    # Transpose the data for Plotly (columns become rows)
    for col_idx in range(len(header_values)):
        col_data = []
        col_color = []
        for row_idx in range(len(table_data) + 1):  # +1 for header
            if row_idx == 0:  # Header
                col_data.append(header_values[col_idx])
                col_color.append('#f1f1f1')
            else:
                col_data.append(table_data[row_idx - 1][col_idx])
                col_color.append(fill_colors[row_idx][col_idx])
        cell_values.append(col_data)
        cell_colors.append(col_color)
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Row Labels'] + columns,
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=10, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=[['Date', 'Week Day', 'Shift', 'Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']] + 
                   [[st.session_state.shift_summary_transposed[col][row] for row in rows] for col in columns],
            fill_color=[['#f9f9f9'] * len(rows)] + 
                      [[get_cell_color(col, row, st.session_state.shift_summary_transposed[col][row]) for row in rows] for col in columns],
            align='center',
            font=dict(size=9),
            height=25,
        )
    )])
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        title="Shift Summary - Hover over values to see details"
    )
    
    return fig

def get_cell_color(col, row, value):
    """Get appropriate cell color based on value and type"""
    if row == 'Total Gap':
        if isinstance(value, (int, float)):
            if value < 0:
                return '#ffebee'  # Light red for negative gap
            elif value > 0:
                return '#e8f5e8'  # Light green for positive gap
    return 'white'

def create_weekly_hc_details_table_with_tooltips():
    """Create weekly HC details table with exact columns and tooltips"""
    # Create DataFrame with exact columns: Week, Day/Shift, FTE, FTE vs Previous Week, TEMP, Temp vs Previous Week, NEW HIRES, NEW HIRES vs Previous Week, FLEX, FLEX vs Previous Week, WW/GS
    display_data = []
    
    for row in st.session_state.weekly_hc_details:
        display_data.append({
            'Week': row['Week'],
            'Day/Shift': row['Day/Shift'],
            'FTE': row['FTE'],
            'FTE vs Previous Week': row['FTE vs Previous Week'],
            'TEMP': row['TEMP'],
            'Temp vs Previous Week': row['Temp vs Previous Week'],
            'NEW HIRES': row['NEW HIRES'],
            'NEW HIRES vs Previous Week': row['NEW HIRES vs Previous Week'],
            'FLEX': row['FLEX'],
            'FLEX vs Previous Week': row['FLEX vs Previous Week'],
            'WW/GS': row['WW/GS']
        })
    
    df = pd.DataFrame(display_data)
    return create_plotly_table_with_tooltips(df)

def create_employee_details_table_with_tooltips(selected_dept):
    """Create employee details table with exact columns and tooltips"""
    # Filter employees by department
    filtered_data = [emp for emp in st.session_state.employee_data if emp['Department'] == selected_dept]
    
    if not filtered_data:
        return None
    
    # Create DataFrame with exact columns: Week, Day/Shift, Worker Type, Employee ID, Employee Name, Hire Date, Workday Schedule, Department, Manager, Roster Bucket
    df = pd.DataFrame(filtered_data)
    return create_plotly_table_with_tooltips(df)

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
    
    # Weekly Department Details section
    st.markdown("---")
    st.markdown('<div class="section-header">Weekly Department Details</div>', unsafe_allow_html=True)
    

# Four toggle buttons with dynamic highlighting - REPLACE lines 670-687
col1, col2, col3, col4 = st.columns(4)

# Button data for easier management
buttons = [
    {"view": "Shift Summary", "icon": "📊", "label": "Shift Summary"},
    {"view": "Roster HC Summary", "icon": "👥", "label": "Roster HC Summary"}, 
    {"view": "Roster HC Details", "icon": "📋", "label": "Roster HC Details"},
    {"view": "Attendance Assumption", "icon": "📈", "label": "Attendance Assumption"}
]

columns = [col1, col2, col3, col4]

for i, (col, btn) in enumerate(zip(columns, buttons)):
    with col:
        # Determine if this button is selected
        is_selected = st.session_state.current_view == btn["view"]
        
        # Set colors based on selection
        bg_color = "#2ca02c" if is_selected else "#1f77b4"  # Green if selected, blue if not
        text_color = "white"
        border_color = "#2ca02c" if is_selected else "#1f77b4"
        
        # Create custom styled button using HTML
        button_html = f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: 0.75rem;
            border: 2px solid {border_color};
            border-radius: 0.5rem;
            text-align: center;
            font-weight: bold;
            font-size: 0.9rem;
            cursor: pointer;
            margin: 0.25rem 0;
            box-shadow: {'0 4px 8px rgba(0,0,0,0.2)' if is_selected else '0 2px 4px rgba(0,0,0,0.1)'};
            transition: all 0.3s ease;
        " onclick="this.style.transform='scale(0.98)'">
            {btn["icon"]} {btn["label"]}
        </div>
        """
        
        # Display the styled button and handle clicks
        st.markdown(button_html, unsafe_allow_html=True)
        
        # Use an invisible button for click detection
        if st.button(f"Select {btn['label']}", key=f"btn_{i}", label_visibility="hidden"):
            st.session_state.current_view = btn["view"]
            st.rerun()  # Force refresh to show the highlighting immediately
    
    # Display selected view with exact tables and tooltips
    if st.session_state.current_view == "Shift Summary":
        st.markdown("### Shift Summary")
        st.markdown("*Hover over numbers to see detailed breakdowns and comparisons*")
        
        fig = create_transposed_shift_summary_table_with_tooltips()
        st.plotly_chart(fig, use_container_width=True)
    
    elif st.session_state.current_view == "Roster HC Summary":
        st.markdown("### Roster HC Summary")
        st.markdown("Shows Filtered Dept vs Other Depts")
        
        # Simple summary for now - can be enhanced based on more mockup details
        summary_data = []
        for dept, gap in st.session_state.departments.items():
            status = "Selected Dept" if dept == selected_department else "Other Dept"
            summary_data.append({
                'Department': dept,
                'Status': status,
                'Gap in HC': gap,
                'vs Previous Week': f"{gap:+d}"
            })
        
        df = pd.DataFrame(summary_data)
        fig = create_plotly_table_with_tooltips(df)
        st.plotly_chart(fig, use_container_width=True)
    
    elif st.session_state.current_view == "Roster HC Details":
        st.markdown("### Roster HC Details")
        st.markdown("**● Att.Assumption: 92%**")
        st.markdown("**● Vs Prev. Week: -6 workers**")
        
        fig = create_weekly_hc_details_table_with_tooltips()
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Attendance Assumption
        st.markdown("### Attendance Assumption")
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
    
    
    # Show gap analysis for selected department
    gap = st.session_state.departments[selected_department]
    if gap < 0:
        st.error(f"⚠️ {selected_department} is understaffed by {abs(gap)} people")
    elif gap > 0:
        st.success(f"✅ {selected_department} has {gap} extra people")
    else:
        st.info(f"✅ {selected_department} staffing is balanced")
    
    # Employee details table with exact columns and tooltips
    st.markdown(f"### {selected_department} Employee List")
    st.markdown("*Detailed employee roster*")
    
    fig = create_employee_details_table_with_tooltips(selected_department)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
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

