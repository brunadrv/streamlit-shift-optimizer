# Labor Planning Shift Optimizer

A Streamlit dashboard application for optimizing labor planning and shift management at manufacturing facilities.

## 🚀 Quick Deploy to Streamlit Cloud

1. **Push this code to GitHub** (see GITHUB_SETUP_GUIDE.md for detailed instructions)
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Sign in with GitHub**
4. **Click "New app"** and select your repository
5. **Set main file to `app.py`**
6. **Click Deploy!**

## 📋 Features

- **Real-time HC Analysis**: Track expected vs. needed headcount
- **Department Gap Analysis**: Visual breakdown by department
- **Weekly Shift Summary**: Monitor 1st, 2nd, and 3rd shifts
- **Interactive Charts**: Plotly-powered visualizations
- **Department Details**: Specific recommendations per department

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📊 Dashboard Sections

### Key Metrics
- Expected HC: 80 (25% vs last week)
- Needed HC: 100 (5% vs last week)  
- Gap in HC: 20 (Understaffed by 20%)

### Department Breakdown
- Kitchen: -7 (understaffed)
- Production: +7 (overstaffed)
- Sanitation: +10 (overstaffed)
- Quality: 0 (balanced)
- Warehouse: -2 (understaffed)
- Fulfillment: 0 (balanced)
- Shipping: +5 (overstaffed)

## 🔧 Customization

To modify departments or data, edit the session state initialization in `app.py`:

```python
st.session_state.departments = {
    'Kitchen': -7,
    'Production': 7,
    # Add your departments here
}
```

## 📈 Data Integration

The app currently uses sample data. To integrate real data:

1. Replace sample data with database connections
2. Add API integrations for real-time HR data
3. Implement authentication if needed

Built with ❤️ using [Streamlit](https://streamlit.io/)