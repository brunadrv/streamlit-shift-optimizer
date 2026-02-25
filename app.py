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
    
    # COMPREHENSIVE MASTER DATASET - Single source of truth
    st.session_state.master_data = {
        # Location -> Department -> Week -> Date -> Shift -> Data
        "AZ Goodyear": {
            "Kitchen": {
                "2026-W08": {
                    datetime(2026, 2, 19): {  # Thursday
                        "1st": {"needed": 35, "expected": 26, "punches": 28, "fte": 22, "temp": 12, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 3, "pto": 2, "fte_att": 85, "temp_att": 75},
                        "2nd": {"needed": 33, "expected": 25, "punches": 26, "fte": 20, "temp": 11, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 85, "temp_att": 75},
                        "3rd": {"needed": 22, "expected": 18, "punches": 19, "fte": 15, "temp": 7, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 85, "temp_att": 75}
                    },
                    datetime(2026, 2, 20): {  # Friday
                        "1st": {"needed": 40, "expected": 33, "punches": 35, "fte": 25, "temp": 15, "new_hires": 1, "flex": 2, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 90, "temp_att": 80},
                        "2nd": {"needed": 38, "expected": 30, "punches": 32, "fte": 22, "temp": 13, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 2, "fte_att": 88, "temp_att": 78},
                        "3rd": {"needed": 20, "expected": 16, "punches": 18, "fte": 12, "temp": 8, "new_hires": 0, "flex": 0, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 82, "temp_att": 85}
                    },
                    datetime(2026, 2, 21): {  # Saturday  
                        "1st": {"needed": 42, "expected": 35, "punches": 37, "fte": 28, "temp": 16, "new_hires": 0, "flex": 3, "wwgs": 1, "veh": 4, "pto": 2, "fte_att": 92, "temp_att": 76},
                        "2nd": {"needed": 35, "expected": 32, "punches": 33, "fte": 25, "temp": 12, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 3, "pto": 1, "fte_att": 91, "temp_att": 71},
                        "3rd": {"needed": 18, "expected": 15, "punches": 16, "fte": 11, "temp": 6, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 88, "temp_att": 72}
                    },
                    datetime(2026, 2, 22): {  # Sunday  
                        "1st": {"needed": 30, "expected": 25, "punches": 27, "fte": 20, "temp": 10, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 88, "temp_att": 78},
                        "2nd": {"needed": 28, "expected": 22, "punches": 24, "fte": 18, "temp": 8, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 86, "temp_att": 76},
                        "3rd": {"needed": 15, "expected": 12, "punches": 13, "fte": 10, "temp": 4, "new_hires": 0, "flex": 0, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 84, "temp_att": 74}
                    },
                    datetime(2026, 2, 23): {  # Monday  
                        "1st": {"needed": 45, "expected": 38, "punches": 40, "fte": 30, "temp": 18, "new_hires": 1, "flex": 3, "wwgs": 0, "veh": 3, "pto": 2, "fte_att": 90, "temp_att": 82},
                        "2nd": {"needed": 42, "expected": 35, "punches": 37, "fte": 28, "temp": 15, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 3, "pto": 2, "fte_att": 89, "temp_att": 80},
                        "3rd": {"needed": 25, "expected": 20, "punches": 22, "fte": 16, "temp": 9, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 87, "temp_att": 78}
                    },
                    datetime(2026, 2, 24): {  # Tuesday  
                        "1st": {"needed": 44, "expected": 37, "punches": 39, "fte": 29, "temp": 17, "new_hires": 0, "flex": 3, "wwgs": 0, "veh": 3, "pto": 2, "fte_att": 91, "temp_att": 83},
                        "2nd": {"needed": 41, "expected": 34, "punches": 36, "fte": 27, "temp": 14, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 3, "pto": 2, "fte_att": 90, "temp_att": 81},
                        "3rd": {"needed": 24, "expected": 19, "punches": 21, "fte": 15, "temp": 8, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 88, "temp_att": 79}
                    },
                    datetime(2026, 2, 25): {  # Wednesday  
                        "1st": {"needed": 40, "expected": 33, "punches": 35, "fte": 26, "temp": 15, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 3, "pto": 2, "fte_att": 89, "temp_att": 80},
                        "2nd": {"needed": 37, "expected": 30, "punches": 32, "fte": 24, "temp": 12, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 2, "pto": 2, "fte_att": 88, "temp_att": 78},
                        "3rd": {"needed": 20, "expected": 16, "punches": 18, "fte": 13, "temp": 6, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 86, "temp_att": 76}
                    }
                },
                "2026-W07": {
                    datetime(2026, 2, 12): {  # Thursday  
                        "1st": {"needed": 32, "expected": 24, "punches": 26, "fte": 20, "temp": 10, "new_hires": 1, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 83, "temp_att": 73},
                        "2nd": {"needed": 30, "expected": 23, "punches": 24, "fte": 18, "temp": 9, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 83, "temp_att": 73},
                        "3rd": {"needed": 20, "expected": 15, "punches": 16, "fte": 12, "temp": 5, "new_hires": 0, "flex": 0, "wwgs": 0, "veh": 1, "pto": 0, "fte_att": 83, "temp_att": 73}
                    }
                }
            },
            "Production": {
                "2026-W08": {
                    datetime(2026, 2, 19): {
                        "1st": {"needed": 25, "expected": 20, "punches": 22, "fte": 15, "temp": 8, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 85, "temp_att": 75},
                        "2nd": {"needed": 23, "expected": 18, "punches": 20, "fte": 13, "temp": 7, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 85, "temp_att": 75},
                        "3rd": {"needed": 15, "expected": 12, "punches": 13, "fte": 10, "temp": 5, "new_hires": 0, "flex": 0, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 85, "temp_att": 75}
                    }
                }
            }
        },
        "IL Aurora": {
            "Kitchen": {
                "2026-W08": {
                    datetime(2026, 2, 19): {
                        "1st": {"needed": 28, "expected": 22, "punches": 24, "fte": 18, "temp": 10, "new_hires": 0, "flex": 2, "wwgs": 0, "veh": 2, "pto": 1, "fte_att": 88, "temp_att": 78},
                        "2nd": {"needed": 26, "expected": 20, "punches": 22, "fte": 16, "temp": 8, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 86, "temp_att": 76},
                        "3rd": {"needed": 18, "expected": 14, "punches": 16, "fte": 12, "temp": 5, "new_hires": 0, "flex": 1, "wwgs": 0, "veh": 1, "pto": 1, "fte_att": 84, "temp_att": 74}
                    }
                }
            }
        }
    }
    
    # Employee data
    st.session_state.employee_data = [
        # Kitchen Department - AZ Goodyear
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '1st', 'Location': 'AZ Goodyear', 'Worker Type': 'FTE', 'Employee ID': 'EMP001', 'Employee Name': 'John Smith', 'Hire Date': '2023-01-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '1st', 'Location': 'AZ Goodyear', 'Worker Type': 'FTE', 'Employee ID': 'EMP002', 'Employee Name': 'Mary Davis', 'Hire Date': '2022-08-20', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '1st', 'Location': 'AZ Goodyear', 'Worker Type': 'TEMP', 'Employee ID': 'TMP101', 'Employee Name': 'Mike Wilson', 'Hire Date': '2026-02-01', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '2nd', 'Location': 'AZ Goodyear', 'Worker Type': 'FTE', 'Employee ID': 'EMP003', 'Employee Name': 'Lisa Brown', 'Hire Date': '2021-12-10', 'Workday Schedule': '14:00-22:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 20), 'Shift': '1st', 'Location': 'AZ Goodyear', 'Worker Type': 'FTE', 'Employee ID': 'EMP004', 'Employee Name': 'Carlos Rodriguez', 'Hire Date': '2023-11-08', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'Sarah Johnson', 'Roster Bucket': 'Active'},
        
        # Production Department - AZ Goodyear
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '1st', 'Location': 'AZ Goodyear', 'Worker Type': 'FTE', 'Employee ID': 'PRD001', 'Employee Name': 'James Wilson', 'Hire Date': '2023-03-22', 'Workday Schedule': '06:00-14:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '2nd', 'Location': 'AZ Goodyear', 'Worker Type': 'TEMP', 'Employee ID': 'TMP201', 'Employee Name': 'Kevin Chen', 'Hire Date': '2026-01-15', 'Workday Schedule': '14:00-22:00', 'Department': 'Production', 'Manager': 'Michael Thompson', 'Roster Bucket': 'Active'},
        
        # Kitchen Department - IL Aurora
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '1st', 'Location': 'IL Aurora', 'Worker Type': 'FTE', 'Employee ID': 'IL001', 'Employee Name': 'Anna Martinez', 'Hire Date': '2022-06-15', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'David Rodriguez', 'Roster Bucket': 'Active'},
        {'Week': '2026-W08', 'Date': datetime(2026, 2, 19), 'Shift': '1st', 'Location': 'IL Aurora', 'Worker Type': 'TEMP', 'Employee ID': 'IL101', 'Employee Name': 'Robert Kim', 'Hire Date': '2026-01-10', 'Workday Schedule': '06:00-14:00', 'Department': 'Kitchen', 'Manager': 'David Rodriguez', 'Roster Bucket': 'Active'},
    ]

