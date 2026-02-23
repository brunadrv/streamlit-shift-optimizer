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
        },
        '2026-02-14 Sat Shift 1': {
            'FTE': 43,
            'TEMP': 35,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 40\n• Change: +3',
            'tooltip_temp': 'Previous Week: 32\n• Change: +3',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 0\n• Change: 0',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-14 Sat Shift 2': {
            'FTE': 62,
            'TEMP': 17,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 58\n• Change: +4',
            'tooltip_temp': 'Previous Week: 20\n• Change: -3',
            'tooltip_newhires': 'Previous Week: 0\n• Change: 0',
            'tooltip_flex': 'Previous Week: 0\n• Change: 0',
            'tooltip_wwgs': 'Previous Week: 0\n• Change: 0',
            'tooltip_vehmeh': 'Previous Week: 0\n• Change: 0',
            'tooltip_pto': 'Previous Week: 0\n• Change: 0'
        },
        '2026-02-14 Sat Shift 3': {
            'FTE': 10,
            'TEMP': 6,
            'NEW HIRES': 0,
            'FLEX': 0,
            'WW/GS': 0,
            'VEH/MEH': '',
            'PTO': '',
            'tooltip_fte': 'Previous Week: 8\n• Change: +2',
            'tooltip_temp': 'Previous Week: 4\n• Change: +2',
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
        },
        '2026-02-13 Fri Shift 1': {
            'FTE Attendance Assumption': '93%',
            'TEMP Attendance Assumption': '60%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 91%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 65%\n• Change: -5%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-13 Fri Shift 2': {
            'FTE Attendance Assumption': '86%',
            'TEMP Attendance Assumption': '78%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 84%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 80%\n• Change: -2%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-13 Fri Shift 3': {
            'FTE Attendance Assumption': '84%',
            'TEMP Attendance Assumption': '100%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 82%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 95%\n• Change: +5%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-14 Sat Shift 1': {
            'FTE Attendance Assumption': '92%',
            'TEMP Attendance Assumption': '76%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 90%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 74%\n• Change: +2%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-14 Sat Shift 2': {
            'FTE Attendance Assumption': '91%',
            'TEMP Attendance Assumption': '71%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 89%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 73%\n• Change: -2%',
            'tooltip_newhires': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_flex': 'Previous Week: 50%\n• Change: 0%',
            'tooltip_wwgs': 'Previous Week: 100%\n• Change: 0%',
            'tooltip_veh': 'Previous Week: 80%\n• Change: 0%'
        },
        '2026-02-14 Sat Shift 3': {
            'FTE Attendance Assumption': '88%',
            'TEMP Attendance Assumption': '72%',
            'NEW HIRES Show Up Rate': '50%',
            'FLEX Show Up Rate': '50%',
            'WW/GS Show Up Rate': '100.00%',
            'VEH Show Up Rate': '80.00%',
            'tooltip_fte': 'Previous Week: 86%\n• Change: +2%',
            'tooltip_temp': 'Previous Week: 70%\n• Change: +2%',
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
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'EMP005', 'Employee Name': 'Carlos Rodriguez', 'Hire Date': '2023-11-08', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'EMP003', 'Employee Name': 'Lisa Brown', 'Hire Date': '2021-12-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'NEW HIRES', 'Employee ID': 'NEW001', 'Employee Name': 'David Garcia', 'Hire Date': '2026-02-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Training'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'TEMP', 'Employee ID': 'TMP102', 'Employee Name': 'Amanda Taylor', 'Hire Date': '2026-01-28', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'EMP004', 'Employee Name': 'Jennifer Lee', 'Hire Date': '2023-06-05', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FLEX', 'Employee ID': 'FLX201', 'Employee Name': 'Robert Martinez', 'Hire Date': '2024-03-12', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Flexible'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'EMP006', 'Employee Name': 'Patricia White', 'Hire Date': '2022-05-18', 'Workday Schedule': '22:00-06:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        
        # Production Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'PRD001', 'Employee Name': 'James Wilson', 'Hire Date': '2023-03-22', 'Workday Schedule': '06:00-14:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'PRD002', 'Employee Name': 'Emma Johnson', 'Hire Date': '2022-11-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP201', 'Employee Name': 'Kevin Chen', 'Hire Date': '2026-01-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'PRD003', 'Employee Name': 'Rachel Adams', 'Hire Date': '2023-07-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FLEX', 'Employee ID': 'FLX301', 'Employee Name': 'Anthony Davis', 'Hire Date': '2024-01-08', 'Workday Schedule': '14:00-22:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Flexible'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'PRD004', 'Employee Name': 'Stephanie Lee', 'Hire Date': '2022-09-05', 'Workday Schedule': '22:00-06:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        
        # Sanitation Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'SAN001', 'Employee Name': 'Daniel Brown', 'Hire Date': '2023-02-14', 'Workday Schedule': '06:00-14:00', 'Department': 'Sanitation', 'Manager': 'Linda Rodriguez', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP301', 'Employee Name': 'Maria Gonzalez', 'Hire Date': '2026-01-20', 'Workday Schedule': '06:00-14:00', 'Department': 'Sanitation', 'Manager': 'Linda Rodriguez', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'SAN002', 'Employee Name': 'Christopher Moore', 'Hire Date': '2023-05-30', 'Workday Schedule': '14:00-22:00', 'Department': 'Sanitation', 'Manager': 'Linda Rodriguez', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FTE', 'Employee ID': 'SAN003', 'Employee Name': 'Jessica Taylor', 'Hire Date': '2022-12-12', 'Workday Schedule': '22:00-06:00', 'Department': 'Sanitation', 'Manager': 'Linda Rodriguez', 'Roster Bucket': 'Active'},
        
        # Quality Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'QUA001', 'Employee Name': 'Thomas Anderson', 'Hire Date': '2023-04-18', 'Workday Schedule': '06:00-14:00', 'Department': 'Quality', 'Manager': 'Janet Wilson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'QUA002', 'Employee Name': 'Nicole Martinez', 'Hire Date': '2022-10-25', 'Workday Schedule': '06:00-14:00', 'Department': 'Quality', 'Manager': 'Janet Wilson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'NEW HIRES', 'Employee ID': 'NEW002', 'Employee Name': 'Brian Clark', 'Hire Date': '2026-02-05', 'Workday Schedule': '14:00-22:00', 'Department': 'Quality', 'Manager': 'Janet Wilson', 'Roster Bucket': 'Training'},
        
        # Warehouse Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'WHR001', 'Employee Name': 'Matthew Garcia', 'Hire Date': '2023-01-30', 'Workday Schedule': '06:00-14:00', 'Department': 'Warehouse', 'Manager': 'Robert Kim', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'WHR002', 'Employee Name': 'Ashley Thompson', 'Hire Date': '2022-08-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Warehouse', 'Manager': 'Robert Kim', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP401', 'Employee Name': 'Ryan Miller', 'Hire Date': '2026-01-25', 'Workday Schedule': '06:00-14:00', 'Department': 'Warehouse', 'Manager': 'Robert Kim', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'WHR003', 'Employee Name': 'Michelle White', 'Hire Date': '2023-06-20', 'Workday Schedule': '14:00-22:00', 'Department': 'Warehouse', 'Manager': 'Robert Kim', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/3rd', 'Worker Type': 'FLEX', 'Employee ID': 'FLX401', 'Employee Name': 'Steven Lopez', 'Hire Date': '2024-02-14', 'Workday Schedule': '22:00-06:00', 'Department': 'Warehouse', 'Manager': 'Robert Kim', 'Roster Bucket': 'Flexible'},
        
        # Fulfillment Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'FUL001', 'Employee Name': 'Amanda Rodriguez', 'Hire Date': '2023-03-08', 'Workday Schedule': '06:00-14:00', 'Department': 'Fulfillment', 'Manager': 'David Chang', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'TEMP', 'Employee ID': 'TMP501', 'Employee Name': 'Jonathan Smith', 'Hire Date': '2026-02-08', 'Workday Schedule': '06:00-14:00', 'Department': 'Fulfillment', 'Manager': 'David Chang', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'FTE', 'Employee ID': 'FUL002', 'Employee Name': 'Samantha Davis', 'Hire Date': '2022-11-30', 'Workday Schedule': '14:00-22:00', 'Department': 'Fulfillment', 'Manager': 'David Chang', 'Roster Bucket': 'Active'},
        
        # Shipping Department
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'SHP001', 'Employee Name': 'Gregory Wilson', 'Hire Date': '2023-05-12', 'Workday Schedule': '06:00-14:00', 'Department': 'Shipping', 'Manager': 'Patricia Lee', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/1st', 'Worker Type': 'FTE', 'Employee ID': 'SHP002', 'Employee Name': 'Kimberly Johnson', 'Hire Date': '2022-07-22', 'Workday Schedule': '06:00-14:00', 'Department': 'Shipping', 'Manager': 'Patricia Lee', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'TEMP', 'Employee ID': 'TMP601', 'Employee Name': 'Eric Brown', 'Hire Date': '2026-01-18', 'Workday Schedule': '14:00-22:00', 'Department': 'Shipping', 'Manager': 'Patricia Lee', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Day/Shift': 'Monday/2nd', 'Worker Type': 'NEW HIRES', 'Employee ID': 'NEW003', 'Employee Name': 'Catherine Martinez', 'Hire Date': '2026-02-12', 'Workday Schedule': '14:00-22:00', 'Department': 'Shipping', 'Manager': 'Patricia Lee', 'Roster Bucket': 'Training'},
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

def create_transposed_shift_summary_table_with_tooltips(filtered_data=None):
    """Create transposed shift summary table matching the screenshot structure"""
    
    # Use filtered data if provided, otherwise use all data
    data_to_use = filtered_data if filtered_data else st.session_state.shift_summary_transposed
    
    # Prepare the transposed structure
    columns = list(data_to_use.keys())
    rows = ['Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']
    
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
            values=['Date & Shift'] + columns,
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=12, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=[['Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']] + 
                   [[data_to_use[col][row] for row in rows] for col in columns],
            fill_color=[['#f9f9f9'] * len(rows)] + 
                      [['white' for row in rows] for col in columns],
            align='center',
            font=dict(size=12),
            height=25,
        )
    )])
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),  # Use valid margin values
        title="Shift Summary - Hover over values to see details"
    )
    
    return fig

