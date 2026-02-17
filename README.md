
# Labor Planning Shift Optimizer

A Streamlit dashboard application for optimizing labor planning and shift management at manufacturing facilities.

![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Overview

The Labor Planning Shift Optimizer helps manufacturing facilities manage their workforce by providing:

- **Real-time HC (Headcount) Analysis**: Track expected vs. needed headcount
- **Department Gap Analysis**: Identify overstaffed and understaffed departments
- **Shift Management**: Monitor 1st, 2nd, and 3rd shift performance
- **Weekly Trends**: Visualize workforce patterns over time
- **Attendance Integration**: Factor in historical attendance rates

## 🚀 Features

### Key Metrics Dashboard
- Expected HC vs. Needed HC comparison
- Gap analysis with percentage calculations
- Week-over-week trend indicators

### Department Breakdown
- Visual gap analysis by department (Kitchen, Production, Sanitation, Quality, Warehouse, Fulfillment, Shipping)
- Color-coded indicators for understaffed (red) and overstaffed (green) areas

### Shift Management
- Individual shift analysis (1st, 2nd, 3rd shifts)
- Attendance rate integration
- Actual available workforce calculations

### Interactive Controls
- Location selection (AZ Goodyear, TX Houston, CA Los Angeles)
- Week selection for analysis
- Shift filtering options
- Attendance rate adjustment

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd labor-planning-optimizer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

### Streamlit Community Cloud Deployment

1. **Push to GitHub**: Ensure your code is in a GitHub repository

2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select your repository and branch
   - Set main file path to `app.py`

3. **Deploy**: Click "Deploy!" and your app will be live

## 📁 Project Structure

```
labor-planning-optimizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore patterns
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── data/
    └── sample_data.csv   # Sample data file (optional)
```

## 🎯 Usage

### Dashboard Navigation

1. **Sidebar Configuration**: 
   - Select your facility location
   - Choose the week for analysis
   - Filter shifts to analyze
   - Adjust historical attendance rates

2. **Main Dashboard**:
   - View key metrics at the top
   - Check staffing alerts and warnings
   - Analyze department gaps in the chart
   - Review weekly trends

3. **Detailed Analysis**:
   - Expand shift summaries for detailed breakdown
   - View data tables for raw numbers
   - Export data if needed

### Interpreting the Data

- **Red indicators**: Understaffed areas requiring attention
- **Green indicators**: Overstaffed areas with potential for reallocation
- **Gray/Neutral**: Properly balanced staffing levels

## 🔧 Customization

### Adding New Locations
Edit the sidebar selectbox in `app.py`:
```python
location = st.selectbox("Location", ["AZ Goodyear", "Your New Location"], index=0)
```

### Modifying Departments
Update the departments dictionary in the session state initialization:
```python
st.session_state.departments = {
    'Your Department': gap_value,
    # Add more departments as needed
}
```

### Changing Color Schemes
Modify the custom CSS section at the top of `app.py` to match your brand colors.

## 📊 Data Sources

This application currently uses simulated data for demonstration. To connect real data:

1. Replace the sample data generation with your database connections
2. Implement API calls to your HR/workforce management systems
3. Add data validation and error handling
4. Consider implementing caching for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [Streamlit documentation](https://docs.streamlit.io/)
- Review the [Plotly documentation](https://plotly.com/python/) for chart customization

## 🔄 Version History

- **v1.0.0**: Initial release with basic dashboard functionality
- **v1.1.0**: Added department breakdown and shift analysis
- **v1.2.0**: Enhanced visualizations and interactivity

## 🚀 Future Enhancements

- [ ] Database integration for real-time data
- [ ] Predictive analytics for workforce planning
- [ ] Email alerts for critical staffing gaps
- [ ] Mobile-responsive design improvements
- [ ] Export functionality for reports
- [ ] User authentication and role-based access
- [ ] Historical data analysis and trending

---

**Built with ❤️ using [Streamlit](https://streamlit.io/)**