def generate_shift_breakdown(filtered_data, metric_key):
    """Generate shift-level breakdown showing days horizontally with shift data"""
    if not filtered_data:
        return '<div style="color: #999; font-style: italic; font-size: 0.8rem; margin-top: 8px;">No data for selected filters</div>'
    
    # Organize data by date and shift
    days_data = {}
    
    for key, data in filtered_data.items():
        # Key format: "2026-02-12 Wed Shift 1" (note: just the number, not "1st")
        parts = key.split(' ')
        if len(parts) >= 4 and 'Shift' in parts:
            date_str = parts[0]  # "2026-02-12"
            day_name = parts[1]  # "Wed" 
            shift_num = parts[3] # "1", "2", "3"
            
            if date_str not in days_data:
                days_data[date_str] = {'day_name': day_name, 'shifts': {}}
            
            # Get the metric value
            value = data.get(metric_key, 0)
            if metric_key == 'gap':
                value = data.get('expected', 0) - data.get('needed', 0)
            
            days_data[date_str]['shifts'][shift_num] = value
    
    if not days_data:
        return '<div style="color: #999; font-style: italic; font-size: 0.8rem; margin-top: 8px;">No breakdown available</div>'
    
    # Generate breakdown HTML - each day as a row
    breakdown_html = '<div style="margin-top: 8px; padding: 8px; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e9ecef;">'
    
    # Sort days chronologically  
    sorted_days = sorted(days_data.items())
    
    for i, (date_str, day_info) in enumerate(sorted_days):
        day_name = day_info['day_name']
        shifts_data = day_info['shifts']
        
        # Build the row: "Thu Shift 1: 35 | Shift 2: 28 | Shift 3: 17"
        row_parts = [f"<strong>{day_name}</strong>"]
        
        # Add shifts in order (1, 2, 3)
        for shift_num in ["1", "2", "3"]:
            if shift_num in shifts_data:
                value = shifts_data[shift_num]
                # Color coding
                if metric_key == 'gap':
                    color = '#d32f2f' if value < 0 else '#2e7d32' if value > 0 else '#666'
                else:
                    color = '#1565c0'
                
                row_parts.append(f'<span style="color: {color}; font-weight: 600;">Shift {shift_num}: {value}</span>')
        
        # Join with " | " separator
        row_html = f'''
        <div style="padding: 3px 0; font-size: 0.75rem; line-height: 1.4;">
            {" | ".join(row_parts)}
        </div>
        '''
        
        breakdown_html += row_html
        
        # Add separator line except for last day
        if i < len(sorted_days) - 1:
            breakdown_html += '<div style="border-bottom: 1px solid #e0e0e0; margin: 4px 0;"></div>'
    
    breakdown_html += '</div>'
    
    return breakdown_html