def create_weekly_hc_details_table_with_tooltips():
    """Create transposed HC details table matching the screenshot structure"""
    
    # Prepare the transposed structure
    columns = list(st.session_state.weekly_hc_details_transposed.keys())
    rows = ['FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'WW/GS', 'VEH/MEH', 'PTO']
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date & Shift'] + columns,
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=12, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=[['FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'WW/GS', 'VEH/MEH', 'PTO']] + 
                   [[st.session_state.weekly_hc_details_transposed[col][row] for row in rows] for col in columns],
            fill_color=[['#f9f9f9'] * len(rows)] + 
                      [['white' for row in rows] for col in columns],
            align='center',
            font=dict(size=12),
            height=25,
        )
    )])
    
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),  # Use valid margin values
        title="HC Details - Hover over values to see details"
    )
    
    return fig

def create_transposed_attendance_assumptions_table(filtered_data=None):
    """Create transposed attendance assumptions table matching the screenshot structure - UPDATED TO USE TRANSPOSED VERSION"""
    
    # Use filtered data if provided, otherwise use all data
    data_to_use = filtered_data if filtered_data else st.session_state.attendance_assumptions_transposed
    
    # Prepare the transposed structure
    columns = list(data_to_use.keys())
    rows = ['FTE Attendance Assumption', 'TEMP Attendance Assumption', 'NEW HIRES Show Up Rate', 'FLEX Show Up Rate', 'WW/GS Show Up Rate', 'VEH Show Up Rate']
    
    def get_tooltip_for_cell(col, row):
        """Get tooltip for each cell based on column and row"""
        data = data_to_use[col]
        if row == 'FTE Attendance Assumption' and 'tooltip_fte' in data:
            return data['tooltip_fte']
        elif row == 'TEMP Attendance Assumption' and 'tooltip_temp' in data:
            return data['tooltip_temp']  
        elif row == 'NEW HIRES Show Up Rate' and 'tooltip_newhires' in data:
            return data['tooltip_newhires']
        elif row == 'FLEX Show Up Rate' and 'tooltip_flex' in data:
            return data['tooltip_flex']
        elif row == 'WW/GS Show Up Rate' and 'tooltip_wwgs' in data:
            return data['tooltip_wwgs']
        elif row == 'VEH Show Up Rate' and 'tooltip_veh' in data:
            return data['tooltip_veh']
        else:
            return f"{row}: {data.get(row, 'N/A')}"
    
    # Prepare cell values and colors for Plotly
    cell_values = [rows]  # First column is row labels
    cell_colors = [['#f9f9f9'] * len(rows)]  # First column color
    
    for col in columns:
        col_values = []
        col_colors = []
        for row in rows:
            value = data_to_use[col][row]
            col_values.append(value)
            col_colors.append('white')
        cell_values.append(col_values)
        cell_colors.append(col_colors)
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date & Shift'] + columns,  # Empty first header for row labels column
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=12, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=cell_values,
            fill_color=cell_colors,
            align='center',
            font=dict(size=12),
            height=25,
        )
    )])
    
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),  # Use valid margin values
        title="Attendance Assumptions - Transposed View"
    )
    
    return fig

