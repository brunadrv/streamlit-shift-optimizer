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
    
    # Weekly Expected HC Details: Transposed structure with Date, Week Day, Shift, FTE, TEMP, NEW HIRES, FLEX, WW/GS, VEH/MEH, PTO as ROWS
    st.session_state.weekly_hc_details_transposed = {
        '2026-02-12 Thu Shift 1': {
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 1',
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
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 2',
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
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 3',
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
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 1',
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
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 2',
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
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 3',
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
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 1',
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
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 2',
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
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 3',
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
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 1',
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
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 2',
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
            'Date': '2026-02-12',
            'Week Day': 'Thu',
            'Shift': 'Shift 3',
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
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 1',
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
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 2',
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
            'Date': '2026-02-13',
            'Week Day': 'Fri',
            'Shift': 'Shift 3',
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
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 1',
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
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 2',
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
            'Date': '2026-02-14',
            'Week Day': 'Sat',
            'Shift': 'Shift 3',
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
            font=dict(size=12, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=[['Date', 'Week Day', 'Shift', 'Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']] + 
                   [[st.session_state.shift_summary_transposed[col][row] for row in rows] for col in columns],
            fill_color=[['#f9f9f9'] * len(rows)] + 
                      [[get_cell_color(col, row, st.session_state.shift_summary_transposed[col][row]) for row in rows] for col in columns],
            align='center',
            font=dict(size=12),
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

def create_transposed_hc_details_table_with_tooltips():
    """Create transposed HC details table matching the screenshot structure"""
    
    # Prepare the transposed structure
    columns = list(st.session_state.weekly_hc_details_transposed.keys())
    rows = ['Date', 'Week Day', 'Shift', 'FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'WW/GS', 'VEH/MEH', 'PTO']
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Row Labels'] + columns,
            fill_color='#f1f1f1',
            align='center',
            font=dict(size=12, color='#2E4057'),
            height=30
        ),
        cells=dict(
            values=[['Date', 'Week Day', 'Shift', 'FTE', 'TEMP', 'NEW HIRES', 'FLEX', 'WW/GS', 'VEH/MEH', 'PTO']] + 
                   [[st.session_state.weekly_hc_details_transposed[col][row] for row in rows] for col in columns],
            fill_color=[['#f9f9f9'] * len(rows)] + 
                      [[get_hc_cell_color(col, row, st.session_state.weekly_hc_details_transposed[col][row]) for row in rows] for col in columns],
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

def create_transposed_attendance_assumptions_table():
    """Create transposed attendance assumptions table matching the screenshot structure - UPDATED TO USE TRANSPOSED VERSION"""
    
    # Prepare the transposed structure
    columns = list(st.session_state.attendance_assumptions_transposed.keys())
    rows = ['Date', 'Week Day', 'Shift', 'FTE Attendance Assumption', 'TEMP Attendance Assumption', 'NEW HIRES Show Up Rate', 'FLEX Show Up Rate', 'WW/GS Show Up Rate', 'VEH Show Up Rate']
    
    def get_tooltip_for_cell(col, row):
        """Get tooltip for each cell based on column and row"""
        data = st.session_state.attendance_assumptions_transposed[col]
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
            value = st.session_state.attendance_assumptions_transposed[col][row]
            col_values.append(value)
            col_colors.append(get_attendance_cell_color(col, row, value))
        cell_values.append(col_values)
        cell_colors.append(col_colors)
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[''] + columns,  # Empty first header for row labels column
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
        margin=dict(l=0, r=0, t=20, b=0),
        title="Attendance Assumptions - Transposed View"
    )
    
    return fig

def get_attendance_cell_color(col, row, value):
    """Get appropriate cell color based on value and type for attendance assumptions"""
    # Color coding based on screenshot - red highlighting for certain low values
    if row == 'TEMP Attendance Assumption' and value == '60%':
        return '#ffebee'  # Light red for low TEMP attendance (as shown in screenshot)
    elif row == 'NEW HIRES Show Up Rate' and value == '50%':
        return '#ffebee'  # Light red for NEW HIRES show up rate
    elif row == 'FLEX Show Up Rate' and value == '50%':
        return '#ffebee'  # Light red for FLEX show up rate
    return 'white'

def get_hc_cell_color(col, row, value):
    """Get appropriate cell color based on value and type for HC details"""
    if row == 'PTO' and value == 1:
        return '#ffebee'  # Light red for PTO (as shown in screenshot)
    elif row == 'VEH/MEH' and value == 2:
        return '#e8f5e8'  # Light green for VEH/MEH (as shown in screenshot)
    return 'white'

def create_weekly_hc_details_table_with_tooltips():
    """Create weekly HC details table with exact columns and tooltips - UPDATED TO USE TRANSPOSED VERSION"""
    return create_transposed_hc_details_table_with_tooltips()

def create_attendance_assumptions_table_with_tooltips():
    """Create attendance assumptions table with exact columns and tooltips - UPDATED TO USE TRANSPOSED VERSION"""
    return create_transposed_attendance_assumptions_table()

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

def should_show_alert(gap, gap_percentage):
    """Determine if critical staffing alert should be shown"""
    return gap > 0 and abs(gap_percentage) >= 15  # Show alert if understaffed by 15% or more

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
        selected_date = st.date_input("", value=pd.to_datetime("2026-02-12"), label_visibility="collapsed") 
    
    with col5:
        st.markdown("**Shift**")
        shifts = st.multiselect("", ["1st", "2nd", "3rd"], 
                               default=["1st", "2nd", "3rd"], label_visibility="collapsed") 
    
    # Calculate dynamic metrics based on filter selections
    metrics = calculate_dynamic_metrics(location, selected_department, week, selected_date, shifts)
    gap_status, gap_class, gap_color = get_gap_status_info(metrics["gap"], metrics["gap_percentage"])
    show_alert = should_show_alert(metrics["gap"], metrics["gap_percentage"])
    
    # Weekly Overview section
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    
    # Key metrics row - All three KPIs: Needed HC, Expected HC, Gap in HC
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-label">Needed HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-large">{metrics["needed"]}</div>', unsafe_allow_html=True)
        
        # Dynamic change indicator
        change_symbol = "↗️" if metrics["needed_change"] >= 0 else "↘️"
        change_class = "metric-change-up" if metrics["needed_change"] >= 0 else "metric-change-down"
        st.markdown(f'<div class="metric-change {change_class}">{change_symbol} {abs(metrics["needed_change"])}% vs last week</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Target HC to fulfill orders</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Expected HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-large">{metrics["expected"]}</div>', unsafe_allow_html=True)
        
        # Dynamic change indicator  
        change_symbol = "↗️" if metrics["expected_change"] >= 0 else "↘️"
        change_class = "metric-change-up" if metrics["expected_change"] >= 0 else "metric-change-down"
        st.markdown(f'<div class="metric-change {change_class}">{change_symbol} {abs(metrics["expected_change"])}% vs last week</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Scheduled x Attendance Assumption</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-label">Gap in HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{gap_class}">{abs(metrics["gap"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gap-status" style="color: {gap_color};">{gap_status}</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.9rem; color: #666;">Expected - Needed</div>', unsafe_allow_html=True)
        
        # Conditional warning alert - only shown for critical understaffing
        if show_alert:
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

    
    # Department Details section
    st.markdown('<div class="section-header">Department Details</div>', unsafe_allow_html=True)
    
    # Three toggle buttons with built-in highlighting (removed Roster HC Details)
    view_options = ["📊 Shift Summary", "👥 Roster HC Summary", "📈 Attendance Assumption"]
    
    # Use radio directly and let it manage the state
    selected_option = st.radio(
        label="Select View:",
        options=view_options,
        horizontal=True,
        label_visibility="collapsed",
        key="view_selector"
    )
    
    # Map radio selection to view names for the display logic (removed Roster HC Details)
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
        st.markdown("*Hover over numbers to see detailed breakdowns and comparisons*")
        
        fig = create_transposed_shift_summary_table_with_tooltips()
        st.plotly_chart(fig, use_container_width=True)
    
    elif current_view == "Roster HC Summary":
        st.markdown("#### Roster HC Summary")
        st.markdown("*Hover over numbers to see detailed breakdowns and comparisons*")
        
        # Use the transposed HC Details table for Roster HC Summary
        fig = create_transposed_hc_details_table_with_tooltips()
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Attendance Assumption
        st.markdown("#### Attendance Assumption")
        st.plotly_chart(create_transposed_attendance_assumptions_table(), use_container_width=True)
    
    
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
    st.markdown("*Detailed employee roster with exact columns from mockup*")
    
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
















