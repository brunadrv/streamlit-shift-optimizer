# Streamlit app for real-time workforce dashboard
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Workforce Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for styling
st.markdown("""
<style>
/* Global styles */
.main > div {
    padding-top: 2rem;
}

/* Overview pills styling */
.metric-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
    line-height: 1;
}

.metric-label {
    font-size: 0.9rem;
    margin-top: 0.5rem;
    opacity: 0.9;
}

.metric-change {
    font-size: 0.75rem;
    margin-top: 0.25rem;
    opacity: 0.8;
}

/* Gap specific styling */
.gap-negative {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
}

.gap-positive {
    background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
}

/* Section headers */
.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2E4057;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #667eea;
}

/* View toggle buttons */
.view-toggle {
    display: flex;
    background: #f1f3f4;
    border-radius: 8px;
    padding: 4px;
    margin: 1rem 0;
    gap: 2px;
}

.view-button {
    flex: 1;
    padding: 8px 16px;
    text-align: center;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: #666;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.view-button.active {
    background: white;
    color: #2E4057;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.view-button:hover {
    background: #e8eaed;
}

.view-button.active:hover {
    background: white;
}

/* Legend styling */
.legend-container {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
    font-size: 0.9rem;
}

.legend-item {
    display: inline-block;
    margin-right: 15px;
    padding: 3px 8px;
    border-radius: 3px;
}

.legend-negative {
    background-color: #ffcccc;
}

.legend-positive {
    background-color: #ccffcc;
}

/* Plotly table overrides */
.js-plotly-plot .plotly .main-svg {
    border-radius: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
    .metric-container {
        height: 100px;
    }
    
    .metric-value {
        font-size: 2rem;
    }
    
    .section-header {
        font-size: 1.25rem;
    }
}
</style>
""", unsafe_allow_html=True)

# CENTRALIZED DATA MANAGEMENT - keeping only the data layer fix
@st.cache_data
def initialize_master_data():
    """Initialize the master workforce dataset - single source of truth"""
    return {
        'Kitchen': {
            '2026-02-12': {
                'Thu Shift 1': {
                    'headcount': {'FTE': 22, 'TEMP': 12, 'NEW HIRES': 0, 'FLEX': 2, 'WW/GS': 0, 'VEH/MEH': 3, 'PTO': 2, 'VER/MTO': 0},
                    'attendance': {'FTE': 85, 'TEMP': 75, 'NEW HIRES': 50, 'FLEX': 50, 'WW/GS': 100, 'VEH/MEH': 70, 'PTO': 50, 'VER/MTO': 50},
                    'expected': 26, 'needed': 91, 'gap': -12, 'punches': 106
                },
                'Thu Shift 2': {
                    'headcount': {'FTE': 20, 'TEMP': 11, 'NEW HIRES': 0, 'FLEX': 1, 'WW/GS': 0, 'VEH/MEH': 2, 'PTO': 1, 'VER/MTO': 0},
                    'attendance': {'FTE': 85, 'TEMP': 75, 'NEW HIRES': 50, 'FLEX': 50, 'WW/GS': 100, 'VEH/MEH': 70, 'PTO': 50, 'VER/MTO': 50},
                    'expected': 25, 'needed': 86, 'gap': -13, 'punches': 88
                },
                'Thu Shift 3': {
                    'headcount': {'FTE': 15, 'TEMP': 7, 'NEW HIRES': 0, 'FLEX': 1, 'WW/GS': 0, 'VEH/MEH': 1, 'PTO': 1, 'VER/MTO': 0},
                    'attendance': {'FTE': 85, 'TEMP': 75, 'NEW HIRES': 50, 'FLEX': 50, 'WW/GS': 100, 'VEH/MEH': 70, 'PTO': 50, 'VER/MTO': 50},
                    'expected': 18, 'needed': 15, 'gap': 3, 'punches': 0
                }
            },
            '2026-02-13': {
                'Fri Shift 1': {
                    'headcount': {'FTE': 48, 'TEMP': 30, 'NEW HIRES': 0, 'FLEX': 1, 'WW/GS': 0, 'VEH/MEH': 2, 'PTO': 1, 'VER/MTO': 0},
                    'attendance': {'FTE': 93, 'TEMP': 60, 'NEW HIRES': 50, 'FLEX': 50, 'WW/GS': 100, 'VEH/MEH': 80, 'PTO': 50, 'VER/MTO': 50},
                    'expected': 83, 'needed': 79, 'gap': 4, 'punches': 91
                },
                'Fri Shift 2': {
                    'headcount': {'FTE': 58, 'TEMP': 15, 'NEW HIRES': 0, 'FLEX': 0, 'WW/GS': 0, 'VEH/MEH': 0, 'PTO': 0, 'VER/MTO': 0},
                    'attendance': {'FTE': 86, 'TEMP': 78, 'NEW HIRES': 50, 'FLEX': 50, 'WW/GS': 100, 'VEH/MEH': 80, 'PTO': 50, 'VER/MTO': 50},
                    'expected': 53, 'needed': 65, 'gap': -12, 'punches': 101
                },
                'Fri Shift 3': {
                    'headcount': {'FTE': 12, 'TEMP': 7, 'NEW HIRES': 0, 'FLEX': 0, 'WW/GS': 0, 'VEH/MEH': 0, 'PTO': 0, 'VER/MTO': 0},
                    'attendance': {'FTE': 84, 'TEMP': 100, 'NEW HIRES': 50, 'FLEX': 50, 'WW/GS': 100, 'VEH/MEH': 80, 'PTO': 50, 'VER/MTO': 50},
                    'expected': 17, 'needed': 13, 'gap': 4, 'punches': 0
                }
            }
        }
    }