def create_transposed_hc_details_table_with_tooltips(filtered_data=None):
    """Create transposed HC details table matching the screenshot structure"""
    
    # Use filtered data if provided, otherwise use all data
    data_to_use = filtered_data if filtered_data else st.session_state.weekly_hc_details_transposed
    
    # Prepare the transposed structure
    columns = list(data_to_use.keys())
    rows = ['FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'WW/GS', 'VEH/MEH', 'PTO']
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date & Shift'] + columns,
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=12, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=[['FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'WW/GS', 'VEH/MEH', 'PTO']] + 
                   [[data_to_use[col][row] for row in rows] for col in columns],
            fill_color=[['#f9f9f9'] * len(rows)] + 
                      [['white' for row in rows] for col in columns],
            align='center',
            font=dict(size=12),
            height=25,
        )
    )])
    
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        title="HC Details - Hover over values to see details"
    )
    
    return fig

def create_weekly_hc_details_table_with_tooltips():
    """Create weekly HC details table with exact columns and tooltips - UPDATED TO USE TRANSPOSED VERSION"""
    return create_transposed_hc_details_table_with_tooltips()

def create_attendance_assumptions_table_with_tooltips():
    """Create attendance assumptions table with exact columns and tooltips - UPDATED TO USE TRANSPOSED VERSION"""
    return create_transposed_attendance_assumptions_table()

def create_employee_details_table_with_tooltips(selected_dept, filtered_employees=None):
    """Create employee details table with exact columns and tooltips"""
    # Use filtered employees if provided, otherwise filter by department only
    if filtered_employees is not None:
        filtered_data = filtered_employees
    else:
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

def calculate_dynamic_metrics(location, department, week, selected_date, shifts):
    """Calculate dynamic metrics based on filter selections"""
    
    # Base metrics that vary by location
    base_metrics = {
        "AZ Goodyear": {"needed": 100, "expected": 80, "gap": 20},
        "IL Aurora": {"needed": 85, "expected": 75, "gap": 10}, 
        "AZ Phoenix": {"needed": 120, "expected": 95, "gap": 25},
        "IL Lake Zurich": {"needed": 90, "expected": 85, "gap": 5},
        "IL Burr Ridge": {"needed": 75, "expected": 70, "gap": 5}
    }
    
    # Department multipliers
    dept_multipliers = {
        "Kitchen": 1.0,
        "Production": 0.8,
        "Sanitation": 0.6,
        "Quality": 0.4,
        "Warehouse": 0.9,
        "Fulfillment": 0.7,
        "Shipping": 0.5
    }
    
    # Week variations (recent weeks have different patterns)
    week_variations = {
        "2026-W08": 1.0,
        "2026-W07": 0.95,
        "2026-W09": 1.05,
        "2026-W06": 0.9,
        "2026-W10": 1.1
    }
    
    # Shift adjustments (fewer shifts selected = lower numbers)
    shift_multiplier = len(shifts) / 3.0 if shifts else 1.0
    
    # Get base metrics for location
    base = base_metrics.get(location, base_metrics["AZ Goodyear"])
    
    # Apply all multipliers
    dept_mult = dept_multipliers.get(department, 1.0)
    week_mult = week_variations.get(week, 1.0)
    
    # Calculate final metrics
    needed = int(base["needed"] * dept_mult * week_mult * shift_multiplier)
    expected = int(base["expected"] * dept_mult * week_mult * shift_multiplier)
    gap = needed - expected
    
    # Calculate percentage changes vs "last week"
    needed_change = int((week_mult - 0.95) * 100)  # Simulate vs previous week
    expected_change = int((week_mult - 0.9) * 100 + 10)  # Different baseline
    
    return {
        "needed": needed,
        "expected": expected, 
        "gap": gap,
        "needed_change": needed_change,
        "expected_change": expected_change,
        "gap_percentage": int((gap / needed * 100)) if needed > 0 else 0
    }

def get_gap_status_info(gap, gap_percentage):
    """Get gap status with appropriate styling and messaging"""
    if gap == 0:
        return "✅ Fully Staffed", "gap-neutral", "#28a745"
    elif gap > 0:
        return f"↘️ Understaffed by {abs(gap_percentage)}%", "gap-negative", "#dc3545"
    else:
        return f"↗️ Overstaffed by {abs(gap_percentage)}%", "gap-positive", "#28a745"