def filter_data_by_selections(location, department, week, selected_dates, shifts):
    """Filter master dataset by all selections"""
    filtered_data = {}
    
    try:
        location_data = st.session_state.master_data.get(location, {})
        dept_data = location_data.get(department, {})
        week_data = dept_data.get(week, {})
        
        for selected_date in selected_dates:
            # Handle different date types
            if hasattr(selected_date, 'date'):
                # It's a datetime.date object, convert to datetime
                date_key = datetime.combine(selected_date.date(), datetime.min.time())
            elif hasattr(selected_date, 'year'):
                # It's already a datetime or date
                if isinstance(selected_date, datetime):
                    date_key = selected_date
                else:
                    date_key = datetime.combine(selected_date, datetime.min.time())
            else:
                continue
            
            if date_key in week_data:
                for shift in shifts:
                    if shift in week_data[date_key]:
                        key = f"{date_key.strftime('%Y-%m-%d')} {date_key.strftime('%a')} Shift {shift[-1]}"
                        filtered_data[key] = week_data[date_key][shift]
        
        return filtered_data
        
    except Exception:
        # Return empty data if any filtering fails - no error display
        return {}

def calculate_overview_metrics(filtered_data):
    """Calculate overview metrics from filtered data"""
    if not filtered_data:
        return {"needed": 0, "expected": 0, "gap": 0, "punches": 0}
    
    total_needed = sum(data.get('needed', 0) for data in filtered_data.values())
    total_expected = sum(data.get('expected', 0) for data in filtered_data.values())
    total_punches = sum(data.get('punches', 0) for data in filtered_data.values())
    total_gap = total_expected - total_needed
    
    return {
        "needed": total_needed,
        "expected": total_expected, 
        "gap": total_gap,
        "punches": total_punches
    }