def generate_legacy_data_structures():
    """Generate the old data structures from master dataset for backward compatibility"""
    master_data = initialize_master_data()
    
    # Generate shift_summary_transposed
    st.session_state.shift_summary_transposed = {}
    # Generate weekly_hc_details_transposed  
    st.session_state.weekly_hc_details_transposed = {}
    # Generate attendance_assumptions_transposed
    st.session_state.attendance_assumptions_transposed = {}
    
    for dept, dept_data in master_data.items():
        for date, date_data in dept_data.items():
            for shift_name, shift_data in date_data.items():
                key = f'{date} {shift_name}'
                
                # Populate shift summary
                st.session_state.shift_summary_transposed[key] = {
                    'Total Needed': shift_data['needed'],
                    'Total Expected': shift_data['expected'],
                    'Total Gap': shift_data['gap'],
                    'Total Attendance Assumption': f"{shift_data['attendance']['FTE']}%",
                    'Total Punches': shift_data['punches'],
                    'tooltip_needed': '• Dynamic from master data',
                    'tooltip_expected': f'Previous Week: {shift_data["expected"]-2}\n• Change: +2',
                    'tooltip_gap': f'Previous Week: {shift_data["gap"]+1}\n• Change: -1',
                    'tooltip_attendance': f'Previous Week: {shift_data["attendance"]["FTE"]-2}%\n• Change: +2%',
                    'tooltip_punches': f'Previous Week: {shift_data["punches"]-3}\n• Change: +3'
                }
                
                # Populate headcount details
                st.session_state.weekly_hc_details_transposed[key] = shift_data['headcount'].copy()
                
                # Populate attendance assumptions
                st.session_state.attendance_assumptions_transposed[key] = {
                    'FTE Attendance Assumption': f"{shift_data['attendance']['FTE']}%",
                    'TEMP Attendance Assumption': f"{shift_data['attendance']['TEMP']}%",
                    'NEW HIRES Show Up Rate': f"{shift_data['attendance']['NEW HIRES']}%",
                    'FLEX Show Up Rate': f"{shift_data['attendance']['FLEX']}%",
                    'WW/GS Show Up Rate': f"{shift_data['attendance']['WW/GS']}%",
                    'VEH Show Up Rate': f"{shift_data['attendance']['VEH/MEH']}%",
                    'VER/MTO Show Up Rate': f"{shift_data['attendance']['VER/MTO']}%",
                }

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
    
    # Department expected HC values
    st.session_state.department_expected_hc = {
        'Kitchen': 69,
        'Production': 45,
        'Sanitation': 25,
        'Quality': 15,
        'Warehouse': 30,
        'Fulfillment': 20,
        'Shipping': 35
    }

# Generate legacy structures from master data
generate_legacy_data_structures()

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

def create_transposed_shift_summary_table_with_tooltips(filtered_data=None):
    """Create transposed shift summary table matching the screenshot structure"""
    
    # Use filtered data if provided, otherwise use all data
    data_to_use = filtered_data if filtered_data else st.session_state.shift_summary_transposed
    
    # Prepare the transposed structure
    columns = list(data_to_use.keys())
    rows = ['Total Needed', 'Total Expected', 'Total Gap', 'Total Attendance Assumption', 'Total Punches']
    
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
        margin=dict(l=0, r=0, t=20, b=0),
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
        margin=dict(l=0, r=0, t=20, b=0),
        title="HC Details - Hover over values to see details"
    )
    
    return fig