def create_attendance_html_table_with_tooltips(filtered_attendance_data):
    """Create HTML table with tooltips for attendance assumption data - transposed structure"""
    
    tooltip_css = """
    <style>
    .attendance-table {
        width: 100%; 
        border-collapse: collapse; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 12px;
        margin: 10px 0;
    }
    .attendance-table th {
        background-color: #f1f1f1; 
        color: #2E4057; 
        font-weight: bold; 
        padding: 8px; 
        text-align: center; 
        border: 1px solid #ddd;
        font-size: 10px;
    }
    .attendance-table td {
        padding: 6px 8px; 
        text-align: center; 
        border: 1px solid #ddd; 
        position: relative;
        cursor: help;
    }
    .attendance-table td.row-header {
        background-color: #f9f9f9; 
        font-weight: bold;
        text-align: left;
        cursor: default;
    }
    .attendance-table td.data-cell:hover {
        background-color: #fff3e0 !important;
    }
    .attendance-table .tooltip-text {
        visibility: hidden;
        width: 320px;
        background-color: #e65100;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -160px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 11px;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .attendance-table .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #e65100 transparent transparent transparent;
    }
    .attendance-table td:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    
    # Prepare the transposed structure - metrics as rows, shifts as columns
    columns = list(filtered_attendance_data.keys())
    rows = ['FTE Attendance Assumption', 'TEMP Attendance Assumption', 'NEW HIRES Show Up Rate', 
            'FLEX Show Up Rate', 'WW/GS Show Up Rate', 'VEH Show Up Rate']
    
    # Build HTML table
    html_content = tooltip_css
    html_content += "<table class='attendance-table'>"
    
    # Header row - empty cell + shift columns
    html_content += "<tr><th></th>"
    for shift_key in sorted(columns):
        parts = shift_key.split(' ')
        date = parts[0]
        day = parts[1]
        shift_num = parts[-1].split(' ')[-1]
        html_content += f"<th>{date} {day}<br>Shift {shift_num}</th>"
    html_content += "</tr>"
    
    # Data rows - each metric as a row
    for row_name in rows:
        html_content += "<tr>"
        html_content += f"<td class='row-header'>{row_name}</td>"
        
        for shift_key in sorted(columns):
            data = filtered_attendance_data[shift_key]
            value = data[row_name]
            
            # Get appropriate tooltip
            tooltip = ""
            if row_name == 'FTE Attendance Assumption':
                tooltip = data.get('tooltip_fte', '')
            elif row_name == 'TEMP Attendance Assumption':
                tooltip = data.get('tooltip_temp', '')
            elif row_name == 'NEW HIRES Show Up Rate':
                tooltip = data.get('tooltip_newhires', '')
            elif row_name == 'FLEX Show Up Rate':
                tooltip = data.get('tooltip_flex', '')
            elif row_name == 'WW/GS Show Up Rate':
                tooltip = data.get('tooltip_wwgs', '')
            elif row_name == 'VEH Show Up Rate':
                tooltip = data.get('tooltip_veh', '')
            
            # Create detailed tooltip content
            parts = shift_key.split(' ')
            date = parts[0]
            day = parts[1]
            shift_num = parts[-1].split(' ')[-1]
            
            tooltip_content = f"<strong>{row_name}</strong><br>{date} {day} - Shift {shift_num}<br><br>"
            
            if tooltip:
                tooltip_content += tooltip.replace('\n', '<br>')
            else:
                tooltip_content += f"Current value: {value}<br>No comparison data available"
            
            # Additional context from expandable details
            tooltip_content += "<br><br><strong>Additional Information:</strong><br>"
            
            if 'FTE' in row_name:
                tooltip_content += "• Full-time employee attendance rate<br>"
                tooltip_content += "• Based on historical performance<br>"
                tooltip_content += "• Core workforce reliability metric"
            elif 'TEMP' in row_name:
                tooltip_content += "• Temporary worker attendance rate<br>"
                tooltip_content += "• Generally more variable than FTE<br>"
                tooltip_content += "• Seasonal/contract workforce metric"
            elif 'NEW HIRES' in row_name:
                tooltip_content += "• New employee show-up rate<br>"
                tooltip_content += "• Typically lower during adjustment period<br>"
                tooltip_content += "• Training and onboarding consideration"
            elif 'FLEX' in row_name:
                tooltip_content += "• Flexible worker show-up rate<br>"
                tooltip_content += "• On-demand workforce availability<br>"
                tooltip_content += "• Peak coverage support"
            elif 'WW/GS' in row_name:
                tooltip_content += "• Warehouse/General Support rate<br>"
                tooltip_content += "• Cross-functional team reliability<br>"
                tooltip_content += "• Support operations coverage"
            elif 'VEH' in row_name:
                tooltip_content += "• Vehicle/Equipment operator rate<br>"
                tooltip_content += "• Specialized role reliability<br>"
                tooltip_content += "• Critical operations support"
            
            # Add performance indicators
            if '%' in str(value):
                try:
                    rate = float(str(value).replace('%', ''))
                    if rate >= 90:
                        tooltip_content += "<br><br>🟢 <strong>Excellent</strong> - High reliability"
                    elif rate >= 80:
                        tooltip_content += "<br><br>🟡 <strong>Good</strong> - Acceptable performance"
                    elif rate >= 70:
                        tooltip_content += "<br><br>🟠 <strong>Fair</strong> - Needs improvement"
                    else:
                        tooltip_content += "<br><br>🔴 <strong>Poor</strong> - Immediate attention needed"
                except:
                    pass
            
            html_content += f"""<td class='data-cell'>
                {value}
                <span class='tooltip-text'>{tooltip_content}</span>
            </td>"""
        
        html_content += "</tr>"
    
    html_content += "</table>"
    
    return html_content

def create_roster_hc_html_table_with_tooltips(filtered_hc_data):
    """Create HTML table with tooltips for roster HC data - transposed structure"""
    
    tooltip_css = """
    <style>
    .hc-table {
        width: 100%; 
        border-collapse: collapse; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 12px;
        margin: 10px 0;
    }
    .hc-table th {
        background-color: #f1f1f1; 
        color: #2E4057; 
        font-weight: bold; 
        padding: 8px; 
        text-align: center; 
        border: 1px solid #ddd;
        font-size: 11px;
    }
    .hc-table td {
        padding: 6px 8px; 
        text-align: center; 
        border: 1px solid #ddd; 
        position: relative;
        cursor: help;
    }
    .hc-table td.row-header {
        background-color: #f9f9f9; 
        font-weight: bold;
        text-align: left;
        cursor: default;
    }
    .hc-table td.data-cell:hover {
        background-color: #e8f5e8 !important;
    }
    .hc-table .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #2d5016;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 11px;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .hc-table .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #2d5016 transparent transparent transparent;
    }
    .hc-table td:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    
    # Prepare the transposed structure - metrics as rows, shifts as columns
    columns = list(filtered_hc_data.keys())
    rows = ['FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'Total HC']
    
    # Build HTML table
    html_content = tooltip_css
    html_content += "<table class='hc-table'>"
    
    # Header row - empty cell + shift columns
    html_content += "<tr><th></th>"
    for shift_key in sorted(columns):
        parts = shift_key.split(' ')
        date = parts[0]
        day = parts[1]
        shift_num = parts[-1].split(' ')[-1]
        html_content += f"<th>{date} {day}<br>Shift {shift_num}</th>"
    html_content += "</tr>"
    
    # Data rows - each metric as a row
    for row_name in rows:
        html_content += "<tr>"
        html_content += f"<td class='row-header'>{row_name}</td>"
        
        for shift_key in sorted(columns):
            data = filtered_hc_data[shift_key]
            
            # Handle Total HC calculation
            if row_name == 'Total HC':
                fte_val = data.get('FTE', 0)
                temp_val = data.get('TEMP', 0)
                nh_val = data.get('NEW HIRES', 0)
                flex_val = data.get('FLEX', 0)
                value = fte_val + temp_val + nh_val + flex_val
            else:
                value = data.get(row_name, 0)
            
            # Get appropriate tooltip
            tooltip = ""
            if row_name == 'FTE':
                tooltip = data.get('tooltip_fte', '')
            elif row_name == 'TEMP':
                tooltip = data.get('tooltip_temp', '')
            elif row_name == 'NEW HIRES':
                tooltip = data.get('tooltip_newhires', '')
            elif row_name == 'FLEX':
                tooltip = data.get('tooltip_flex', '')
            elif row_name == 'Total HC':
                tooltip = f"Total: {value} = {data.get('FTE', 0)} FTE + {data.get('TEMP', 0)} TEMP + {data.get('NEW HIRES', 0)} New + {data.get('FLEX', 0)} Flex"
            
            # Create detailed tooltip content
            parts = shift_key.split(' ')
            date = parts[0]
            day = parts[1]
            shift_num = parts[-1].split(' ')[-1]
            
            tooltip_content = f"<strong>{row_name} Details</strong><br>{date} {day} - Shift {shift_num}<br><br>"
            
            if tooltip:
                tooltip_content += tooltip.replace('\n', '<br>')
            else:
                tooltip_content += f"Current value: {value}<br>No comparison data available"
            
            # Additional context from expandable details
            tooltip_content += "<br><br><strong>Additional Information:</strong><br>"
            tooltip_content += f"• {row_name} headcount for this shift<br>"
            
            if 'FTE' in row_name:
                tooltip_content += "• Full-time equivalent employees<br>"
                tooltip_content += "• Permanent staff with benefits<br>"
                tooltip_content += "• Core workforce foundation"
            elif 'TEMP' in row_name:
                tooltip_content += "• Temporary workers<br>"
                tooltip_content += "• Contract or seasonal staff<br>"
                tooltip_content += "• Variable demand coverage"
            elif 'NEW HIRES' in row_name:
                tooltip_content += "• Recently hired employees<br>"
                tooltip_content += "• In training or onboarding<br>"
                tooltip_content += "• Building experience and skills"
            elif 'FLEX' in row_name:
                tooltip_content += "• Flexible workers<br>"
                tooltip_content += "• On-demand scheduling<br>"
                tooltip_content += "• Peak coverage support"
            elif 'Total HC' in row_name:
                fte_val = data.get('FTE', 0)
                temp_val = data.get('TEMP', 0) 
                nh_val = data.get('NEW HIRES', 0)
                flex_val = data.get('FLEX', 0)
                tooltip_content += f"• Breakdown: {fte_val} FTE + {temp_val} TEMP + {nh_val} New + {flex_val} Flex<br>"
                tooltip_content += "• Complete workforce count<br>"
                tooltip_content += "• All employee categories combined"
            
            html_content += f"""<td class='data-cell'>
                {value}
                <span class='tooltip-text'>{tooltip_content}</span>
            </td>"""
        
        html_content += "</tr>"
    
    html_content += "</table>"
    
    return html_content

def create_shift_summary_html_table_with_tooltips(filtered_shift_data):
    """Create HTML table with tooltips for shift summary data - transposed structure"""
    
    tooltip_css = """
    <style>
    .shift-table {
        width: 100%; 
        border-collapse: collapse; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 12px;
        margin: 10px 0;
    }
    .shift-table th {
        background-color: #f1f1f1; 
        color: #2E4057; 
        font-weight: bold; 
        padding: 8px; 
        text-align: center; 
        border: 1px solid #ddd;
        font-size: 11px;
    }
    .shift-table td {
        padding: 6px 8px; 
        text-align: center; 
        border: 1px solid #ddd; 
        position: relative;
        cursor: help;
    }
    .shift-table td.row-header {
        background-color: #f9f9f9; 
        font-weight: bold;
        text-align: left;
        cursor: default;
    }
    .shift-table td.data-cell:hover {
        background-color: #e3f2fd !important;
    }
    .shift-table .tooltip-text {
        visibility: hidden;
        width: 280px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -140px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 11px;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .shift-table .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }
    .shift-table td:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    
    # Prepare the transposed structure - metrics as rows, shifts as columns
    columns = list(filtered_shift_data.keys())
    rows = ['Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']
    
    # Build HTML table
    html_content = tooltip_css
    html_content += "<table class='shift-table'>"
    
    # Header row - empty cell + shift columns
    html_content += "<tr><th></th>"
    for shift_key in sorted(columns):
        parts = shift_key.split(' ')
        date = parts[0]
        day = parts[1]
        shift_num = parts[-1].split(' ')[-1]
        html_content += f"<th>{date} {day}<br>Shift {shift_num}</th>"
    html_content += "</tr>"
    
    # Data rows - each metric as a row
    for row_name in rows:
        html_content += "<tr>"
        html_content += f"<td class='row-header'>{row_name}</td>"
        
        for shift_key in sorted(columns):
            data = filtered_shift_data[shift_key]
            value = data[row_name]
            
            # Get appropriate tooltip
            tooltip = ""
            if row_name == 'Total Needed':
                tooltip = data.get('tooltip_needed', '')
            elif row_name == 'Total Expected':
                tooltip = data.get('tooltip_expected', '')
            elif row_name == 'Total Gap':
                tooltip = data.get('tooltip_gap', '')
            elif row_name == 'Total Attendance Assumption':
                tooltip = data.get('tooltip_attendance', '')
            elif row_name == 'Total Punches':
                tooltip = data.get('tooltip_punches', '')
            
            # Create detailed tooltip content
            parts = shift_key.split(' ')
            date = parts[0]
            day = parts[1]
            shift_num = parts[-1].split(' ')[-1]
            
            tooltip_content = f"<strong>{row_name}</strong><br>{date} {day} - Shift {shift_num}<br><br>"
            
            if tooltip:
                tooltip_content += tooltip.replace('\n', '<br>')
            else:
                tooltip_content += f"Current value: {value}<br>No comparison data available"
            
            # Additional context based on metric
            if 'Gap' in row_name and str(value).replace('-', '').isdigit():
                gap_val = int(value) if str(value).replace('-', '').isdigit() else 0
                if gap_val > 0:
                    tooltip_content += "<br><br>⚠️ <strong>Staffing shortage</strong> - Additional staff needed"
                elif gap_val < 0:
                    tooltip_content += "<br><br>✅ <strong>Overstaffed</strong> - Consider reallocation"
                else:
                    tooltip_content += "<br><br>✅ <strong>Optimal staffing</strong> - No gap detected"
            
            # Add color coding for gap values
            cell_class = "data-cell"
            if row_name == 'Total Gap':
                try:
                    gap_val = int(value) if str(value).replace('-', '').isdigit() else 0
                    if gap_val < 0:
                        cell_class += " gap-negative"
                    elif gap_val > 0:
                        cell_class += " gap-positive"
                except:
                    pass
            
            html_content += f"""<td class='{cell_class}'>
                {value}
                <span class='tooltip-text'>{tooltip_content}</span>
            </td>"""
        
        html_content += "</tr>"
    
    html_content += "</table>"
    
    return html_content

def create_html_table_with_tooltips(data_dict, rows, table_title, tooltip_mapping=None):
    """Create HTML table with hover tooltips instead of Plotly table"""
    
    columns = list(data_dict.keys())
    
    # CSS for hover tooltips
    tooltip_css = """
    <style>
    .tooltip-table {
        width: 100%; 
        border-collapse: collapse; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 12px;
        margin: 10px 0;
    }
    .tooltip-table th {
        background-color: #f1f1f1; 
        color: #2E4057; 
        font-weight: bold; 
        padding: 8px; 
        text-align: center; 
        border: 1px solid #ddd;
        font-size: 10px;
    }
    .tooltip-table td {
        padding: 6px 8px; 
        text-align: center; 
        border: 1px solid #ddd; 
        position: relative;
        cursor: help;
    }
    .tooltip-table td.row-header {
        background-color: #f9f9f9; 
        font-weight: bold;
        cursor: default;
    }
    .tooltip-table td:not(.row-header):hover {
        background-color: #e3f2fd !important;
    }
    .tooltip-table .tooltip-text {
        visibility: hidden;
        width: 250px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -125px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 11px;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .tooltip-table .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }
    .tooltip-table td:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    
    # Build HTML table
    html_content = tooltip_css
    html_content += f"<div style='margin: 20px 0;'><strong>{table_title}</strong></div>"
    html_content += "<table class='tooltip-table'>"
    
    # Header row
    html_content += "<tr><th>Date & Shift</th>"
    for col in columns:
        html_content += f"<th>{col}</th>"
    html_content += "</tr>"
    
    # Data rows
    for row in rows:
        html_content += "<tr>"
        html_content += f"<td class='row-header'>{row}</td>"
        
        for col in columns:
            value = data_dict[col].get(row, '')
            tooltip_text = ""
            
            # Get tooltip text based on mapping
            if tooltip_mapping and col in data_dict:
                tooltip_key = tooltip_mapping.get(row, '')
                if tooltip_key and tooltip_key in data_dict[col]:
                    tooltip_text = data_dict[col][tooltip_key].replace('\n', '<br>')
            
            if tooltip_text:
                html_content += f"""<td>
                    {value}
                    <span class='tooltip-text'>{tooltip_text}</span>
                </td>"""
            else:
                html_content += f"<td class='row-header'>{value}</td>"
        
        html_content += "</tr>"
    
    html_content += "</table>"
    
    return html_content

def render_metric_with_tooltip(metric_name: str, tooltip_text: str):
    """Render metric label with tooltip using details/summary HTML elements"""
    st.markdown(
        """
        <style>
          .metric-tooltip { display:inline-block; margin-left:6px; }
          .metric-tooltip summary {
            list-style:none; cursor:pointer; user-select:none; display:inline-flex;
            align-items:center; justify-content:center; width:16px; height:16px;
            border-radius:50%; border:1px solid rgba(0,0,0,0.18); color:#6b7280; font-size:11px;
            background-color:#f9f9f9;
          }
          .metric-tooltip summary:hover {
            background-color:#e5e7eb; border-color:#374151;
          }
          .metric-tooltip summary::-webkit-details-marker { display:none; }
          .metric-tooltip .tooltip-card {
            position: absolute; z-index: 1000; margin-top:6px; background:#fff; 
            border:1px solid rgba(0,0,0,0.1); box-shadow:0 4px 12px rgba(0,0,0,0.1); 
            border-radius:6px; padding:10px 12px; font-size:0.875rem; color:#374151; 
            max-width:280px; line-height:1.4;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Sanitize inputs
    safe_metric = metric_name.replace("<","&lt;").replace(">","&gt;")
    safe_tooltip = tooltip_text.replace("<","&lt;").replace(">","&gt;")
    
    st.markdown(
        f"""
        <div class="metric-label">
          {safe_metric}
          <details class='metric-tooltip'>
            <summary aria-label='More information'>i</summary>
            <div class='tooltip-card'>{safe_tooltip}</div>
          </details>
        </div>
        """,
        unsafe_allow_html=True,
    )

def should_show_alert(gap, gap_percentage):
    """Determine if critical staffing alert should be shown"""
    return gap > 0 and abs(gap_percentage) >= 15  # Show alert if understaffed by 15% or more

def generate_dynamic_table_data(location, department, week, selected_dates, shifts):
    """Generate dynamic table data based on all filter selections"""
    
    # Base multipliers by location (similar to Overview section)
    location_multipliers = {
        "AZ Goodyear": 1.0,
        "IL Aurora": 0.85, 
        "AZ Phoenix": 1.2,
        "IL Lake Zurich": 0.9,
        "IL Burr Ridge": 0.75
    }
    
    # Department multipliers
    dept_multipliers = {
        "Kitchen": 1.0,
        "Production": 0.8,
        "Sanitation": 0.6,
        "Quality": 0.4,
        "Warehouse": 0.9,
        "Fulfillment": 0.7,
        "Shipping": 0.5
    }
    
    # Week variations
    week_variations = {
        "2026-W08": 1.0,
        "2026-W07": 0.95,
        "2026-W09": 1.05,
        "2026-W06": 0.9,
        "2026-W10": 1.1
    }
    
    # Get multipliers
    loc_mult = location_multipliers.get(location, 1.0)
    dept_mult = dept_multipliers.get(department, 1.0)
    week_mult = week_variations.get(week, 1.0)
    
    # Base template data - will be modified by multipliers
    base_shift_template = {
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
    }
    
    base_hc_template = {
        'FTE': 48,
        'TEMP': 30,
        'NEW HIRES': 0,
        'FLEX': 1,
        'WW/GS': 0,
        'VEH/MEH': 2,
        'PTO': 1,
        'tooltip_fte': 'Previous Week: 45\n• Change: +3',
        'tooltip_temp': 'Previous Week: 28\n• Change: +2'
    }
    
    base_attendance_template = {
        'FTE Attendance Assumption': '90%',
        'TEMP Attendance Assumption': '84%',
        'NEW HIRES Show Up Rate': '50%',
        'FLEX Show Up Rate': '50%',
        'WW/GS Show Up Rate': '100.00%',
        'VEH Show Up Rate': '80.00%',
        'tooltip_fte': 'Previous Week: 88%\n• Change: +2%',
        'tooltip_temp': 'Previous Week: 82%\n• Change: +2%'
    }
    
    # Generate dynamic data for each selected date and shift
    dynamic_shift_data = {}
    dynamic_hc_data = {}
    dynamic_attendance_data = {}
    
    for selected_date in selected_dates:
        date_str = selected_date.strftime("%Y-%m-%d")
        day_str = selected_date.strftime("%a")
        
        for shift in shifts:
            shift_num = shift[0]  # Convert "1st" to "1"
            key = f"{date_str} {day_str} Shift {shift_num}"
            
            # Apply multipliers to shift data
            shift_data = base_shift_template.copy()
            shift_data['Total Needed'] = int(shift_data['Total Needed'] * loc_mult * dept_mult * week_mult)
            shift_data['Total Expected'] = int(shift_data['Total Expected'] * loc_mult * dept_mult * week_mult)
            shift_data['Total Gap'] = shift_data['Total Expected'] - shift_data['Total Needed']
            shift_data['Total Punches'] = int(shift_data['Total Punches'] * loc_mult * dept_mult * week_mult)
            
            dynamic_shift_data[key] = shift_data
            
            # Apply multipliers to HC data
            hc_data = base_hc_template.copy()
            hc_data['FTE'] = int(hc_data['FTE'] * loc_mult * dept_mult * week_mult)
            hc_data['TEMP'] = int(hc_data['TEMP'] * loc_mult * dept_mult * week_mult)
            hc_data['FLEX'] = int(hc_data['FLEX'] * loc_mult * dept_mult * week_mult)
            
            dynamic_hc_data[key] = hc_data
            
            # Attendance data (percentages don't change much, but can vary slightly)
            attendance_data = base_attendance_template.copy()
            dynamic_attendance_data[key] = attendance_data
    
    return dynamic_shift_data, dynamic_hc_data, dynamic_attendance_data

def validate_and_adjust_totals(filtered_shift_data, overview_metrics, shifts):
    """Ensure table totals match overview metrics"""
    if not filtered_shift_data or not shifts:
        return filtered_shift_data
    
    # Calculate current table totals
    table_needed_total = sum(data['Total Needed'] for data in filtered_shift_data.values())
    table_expected_total = sum(data['Total Expected'] for data in filtered_shift_data.values())
    
    # Get target totals from overview
    target_needed = overview_metrics['needed']
    target_expected = overview_metrics['expected']
    
    # Calculate adjustment ratios
    needed_ratio = target_needed / table_needed_total if table_needed_total > 0 else 1
    expected_ratio = target_expected / table_expected_total if table_expected_total > 0 else 1
    
    # Adjust each shift's values proportionally
    adjusted_data = {}
    for key, data in filtered_shift_data.items():
        adjusted_data[key] = data.copy()
        adjusted_data[key]['Total Needed'] = int(data['Total Needed'] * needed_ratio)
        adjusted_data[key]['Total Expected'] = int(data['Total Expected'] * expected_ratio)
        adjusted_data[key]['Total Gap'] = adjusted_data[key]['Total Expected'] - adjusted_data[key]['Total Needed']
    
    return adjusted_data

def filter_employee_data_by_selections(employee_data, selected_department, week, shifts):
    """Filter employee data based on department, week, and shift selections"""
    filtered_employees = []
    
    # Convert shift format for comparison ("1st" -> "1st")
    shift_filters = shifts if shifts else ["1st", "2nd", "3rd"]
    
    for emp in employee_data:
        # Check department match
        dept_matches = (emp['Department'] == selected_department)
        
        # Check week match
        week_matches = (emp['Week'] == week)
        
        # Check shift match - extract shift from "Day/Shift" field
        day_shift = emp.get('Day/Shift', '')
        if '/' in day_shift:
            emp_shift = day_shift.split('/')[-1]  # Get "1st", "2nd", "3rd"
            shift_matches = (emp_shift in shift_filters)
        else:
            shift_matches = True  # If no shift info, include it
        
        if dept_matches and week_matches and shift_matches:
            filtered_employees.append(emp)
    
    return filtered_employees

def main():
    # Header section - matching mockup layout
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
                                         index=0, label_visibility="collapsed")  # Kitchen is first
    
    with col3:
        st.markdown("**Week**")
        week = st.selectbox("", ["2026-W08", "2026-W07", "2026-W09", "2026-W06", "2026-W10"], 
                           index=0, label_visibility="collapsed")
    
    with col4:
        st.markdown("**Date**")
        # Allow multiple date selection
        available_dates = [
            pd.to_datetime("2026-02-12"),
            pd.to_datetime("2026-02-13"), 
            pd.to_datetime("2026-02-14"),
            pd.to_datetime("2026-02-15"),
            pd.to_datetime("2026-02-16")
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
    
    # Calculate dynamic metrics based on filter selections
    primary_date = selected_dates[0] if selected_dates else pd.to_datetime("2026-02-12")
    metrics = calculate_dynamic_metrics(location, selected_department, week, primary_date, shifts)
    gap_status, gap_class, gap_color = get_gap_status_info(metrics["gap"], metrics["gap_percentage"])
    show_alert = should_show_alert(metrics["gap"], metrics["gap_percentage"])
    
    # Generate dynamic data that actually varies by filters
    if selected_dates and shifts:
        filtered_shift_data, filtered_hc_data, filtered_attendance_data = generate_dynamic_table_data(
            location, selected_department, week, selected_dates, shifts
        )
        
        # Adjust shift data to match overview totals
        filtered_shift_data = validate_and_adjust_totals(filtered_shift_data, metrics, shifts)
        
        # Filter employees
        filtered_employees = filter_employee_data_by_selections(
            st.session_state.employee_data, selected_department, week, shifts
        )
    else:
        # Empty data if no selections
        filtered_shift_data = {}
        filtered_hc_data = {}
        filtered_attendance_data = {}
        filtered_employees = []
    
    # Weekly Overview section
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    
    # Key metrics row - All three KPIs: Needed HC, Expected HC, Gap in HC
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_with_tooltip("Needed HC", "Target HC to fulfill orders")
        st.markdown(f'<div class="metric-large">{metrics["needed"]}</div>', unsafe_allow_html=True)
        
        # Dynamic change indicator
        change_symbol = "↗️" if metrics["needed_change"] >= 0 else "↘️"
        change_class = "metric-change-up" if metrics["needed_change"] >= 0 else "metric-change-down"
        st.markdown(f'<div class="metric-change {change_class}">{change_symbol} {abs(metrics["needed_change"])}% vs last week</div>', unsafe_allow_html=True)
    
    with col2:
        render_metric_with_tooltip("Expected HC", "Scheduled x Attendance Assumption")
        st.markdown(f'<div class="metric-large">{metrics["expected"]}</div>', unsafe_allow_html=True)
        
        # Dynamic change indicator  
        change_symbol = "↗️" if metrics["expected_change"] >= 0 else "↘️"
        change_class = "metric-change-up" if metrics["expected_change"] >= 0 else "metric-change-down"
        st.markdown(f'<div class="metric-change {change_class}">{change_symbol} {abs(metrics["expected_change"])}% vs last week</div>', unsafe_allow_html=True)
    
    with col3:
        render_metric_with_tooltip("Gap in HC", "Expected - Needed")
        st.markdown(f'<div class="{gap_class}">{abs(metrics["gap"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gap-status" style="color: {gap_color};">{gap_status}</div>', unsafe_allow_html=True)
        
        # Conditional warning alert - only shown for critical understaffing
        if show_alert:
            st.markdown("""
            <div class="alert-warning">
                ⚠️ <strong>Alert:</strong> Critical staffing shortage detected. Immediate action required.
            </div>
            """, unsafe_allow_html=True)
        
    # Department Details section
    st.markdown('<div class="section-header">Department Details</div>', unsafe_allow_html=True)
    
    # Three toggle buttons with built-in highlighting
    view_options = ["📊 Shift Summary", "👥 Roster HC Summary", "📈 Attendance Assumption"]
    
    # Use radio directly and let it manage the state
    selected_option = st.radio(
        label="Select View:",
        options=view_options,
        horizontal=True,
        label_visibility="collapsed",
        key="view_selector"
    )
    
    # Map radio selection to view names for the display logic
    view_mapping = {
        "📊 Shift Summary": "Shift Summary",
        "👥 Roster HC Summary": "Roster HC Summary", 
        "📈 Attendance Assumption": "Attendance Assumption"
    }
    
    # Get the current view from radio selection
    current_view = view_mapping[selected_option]
    
    # Display selected view with exact tables and tooltips
    if current_view == "Shift Summary":
        st.markdown("#### Shift Summary")
        st.markdown("*Hover over cells to see detailed breakdowns and comparisons*")
        
        # Create HTML table with tooltips instead of Plotly
        html_table = create_shift_summary_html_table_with_tooltips(filtered_shift_data)
        st.components.v1.html(html_table, height=400)
        
    elif current_view == "Roster HC Summary":
        st.markdown("#### Roster HC Summary")
        st.markdown("*Hover over cells to see detailed breakdowns and comparisons*")
        
        # Create HTML table with tooltips instead of Plotly
        html_table = create_roster_hc_html_table_with_tooltips(filtered_hc_data)
        st.components.v1.html(html_table, height=400)
    
    else:  # Attendance Assumption
        st.markdown("#### Attendance Assumption")
        st.markdown("*Hover over cells to see detailed breakdowns and comparisons*")
        
        # Create HTML table with tooltips instead of Plotly
        html_table = create_attendance_html_table_with_tooltips(filtered_attendance_data)
        st.components.v1.html(html_table, height=400)
    
    st.markdown('<div class="section-header">Roster Details</div>', unsafe_allow_html=True)
    gap = st.session_state.departments[selected_department]
    if gap < 0:
        st.error(f"⚠️ {selected_department} is understaffed by {abs(gap)} people")
                    
                    hc_summary_df = pd.DataFrame([
                        ['FTE', hc_entry['FTE']],
                        ['TEMP', hc_entry['TEMP']],
                        ['NEW HIRES', hc_entry['NEW HIRES']],
                        ['FLEX', hc_entry['FLEX']],
                        ['WW/GS', hc_entry['WW/GS']],
                        ['VEH/MEH', hc_entry['VEH/MEH']],
                        ['PTO', hc_entry['PTO']]
                    ], columns=['Worker Type', 'Count'])
                    
                    st.dataframe(hc_summary_df, hide_index=True, use_container_width=True)
                
                with col2:
                    st.markdown(f"**Shift {hc_entry['Shift']} - Changes vs Last Week**")
                    
                    changes_df = pd.DataFrame([
                        ['FTE', hc_entry['FTE_change']],
                        ['TEMP', hc_entry['TEMP_change']],
                        ['NEW HIRES', hc_entry['NEWHIRES_change']],
                        ['FLEX', hc_entry['FLEX_change']],
                        ['WW/GS', hc_entry['WWGS_change']],
                        ['VEH/MEH', hc_entry['VEHMEH_change']],
                        ['PTO', hc_entry['PTO_change']]
                    ], columns=['Worker Type', 'Change'])
                    
                    st.dataframe(changes_df, hide_index=True, use_container_width=True)
                
                st.markdown("---")
    
    else:  # Attendance Assumption
        st.markdown("#### Attendance Assumption")
        st.markdown("*Hover over cells to see detailed breakdowns and comparisons*")
        
        # Create HTML table with tooltips instead of Plotly
        html_table = create_attendance_html_table_with_tooltips(filtered_attendance_data)
        st.components.v1.html(html_table, height=400)
    
    st.markdown('<div class="section-header">Roster Details</div>', unsafe_allow_html=True)
    gap = st.session_state.departments[selected_department]
    if gap < 0:
        st.error(f"⚠️ {selected_department} is understaffed by {abs(gap)} people")
    elif gap > 0:
        st.success(f"✅ {selected_department} has {gap} extra people")
    else:
        st.info(f"✅ {selected_department} staffing is balanced")
    
    # Employee details table with exact columns and tooltips
    st.markdown(f"#### {selected_department} Employee List")
    st.markdown("*Detailed employee roster for filtered department*")
    
    fig = create_employee_details_table_with_tooltips(selected_department, filtered_employees)
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






















