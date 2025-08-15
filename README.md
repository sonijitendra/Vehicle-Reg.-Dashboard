# Vehicle Registration Analytics Dashboard

An investor-focused interactive dashboard for analyzing vehicle registration data from India's automotive market, built with Streamlit and focused on Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth analysis.

## 🎯 Objective

This project provides a comprehensive analytics platform for investors to analyze vehicle registration trends in India, offering insights into:
- Vehicle category performance (2W/3W/4W)
- Manufacturer-wise growth patterns
- Market dynamics and growth trends
- Key investor insights for decision-making

## 📊 Features

### Core Analytics
- **YoY Growth Analysis**: Year-over-year percentage changes across manufacturers and categories
- **QoQ Growth Analysis**: Quarter-over-quarter momentum tracking
- **Interactive Filtering**: Date range, vehicle category, and manufacturer filters
- **Multiple Visualizations**: Line charts, bar charts, scatter plots, and pie charts
- **Key Metrics Dashboard**: Summary statistics and performance indicators

### Investor Insights
- Automated generation of key market insights
- Top performer identification
- Market momentum analysis
- Growth trend visualization
- Data-driven investment observations

## 🏗️ Project Structure

```
vehicle-registration-dashboard/
├── data/                          # Data storage directory
│   ├── sample_vehicle_data.csv    # Sample dataset for testing
│   └── vehicle_registrations.db   # SQLite database
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── app.py                         # Main application entry point
├── data_collection.py             # Web scraping and data fetching
├── data_processing.py             # Data cleaning and growth calculations
├── database.py                    # SQLite database operations
├── dashboard.py                   # Streamlit UI components
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd vehicle-registration-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard**
   Open your browser and navigate to `http://localhost:8501`

## 📊 Data Sources

### Primary Data Source
- **Vahan Dashboard**: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
- **Data Collection Method**: Web scraping with BeautifulSoup/Requests
- **Fallback**: Enhanced sample data generation for testing

### Data Structure
The system expects data in the following format:
- `date`: Registration date (YYYY-MM-DD)
- `year`: Registration year
- `quarter`: Registration quarter (1-4)
- `vehicle_category`: Vehicle type (2W/3W/4W)
- `manufacturer`: Vehicle manufacturer name
- `registrations`: Number of vehicles registered

## 🔧 Technical Architecture

### Database Integration
- **SQLite Database**: Local storage for processed data
- **Growth Calculations**: SQL-based YoY and QoQ calculations
- **Performance**: Optimized queries with proper indexing

### Web Scraping Capabilities
- **Primary Method**: BeautifulSoup with requests
- **Alternative**: Selenium for JavaScript-heavy pages (optional)
- **Error Handling**: Graceful fallback to sample data

### Analytics Engine
- **YoY Growth**: Year-over-Year percentage calculations
- **QoQ Growth**: Quarter-over-Quarter momentum tracking
- **Dynamic Insights**: Automated investor-relevant observations

## 💡 Key Features

### Interactive Dashboard
- **Date Range Selection**: Filter data by time periods
- **Multi-Filter System**: Vehicle category and manufacturer filters
- **Real-time Updates**: Dynamic recalculation based on selections
- **Export Capability**: Download filtered data as CSV

### Visualizations
- **Trend Analysis**: Line charts showing registration patterns
- **Manufacturer Comparison**: Horizontal bar charts
- **Growth Scatter Plot**: YoY vs QoQ analysis
- **Market Share**: Category-wise distribution pie charts

### Advanced Analytics
- **SQL Query Interface**: Execute custom database queries
- **Growth Metrics**: Automated YoY/QoQ calculations
- **Top Performers**: Dynamic ranking by various metrics
- **Market Insights**: AI-generated investor observations

## 📈 Growth Calculations

### Year-over-Year (YoY) Growth
```sql
YoY Growth % = ((Current Year Registrations - Previous Year Registrations) / Previous Year Registrations) × 100
```

### Quarter-over-Quarter (QoQ) Growth
```sql
QoQ Growth % = ((Current Quarter Registrations - Previous Quarter Registrations) / Previous Quarter Registrations) × 100
```

## 🛠️ Development Guide

### Adding New Features
1. **Data Collection**: Modify `data_collection.py` for new data sources
2. **Processing Logic**: Update `data_processing.py` for new calculations
3. **Database Schema**: Extend `database.py` for additional tables
4. **UI Components**: Add new visualizations in `dashboard.py`

### Error Handling
- **Network Issues**: Automatic fallback to sample data
- **Database Errors**: Graceful degradation to in-memory processing
- **Missing Data**: Clear error messages and alternative suggestions

### Performance Optimization
- **Data Caching**: Streamlit cache for processed datasets
- **SQL Indexing**: Optimized database queries
- **Lazy Loading**: On-demand calculation of expensive operations

## 📋 Usage Examples

### Basic Usage
1. Launch the dashboard
2. Select date range and filters
3. Analyze trends and growth metrics
4. Review investor insights

### Advanced Analysis
1. Access the SQL Query Interface
2. Execute predefined analytical queries
3. Export results for further analysis
4. Create custom reports

## 🔄 Data Update Process

### Manual Update
1. Run `python data_collection.py` to fetch latest data
2. Data automatically processes and updates database
3. Dashboard reflects changes immediately

### Automated Scheduling
- Set up cron jobs for regular data collection
- Configure alerts for data quality issues
- Monitor scraping success rates

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core dashboard functionality
- ✅ SQL database integration
- ✅ Basic web scraping
- ✅ Growth calculations

### Phase 2 (Planned)
- 🔄 Real-time data streaming
- 🔄 Advanced ML predictions
- 🔄 Multi-state data coverage
- 🔄 API integration

### Phase 3 (Future)
- 📋 Mobile responsive design
- 📋 User authentication
- 📋 Custom alert system
- 📋 Advanced export options

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check if data directory exists
ls -la data/
# Recreate database
python database.py
```

**2. Web Scraping Failures**
```bash
# Test network connectivity
python data_collection.py
# Check if using fallback data
```

**3. Dashboard Loading Issues**
```bash
# Clear Streamlit cache
streamlit cache clear
# Restart the application
```

### Support
- Check logs for detailed error messages
- Verify all dependencies are installed
- Ensure Python version compatibility

## 📄 License

This project is developed for educational and analytical purposes. Please ensure compliance with data source terms of service when scraping external websites.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

*Built using Streamlit, Pandas, and SQLite*


## Video walkthrough
Paste your unlisted link here: <ADD LINK>

## Data collection (Vahan)
I used a Selenium-based scraper to fetch manufacturer-wise and category-wise registrations from the Vahan dashboard.
Because the site renders data dynamically, the scraper waits for specific table elements before extracting rows. 
Detailed steps and selectors are documented in `docs/DATA_COLLECTION.md`. A small cached SQLite DB is checked in to let you run the dashboard instantly.