def create_transposed_attendance_assumptions_table(filtered_data=None):
    """Create transposed attendance assumptions table matching the screenshot structure"""
    
    # Use filtered data if provided, otherwise use all data
    data_to_use = filtered_data if filtered_data else st.session_state.attendance_assumptions_transposed
    
    # Prepare the transposed structure
    columns = list(data_to_use.keys())
    rows = ['FTE Attendance Assumption', 'TEMP Attendance Assumption', 'NEW HIRES Show Up Rate', 'FLEX Show Up Rate', 'WW/GS Show Up Rate', 'VEH Show Up Rate']
    
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
            values=[rows] + 
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
        margin=dict(l=0, r=0, t=20, b=0),
        title="Attendance Assumptions - Hover over values to see details"
    )
    
    return fig

# MAIN STREAMLIT APP - RESTORING ORIGINAL UI
st.title("🏭 Real-Time Workforce Dashboard")

# Sidebar filters - ORIGINAL STRUCTURE
with st.sidebar:
    st.header("🔧 Filters")
    
    # Location filter
    location_options = ["AZ Goodyear", "IL Aurora", "AZ Phoenix", "IL Lake Zurich", "IL Burr Ridge"]
    selected_location = st.selectbox("📍 Location", location_options, index=0)
    
    # Department filter  
    department_options = list(st.session_state.departments.keys())
    selected_department = st.selectbox("🏢 Department", department_options, index=0)
    
    # Week filter
    week_options = ["2026-W08", "2026-W07", "2026-W06"]
    selected_week = st.selectbox("📅 Week", week_options, index=0)
    
    # Date filter
    selected_date = st.date_input("📅 Date", value=datetime(2026, 2, 12))
    
    # Shift filter
    shift_options = ["All", "1st", "2nd", "3rd"] 
    selected_shifts = st.multiselect("⏰ Shift", shift_options, default=["All"])

# Calculate metrics - ORIGINAL
metrics = calculate_metrics()

# Overview Section - ORIGINAL PILLS
st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)

# Key metrics row - ORIGINAL LAYOUT
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">100</div>
        <div class="metric-label">Needed HC</div>
        <div class="metric-change">📊 5% vs last week</div>
    </div>
    """, unsafe_allow_html=True)

with col2: 
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">69</div>
        <div class="metric-label">Expected HC</div>
        <div class="metric-change">📈 20% vs last week</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    gap_class = "gap-negative" if metrics['gap'] < 0 else "gap-positive"
    st.markdown(f"""
    <div class="metric-container {gap_class}">
        <div class="metric-value">31</div>
        <div class="metric-label">Gap in HC</div>
        <div class="metric-change">{"📉" if metrics['gap'] < 0 else "📈"} 3% vs last week</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">79</div>
        <div class="metric-label">Total Punches</div>
        <div class="metric-change">📊 4% vs last week</div>
    </div>
    """, unsafe_allow_html=True)

# Department Expected HC Section - ORIGINAL TABLE VIEWS
department_expected = st.session_state.department_expected_hc[selected_department]
st.markdown(f'<div class="section-header">{selected_department} Expected HC ({department_expected})</div>', unsafe_allow_html=True)

# View toggle - ORIGINAL 4-BUTTON DESIGN
st.markdown("""
<div class="view-toggle">
    <button class="view-button active" onclick="setView('Shift Summary')">Shift Summary</button>
    <button class="view-button" onclick="setView('Weekly Expected HC Details')">Weekly Expected HC Details</button>
    <button class="view-button" onclick="setView('Attendance Assumption')">Attendance Assumption</button>
    <button class="view-button" onclick="setView('Employee List')">Employee List</button>
</div>

<script>
function setView(view) {
    // Remove active class from all buttons
    document.querySelectorAll('.view-button').forEach(btn => btn.classList.remove('active'));
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // This would typically trigger a Streamlit rerun with the new view
    console.log('View changed to:', view);
}
</script>
""", unsafe_allow_html=True)

# Show content based on current view - ORIGINAL STRUCTURE
current_view = st.session_state.get('current_view', 'Shift Summary')

if current_view == "Shift Summary":
    # Legend
    st.markdown("""
    <div class="legend-container">
        <strong>Legend:</strong>
        <span class="legend-item legend-negative">>20% variance from last week</span>
        <span class="legend-item legend-positive">10-20% variance from last week</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Display shift summary table
    fig = create_transposed_shift_summary_table_with_tooltips()
    st.plotly_chart(fig, use_container_width=True)

elif current_view == "Weekly Expected HC Details":
    # Display HC details table
    fig = create_weekly_hc_details_table_with_tooltips()
    st.plotly_chart(fig, use_container_width=True)

elif current_view == "Attendance Assumption":
    # Display attendance assumptions table  
    fig = create_transposed_attendance_assumptions_table()
    st.plotly_chart(fig, use_container_width=True)

else:  # Employee List
    # Employee data table
    df = pd.DataFrame(st.session_state.employee_data)
    st.dataframe(df, use_container_width=True)