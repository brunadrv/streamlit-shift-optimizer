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
    /* Reduce spacing between plotly charts and expanders */
    .stExpander {
        margin-top: -20px !important;
    }
    .streamlit-expanderHeader {
        margin-top: -10px !important;
    }
    div[data-testid="stExpander"] > div > div {
        margin-top: -15px !important;
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
    
    # Weekly Expected HC Details: Transposed structure with Date, Week Day, Shift, FTE, TEMP, NEW HIRES, FLEX, WW/GS, VEH/MEH, PTO as ROWS
    st.session_state.weekly_hc_details_transposed = {
        '2026-02-12 Thu Shift 1': {
            'FTE': 48,
            'TEMP': 30,
            'NEW HIRES': 0,
            'FLEX': 1,
            'WW/GS': 0,
            'VEH/MEH': 2,
            'PTO': 1,
            'tooltip_fte': 'Previous Week: 45\n• Change: +3',
            'tooltip_temp': 'Previous Week: 28\n• Change: +2',
            'tooltip_newhires': 'Previous Week: 1\n• Change: -1',
            'tooltip_flex': 'Previous Week: 0\n• Change: +1',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 1\n• Change: +1',
            'tooltip_pto': 'Previous Week: 2\n• Change: -1'
        },
        '2026-02-12 Thu Shift 2': {
            'FTE': 58,
            'TEMP': 15,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 55\n• Change: +3',
            'tooltip_temp': 'Previous Week: 18\n• Change: -3',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 1\n• Change: -1',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-12 Thu Shift 3': {
            'FTE': 12,
            'TEMP': 7,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 10\n• Change: +2',
            'tooltip_temp': 'Previous Week: 5\n• Change: +2',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 0\n• Change: 0',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-13 Fri Shift 1': {
            'FTE': 40,
            'TEMP': 21,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 38\n• Change: +2',
            'tooltip_temp': 'Previous Week: 23\n• Change: -2',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 0\n• Change: 0',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-13 Fri Shift 2': {
            'FTE': 50,
            'TEMP': 3,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 47\n• Change: +3',
            'tooltip_temp': 'Previous Week: 5\n• Change: -2',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 0\n• Change: 0',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-13 Fri Shift 3': {
            'FTE': 17,
            'TEMP': 0,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 15\n• Change: +2',
            'tooltip_temp': 'Previous Week: 2\n• Change: -2',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 0\n• Change: 0',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        }
    }
    
    # Attendance Assumption: Transposed structure with Date, Week Day, Shift, FTE Attendance Assumption, TEMP Attendance Assumption, NEW HIRES Show Up Rate, FLEX Show Up Rate, WW/GS Show Up Rate, VEH Show Up Rate as ROWS
    st.session_state.attendance_assumptions_transposed = {
        '2026-02-12 Thu Shift 1': {
            'FTE Attendance Assumption': '90%',
            'TEMP Attendance Assumption': '84%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 88%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 82%\n• Change: +2%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-12 Thu Shift 2': {
            'FTE Attendance Assumption': '90%',
            'TEMP Attendance Assumption': '83%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 87%\n• Change: +3%',
            'tooltip_temp': 'Previous Week: 85%\n• Change: -2%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-12 Thu Shift 3': {
            'FTE Attendance Assumption': '83%',
            'TEMP Attendance Assumption': '81%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 85%\n• Change: -2%',
            'tooltip_temp': 'Previous Week: 79%\n• Change: +2%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        }
    }
    
    st.session_state.employee_data = [
        # Kitchen Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP001', 'Employee Name': 'John Smith', 'Hire Date': '2023-01-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP002', 'Employee Name': 'Mary Davis', 'Hire Date': '2022-08-20', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP101', 'Employee Name': 'Mike Wilson', 'Hire Date': '2026-02-01', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
    ]

def calculate_metrics():
    """Calculate key metrics for the dashboard"""
    expected_hc = 69
    needed_hc = 100
    gap = expected_hc - needed_hc
    gap_percentage = (gap / needed_hc) * 100
    
    return {
        'expected_hc': expected_hc,
        'needed_hc': needed_hc,
        'gap': gap,
        'gap_percentage': gap_percentage
    }

def create_combined_headcount_attendance_table(filtered_hc_data, filtered_attendance_data, selected_department):
    """Create combined HTML table with headcount and attendance assumption columns for each shift"""
    
    tooltip_css = """
    <style>
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
    .combined-table .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #2d5016;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1000;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 11px;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .combined-table .tooltip-text.tooltip-top {
        bottom: 125%;
    }
    .combined-table .tooltip-text.tooltip-bottom {
        top: 125%;
    }
    .combined-table .tooltip-text.tooltip-top::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #2d5016 transparent transparent transparent;
    }
    .combined-table .tooltip-text.tooltip-bottom::after {
        content: "";
        position: absolute;
        bottom: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #2d5016 transparent;
    }
    .combined-table td:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* Color coding for special attention */
    .high-variance { background-color: #ffcccc !important; }
    .medium-variance { background-color: #fff3cd !important; }
    .total-row { background-color: #e6f3ff; font-weight: bold; }
    </style>
    """
    
    # Define employee types including new ones
    employee_types = [
        'FTE', 'TEMP', 'NEW HIRES', 'Day Labor (Flex)', 
        'Day Labor (WW/GS)', 'Overtime (VEH/MEH)', 'Time Off (VER/MTO)'
    ]
    
    # Get shift columns
    shifts = list(filtered_hc_data.keys())
    
    html_content = tooltip_css
    html_content += "<table class='combined-table'>"
    
    # Header row
    html_content += "<thead><tr><th>Employee Type</th>"
    for shift in shifts:
        html_content += f"<th colspan='2'>{shift}</th>"
    html_content += "</tr>"
    
    # Subheader row
    html_content += "<tr><th></th>"
    for shift in shifts:
        html_content += "<th>Scheduled Headcount</th><th>Attendance Assumption</th>"
    html_content += "</tr></thead>"
    
    html_content += "<tbody>"
    
    # Data rows
    for emp_type in employee_types:
        html_content += f"<tr><td class='row-header'>{emp_type}</td>"
        
        for shift in shifts:
            # Get headcount data
            hc_data = filtered_hc_data.get(shift, {})
            
            # Map employee types to data keys
            if emp_type == 'Day Labor (Flex)':
                hc_key = 'FLEX'
            elif emp_type == 'Day Labor (WW/GS)':
                hc_key = 'WW/GS'
            elif emp_type == 'Overtime (VEH/MEH)':
                hc_key = 'VEH/MEH'
            elif emp_type == 'Time Off (VER/MTO)':
                hc_key = 'PTO'
            else:
                hc_key = emp_type
            
            headcount = hc_data.get(hc_key, 0)
            
            # Get attendance assumption
            att_data = filtered_attendance_data.get(shift, {})
            if emp_type == 'FTE':
                attendance = att_data.get('FTE Attendance Assumption', '90%')
            elif emp_type == 'TEMP':
                attendance = att_data.get('TEMP Attendance Assumption', '84%')
            elif emp_type == 'NEW HIRES':
                attendance = att_data.get('NEW HIRES Show Up Rate', '50%')
            elif emp_type == 'Day Labor (Flex)':
                attendance = att_data.get('FLEX Show Up Rate', '50%')
            elif emp_type == 'Day Labor (WW/GS)':
                attendance = att_data.get('WW/GS Show Up Rate', '100%')
            elif emp_type == 'Overtime (VEH/MEH)':
                attendance = att_data.get('VEH Show Up Rate', '80%')
            elif emp_type == 'Time Off (VER/MTO)':
                attendance = '50%'
            else:
                attendance = '100%'
            
            # Get tooltip data from original data structures
            hc_tooltip = hc_data.get(f'tooltip_{hc_key.lower()}', f'Previous Week: {headcount-1}\n• Change: +1')
            att_tooltip = att_data.get(f'tooltip_{emp_type.lower().replace(" ", "").replace("(", "").replace(")", "")}', f'Previous Week: {attendance}\n• Change: 0%')
            
            # Headcount cell
            html_content += f"""<td class='data-cell'>
                {headcount}
                <span class='tooltip-text'>{hc_tooltip}</span>
            </td>"""
            
            # Attendance cell
            html_content += f"""<td class='data-cell'>
                {attendance}
                <span class='tooltip-text'>{att_tooltip}</span>
            </td>"""
        
        html_content += "</tr>"

    html_content += "</tbody></table>"
    
    return html_content

def generate_shift_breakdown(filtered_shift_data, metric_key):
    """Generate shift-level breakdown with vertically aligned shift badges"""
    if not filtered_shift_data:
        return '<div style="color: #999; font-style: italic;">No data available for selected filters</div>'
    
    # Group shifts by day and find all unique shifts
    day_groups = {}
    all_shifts = set()
    
    for shift_key in sorted(filtered_shift_data.keys()):
        parts = shift_key.split(' ')
        if len(parts) >= 4:
            date = parts[0]
            day = parts[1]
            shift_part = parts[-1]
            shift_num = shift_part if shift_part.isdigit() else shift_part.split()[-1]
            
            shift_value = filtered_shift_data[shift_key].get(metric_key, 0)
            
            day_key = f"{date} {day}"
            if day_key not in day_groups:
                day_groups[day_key] = {}
            day_groups[day_key][shift_num] = shift_value
            all_shifts.add(shift_num)
    
    # Sort shifts numerically
    sorted_shifts = sorted(all_shifts, key=lambda x: int(x) if x.isdigit() else 999)
    
    # Generate HTML
    html_parts = []
    for day_key in sorted(day_groups.keys()):
        shifts_for_day = day_groups[day_key]
        
        # Day label
        day_display = day_key.split()[-1]
        html_parts.append(f'<div style="margin-bottom: 4px; font-size: 0.75rem; color: #666;">{day_display}</div>')
        
        # Shift badges for this day
        shift_badges = []
        for shift_num in sorted_shifts:
            if shift_num in shifts_for_day:
                value = shifts_for_day[shift_num]
                shift_badges.append(f'''
                    <span style="
                        background-color: #e3f2fd;
                        color: #1565c0;
                        padding: 2px 6px;
                        border-radius: 12px;
                        font-size: 0.7rem;
                        margin: 0 2px;
                        display: inline-block;
                        min-width: 20px;
                        text-align: center;
                        font-weight: 500;
                    ">S{shift_num}<br>{value}</span>
                ''')
        
        if shift_badges:
            html_parts.append(f'<div style="margin-bottom: 6px;">{"".join(shift_badges)}</div>')
    
    return ''.join(html_parts)

# Main Streamlit App - Applying all requested changes
def main():
    # Header section - keeping original title
    st.markdown('<h1 class="main-header">Labor Planning Shift Optimizer</h1>', unsafe_allow_html=True)
    
    # All filters at the top - Location, Department, Week, Date, Shift
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
        week = st.selectbox("", ["2026-W08", "2026-W07", "2026-W09", "2026-W06", "2026-W10"], 
                           index=0, label_visibility="collapsed")
    
    with col4:
        st.markdown("**Date**")
        available_dates = [
            pd.to_datetime("2026-02-12"),
            pd.to_datetime("2026-02-13"), 
            pd.to_datetime("2026-02-14")
        ]
        selected_dates = st.multiselect(
            "", 
            options=available_dates,
            default=[pd.to_datetime("2026-02-12")],
            format_func=lambda x: x.strftime("%Y-%m-%d"),
            label_visibility="collapsed"
        ) 
    
    with col5:
        st.markdown("**Shift**")
        shifts = st.multiselect("", ["1st", "2nd", "3rd"], 
                               default=["1st", "2nd", "3rd"], label_visibility="collapsed") 
    
    # Calculate metrics
    metrics = calculate_metrics()
    
    # Get filtered data for shift breakdown
    filtered_shift_data = st.session_state.shift_summary_transposed
    filtered_hc_data = st.session_state.weekly_hc_details_transposed
    filtered_attendance_data = st.session_state.attendance_assumptions_transposed
    
    # CHANGE 1 & 4: Overview Section with 4 pills including Total Punches + Shift Breakdowns
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    
    # Key metrics row - All four KPIs: Needed HC, Expected HC, Gap in HC, Total Punches
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-label">Needed HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">100</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📊 5% vs last week</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Expected HC</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">69</div>', unsafe_allow_html=True)
        
        # CHANGE 1: Add shift breakdown under Expected HC
        expected_breakdown = generate_shift_breakdown(filtered_shift_data, 'Total Expected')
        st.markdown(f'<div style="background-color: #f8f9fa; border-radius: 6px; padding: 8px; margin-top: 8px;">{expected_breakdown}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-change">📈 20% vs last week</div>', unsafe_allow_html=True)
    
    with col3:
        gap_class = "gap-negative" if metrics['gap'] < 0 else "gap-positive"
        st.markdown('<div class="metric-label">Gap in HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{gap_class}">31</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📉 3% vs last week</div>', unsafe_allow_html=True)

    with col4:
        # CHANGE 4: Add Total Punches pill
        st.markdown('<div class="metric-label">Total Punches</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-large">79</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📊 4% vs last week</div>', unsafe_allow_html=True)
    
    # CHANGE 3: Rename section header from "Department Details" to "Kitchen Expected HC (69)"
    department_expected = 69  # Using Kitchen's expected HC
    st.markdown(f'<div class="section-header">{selected_department} Expected HC ({department_expected})</div>', unsafe_allow_html=True)
    
    # CHANGE 5 & 6: Remove radio buttons and Shift Summary table, show only combined table
    # CHANGE 6: Combined Headcount + Attendance table (no more separate views)
    # CHANGE 2: Tooltips showing variance from previous week are already in the data
    
    # Legend
    st.markdown("""
    <div style="margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f8f9fa;">
        <strong>Legend:</strong>
        <span style="margin-left: 20px; padding: 4px 8px; background-color: #ffcccc; border-radius: 3px;">>20% variance from last week</span>
        <span style="margin-left: 10px; padding: 4px 8px; background-color: #fff3cd; border-radius: 3px;">10-20% variance from last week</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Display unified headcount and attendance table
    html_table = create_combined_headcount_attendance_table(filtered_hc_data, filtered_attendance_data, selected_department)
    st.components.v1.html(html_table, height=500)
    
    # Employee List section (keeping this as before)
    st.markdown(f'<div class="section-header">{selected_department} Employee List ({department_expected})</div>', unsafe_allow_html=True)
    
    # Employee data table
    df = pd.DataFrame(st.session_state.employee_data)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()