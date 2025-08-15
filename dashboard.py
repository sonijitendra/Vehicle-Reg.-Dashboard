"""
Vehicle Registration Analytics Dashboard
Author: <Jitendra Soni>
Description: Streamlit dashboard for exploring and analyzing Indian vehicle registration data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# My own data processing + database classes
from data_processing import VehicleDataProcessor
from data_collection import VehicleDataCollector
from database import VehicleDatabase

# Keep processed data in memory so the app runs faster
@st.cache_data
def load_and_process_data():
    """Load and process the vehicle registration data with caching"""
    csv_path = "data/vahan_vehicle_data.csv"  # match assignment requirement

    # If CSV doesn't exist, collect data
    if not os.path.exists(csv_path):
        collector = VehicleDataCollector()
        st.info("Fetching fresh data from Vahan dashboard...")
        collector.collect_and_save()

        # If file now exists, clear message by rerunning
        if os.path.exists(csv_path):
            st.rerun()

    # Now process data
    from data_processing import VehicleDataProcessor
    try:
        processor = VehicleDataProcessor(use_database=True)
        processed_data = processor.process_all_data()
        return processed_data, processor
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def create_filters(df):
    """Sidebar filters: year range, vehicle category, and manufacturer."""
    st.sidebar.header("📊 Dashboard Filters")

    # Time period picker
    st.sidebar.subheader("📅 Time Period")
    years = sorted(df['year'].unique())
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_year = st.selectbox("From Year", years, index=0)
    with col2:
        end_year = st.selectbox("To Year", years, index=len(years)-1)

    # Vehicle categories
    st.sidebar.subheader("🚗 Vehicle Categories")
    categories = ['All'] + sorted(df['vehicle_category'].unique().tolist())
    selected_categories = st.sidebar.multiselect("Select Categories", categories, default=['All'])

    # Manufacturers
    st.sidebar.subheader("🏭 Manufacturers")
    makers = ['All'] + sorted(df['manufacturer'].unique().tolist())
    selected_makers = st.sidebar.multiselect("Select Manufacturers", makers, default=['All'])

    return start_year, end_year, selected_categories, selected_makers

def filter_data(df, start_year, end_year, selected_categories, selected_makers):
    """Filter dataframe based on sidebar selections."""
    filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    if 'All' not in selected_categories:
        filtered = filtered[filtered['vehicle_category'].isin(selected_categories)]
    if 'All' not in selected_makers:
        filtered = filtered[filtered['manufacturer'].isin(selected_makers)]
    return filtered

def summary_metrics(df):
    """Top-level numbers: total registrations, unique makers, avg growth."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = df['registrations'].sum()
        st.metric("Total Registrations", f"{total:,}")

    with col2:
        st.metric("Manufacturers", df['manufacturer'].nunique())

    with col3:
        avg_yoy = df['yoy_growth'].mean()
        st.metric("Avg YoY Growth", f"{avg_yoy:.1f}%" if not pd.isna(avg_yoy) else "N/A")

    with col4:
        avg_qoq = df['qoq_growth'].mean()
        st.metric("Avg QoQ Growth", f"{avg_qoq:.1f}%" if not pd.isna(avg_qoq) else "N/A")

def reg_trends_chart(df):
    """Line chart: registrations over time by category."""
    trends = df.groupby(['year', 'quarter', 'vehicle_category'])['registrations'].sum().reset_index()
    trends['period'] = trends['year'].astype(str) + '-Q' + trends['quarter'].astype(str)

    fig = px.line(trends, x='period', y='registrations', color='vehicle_category',
                  title="Vehicle Registration Trends", markers=True)
    fig.update_layout(hovermode='x unified')
    return fig

def top_makers_chart(df):
    """Horizontal bar: top 10 manufacturers by total registrations."""
    latest = df.groupby('manufacturer')['registrations'].sum().reset_index()
    latest = latest.sort_values('registrations', ascending=True).tail(10)

    fig = px.bar(latest, x='registrations', y='manufacturer', orientation='h',
                 title="Top 10 Manufacturers")
    return fig

def growth_scatter(df):
    """Scatter plot: YoY vs QoQ growth."""
    growth = df.dropna(subset=['yoy_growth', 'qoq_growth'])
    if growth.empty:
        fig = go.Figure()
        fig.add_annotation(text="No growth data available", x=0.5, y=0.5, showarrow=False)
        return fig

    fig = px.scatter(growth, x='yoy_growth', y='qoq_growth', color='vehicle_category',
                     size='registrations', hover_data=['manufacturer'],
                     title="YoY vs QoQ Growth")
    fig.add_hline(y=0, line_dash="dash", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", opacity=0.5)
    return fig

def market_share_pie(df):
    """Pie chart: category market share."""
    share = df.groupby('vehicle_category')['registrations'].sum().reset_index()
    fig = px.pie(share, values='registrations', names='vehicle_category',
                 title="Market Share by Category")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def show_insights(processor, filtered):
    """Show text-based insights for investors."""
    st.subheader("💡 Key Insights")
    for idx, insight in enumerate(processor.generate_insights(filtered), 1):
        st.markdown(f"**{idx}.** {insight}")

def create_dashboard():
    """Main function that builds the whole dashboard layout."""
    st.title("🚗 Vehicle Registration Analytics Dashboard")
    st.markdown("### Investor-Focused Analysis of India's Automotive Market")
    st.markdown("---")

    with st.spinner("Loading data..."):
        df, processor = load_and_process_data()

    if df is None:
        st.error("No data available to load.")
        return

    # Sidebar filters
    start_year, end_year, selected_categories, selected_makers = create_filters(df)
    filtered = filter_data(df, start_year, end_year, selected_categories, selected_makers)

    if filtered.empty:
        st.warning("No data for these filters. Try adjusting them.")
        return

    # Key numbers
    st.subheader("📊 Key Metrics")
    summary_metrics(filtered)
    st.markdown("---")

    # Charts
    st.subheader("📈 Analytics Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(reg_trends_chart(filtered), use_container_width=True)
    with col2:
        st.plotly_chart(top_makers_chart(filtered), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(growth_scatter(filtered), use_container_width=True)
    with col4:
        st.plotly_chart(market_share_pie(filtered), use_container_width=True)

    st.markdown("---")

    # Text insights
    show_insights(processor, filtered)

    st.markdown("---")

    # Raw data preview
    with st.expander("📋 View Raw Data"):
        st.dataframe(filtered.head(100))
        csv = filtered.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name=f"vehicle_data_{start_year}_{end_year}.csv")

    # Footer
    st.markdown("---")
    st.markdown("*Data Source: Vahan Dashboard (Sample Data for Demo)*")
    st.markdown("*Dashboard built with Streamlit & Plotly*")

if __name__ == "__main__":
    create_dashboard()