def filter_employees(location, department, week, selected_dates, shifts):
    """Filter employee data by all selections"""
    filtered_employees = []
    
    for emp in st.session_state.employee_data:
        if (emp['Location'] == location and 
            emp['Department'] == department and
            emp['Week'] == week and
            emp['Date'] in selected_dates and
            emp['Shift'] in shifts):
            filtered_employees.append(emp)
    
    return filtered_employees

def create_combined_headcount_attendance_table_simple(filtered_data):
    """Create combined table using Streamlit native components"""
    
    if not filtered_data:
        st.info("No data available for selected filters")
        return
    
    # Create a simple dataframe instead of complex HTML
    shift_keys = list(filtered_data.keys())
    employee_types = ['FTE', 'TEMP', 'NEW HIRES', 'Day Labor (Flex)', 'Day Labor (WW/GS)', 'Overtime (VEH/MEH)', 'Time Off (PTO)']
    
    # Create data for dataframe
    table_data = []
    
    for emp_type in employee_types:
        row = {'Employee Type': emp_type}
        
        for shift_key in shift_keys:
            data = filtered_data[shift_key]
            
            # Map employee types to data keys
            data_key_map = {
                'FTE': 'fte', 'TEMP': 'temp', 'NEW HIRES': 'new_hires',
                'Day Labor (Flex)': 'flex', 'Day Labor (WW/GS)': 'wwgs',
                'Overtime (VEH/MEH)': 'veh', 'Time Off (PTO)': 'pto'
            }
            
            att_key_map = {
                'FTE': 'fte_att', 'TEMP': 'temp_att', 'NEW HIRES': 'new_hires',
                'Day Labor (Flex)': 'flex', 'Day Labor (WW/GS)': 'wwgs', 
                'Overtime (VEH/MEH)': 'veh', 'Time Off (PTO)': 'pto'
            }
            
            # Get values
            hc_key = data_key_map.get(emp_type, 'fte')
            att_key = att_key_map.get(emp_type, 'fte_att')
            
            headcount = data.get(hc_key, 0)
            
            if att_key in ['fte_att', 'temp_att']:
                attendance = f"{data.get(att_key, 85)}%"
            else:
                default_rates = {'new_hires': 50, 'flex': 50, 'wwgs': 100, 'veh': 80, 'pto': 50}
                attendance = f"{default_rates.get(att_key, 85)}%"
            
            # Add columns for this shift
            row[f'{shift_key} HC'] = headcount
            row[f'{shift_key} Att%'] = attendance
        
        table_data.append(row)
    
    # Create and display dataframe
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

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
        available_dates = [
            datetime(2026, 2, 12), datetime(2026, 2, 13), datetime(2026, 2, 14), 
            datetime(2026, 2, 15), datetime(2026, 2, 16), datetime(2026, 2, 17), 
            datetime(2026, 2, 18)
        ]
        date_options = [f"{date.strftime('%m/%d')} ({date.strftime('%a')})" for date in available_dates]
        selected_dates_display = st.multiselect("", date_options, 
                                               default=date_options[:2], label_visibility="collapsed")
        
        # Map back to datetime objects
        selected_dates = []
        for i, date_display in enumerate(date_options):
            if date_display in selected_dates_display:
                selected_dates.append(available_dates[i]) 
    
    with col5:
        st.markdown("**Shift**")
        shifts = st.multiselect("", ["1st", "2nd", "3rd"], 
                               default=["1st", "2nd", "3rd"], label_visibility="collapsed") 
    
    # Get filtered data based on all selections
    filtered_data = filter_data_by_selections(location, selected_department, week, selected_dates, shifts)
    filtered_employees = filter_employees(location, selected_department, week, selected_dates, shifts)
    
    # Calculate responsive metrics
    overview_metrics = calculate_overview_metrics(filtered_data)
    
    # CHANGE 1 & 4: Overview Section with 4 pills including Total Punches + Shift Breakdowns
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    
    # Key metrics row - All four KPIs (now responsive to filters)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-label">Needed HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-large">{overview_metrics["needed"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📊 5% vs last week</div>', unsafe_allow_html=True)
        
        # Shift breakdown for Needed HC
        if filtered_data:
            shift_breakdown_html = generate_shift_breakdown(filtered_data, 'needed')
            st.markdown(shift_breakdown_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Expected HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-large">{overview_metrics["expected"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-change">📈 20% vs last week</div>', unsafe_allow_html=True)
        
        # Shift breakdown for Expected HC
        if filtered_data:
            shift_breakdown_html = generate_shift_breakdown(filtered_data, 'expected')
            st.markdown(shift_breakdown_html, unsafe_allow_html=True)
    
    with col3:
        gap_class = "gap-negative" if overview_metrics['gap'] < 0 else "gap-positive"
        st.markdown('<div class="metric-label">Gap in HC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{gap_class}">{abs(overview_metrics["gap"])}</div>', unsafe_allow_html=True)
        # CHANGE 2: Update Gap to show percentage change vs previous week
        st.markdown('<div class="metric-change">📉 3% vs last week</div>', unsafe_allow_html=True)
        
        # Shift breakdown for Gap in HC
        if filtered_data:
            shift_breakdown_html = generate_shift_breakdown(filtered_data, 'gap')
            st.markdown(shift_breakdown_html, unsafe_allow_html=True)

    with col4:
        # CHANGE 1: Add Total Punches pill (now responsive)
        st.markdown('<div class="metric-label">Total Punches</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-large">{overview_metrics["punches"]}</div>', unsafe_allow_html=True)
        # CHANGE 3: Add percentage change to Punches
        st.markdown('<div class="metric-change">📊 4% vs last week</div>', unsafe_allow_html=True)
        
        # Shift breakdown for Punches
        if filtered_data:
            shift_breakdown_html = generate_shift_breakdown(filtered_data, 'punches')
            st.markdown(shift_breakdown_html, unsafe_allow_html=True)
    
    # Expected HC section
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
    
    # Headcount and Attendance table
    create_combined_headcount_attendance_table_simple(filtered_data)
    
    # Employee List section (now responsive to all filters)
    st.markdown(f'<div class="section-header">{selected_department} Employee List ({len(filtered_employees)})</div>', unsafe_allow_html=True)
    
    # Employee data table - responsive to filters
    if filtered_employees:
        df = pd.DataFrame(filtered_employees)
        # Clean up the date column for display
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No employees found for the selected filters.")

if __name__ == "__main__":
    main()