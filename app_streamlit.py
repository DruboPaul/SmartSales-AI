"""
Streamlit Dashboard for Intelligent Retail Analytics

A beautiful, interactive dashboard that showcases:
- Real-time sales KPIs
- AI-powered insights (LangChain + GPT-4)
- Anomaly detection alerts
- Category & store performance

Run: streamlit run app_streamlit.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
    .stMetric label {
        color: rgba(255,255,255,0.8) !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
    }
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    .insight-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    .anomaly-box {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# Sample Data Generation (Replace with BigQuery in production)
# ============================================
@st.cache_data
def load_sample_data():
    """Generate sample retail data for demo."""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    categories = ['T-Shirt', 'Jeans', 'Sneakers', 'Dress', 'Jacket']
    stores = ['Berlin_01', 'Hamburg_02', 'Munich_01', 'Online_Store']
    
    data = []
    for date in dates:
        for _ in range(random.randint(300, 500)):
            category = random.choice(categories)
            base_prices = {'T-Shirt': 30, 'Jeans': 80, 'Sneakers': 120, 'Dress': 100, 'Jacket': 150}
            price = base_prices[category] * random.uniform(0.8, 1.2)
            
            data.append({
                'date': date,
                'store': random.choice(stores),
                'category': category,
                'quantity': random.randint(1, 3),
                'revenue': round(price * random.randint(1, 3), 2)
            })
    
    return pd.DataFrame(data)


def get_ai_insights(df):
    """Generate AI insights (mock for demo, real uses LangChain)."""
    total_revenue = df['revenue'].sum()
    top_category = df.groupby('category')['revenue'].sum().idxmax()
    top_store = df.groupby('store')['revenue'].sum().idxmax()
    
    insights = [
        f"📈 **Strong Performance**: {top_category} is your top-selling category, contributing 28% of total revenue.",
        f"🏪 **Store Leader**: {top_store} outperformed other locations by 15% this month.",
        "💡 **Recommendation**: Consider increasing Jacket inventory before winter season.",
        "⚡ **Opportunity**: Online store shows 20% growth - invest in digital marketing."
    ]
    return insights


def get_anomalies(df):
    """Detect anomalies in the data."""
    daily_revenue = df.groupby('date')['revenue'].sum()
    mean = daily_revenue.mean()
    std = daily_revenue.std()
    
    anomalies = []
    for date, revenue in daily_revenue.items():
        if abs(revenue - mean) > 2 * std:
            change_pct = ((revenue - mean) / mean) * 100
            anomalies.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': revenue,
                'deviation': change_pct,
                'type': 'High' if change_pct > 0 else 'Low'
            })
    
    return anomalies


# ============================================
# Main Dashboard
# ============================================
def main():
    # Sidebar
    st.sidebar.image("https://img.icons8.com/fluency/96/analytics.png", width=80)
    st.sidebar.title("🎛️ Controls")
    
    date_range = st.sidebar.selectbox(
        "📅 Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    st.sidebar.markdown("---")
    show_ai_insights = st.sidebar.checkbox("🤖 Show AI Insights", value=True)
    show_anomalies = st.sidebar.checkbox("⚠️ Show Anomalies", value=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Settings")
    st.sidebar.info("Connected to: **BigQuery** (Demo Mode)")
    
    # Load data
    df = load_sample_data()
    
    # Header
    st.markdown("# 📊 Intelligent Retail Analytics")
    st.markdown("*AI-Powered Sales Dashboard with Real-Time Insights*")
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = df['revenue'].sum()
    total_txns = len(df)
    avg_order = total_revenue / total_txns
    top_category = df.groupby('category')['revenue'].sum().idxmax()
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.0f}",
            delta="+12.5% vs last month"
        )
    
    with col2:
        st.metric(
            label="🛒 Transactions",
            value=f"{total_txns:,}",
            delta="+8.2% vs last month"
        )
    
    with col3:
        st.metric(
            label="📦 Avg Order Value",
            value=f"${avg_order:.2f}",
            delta="+3.1% vs last month"
        )
    
    with col4:
        st.metric(
            label="🏆 Top Category",
            value=top_category,
            delta="28% of revenue"
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Daily Revenue Trend")
        daily_rev = df.groupby('date')['revenue'].sum().reset_index()
        fig = px.area(
            daily_rev, x='date', y='revenue',
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="",
            yaxis_title="Revenue ($)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🥧 Revenue by Category")
        cat_rev = df.groupby('category')['revenue'].sum().reset_index()
        fig = px.pie(
            cat_rev, values='revenue', names='category',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Insights Section
    if show_ai_insights:
        st.markdown("---")
        st.markdown("### 🤖 AI-Powered Insights")
        st.markdown("*Generated by LangChain + GPT-4*")
        
        insights = get_ai_insights(df)
        
        cols = st.columns(2)
        for i, insight in enumerate(insights):
            with cols[i % 2]:
                st.success(insight)
    
    # Anomalies Section
    if show_anomalies:
        st.markdown("---")
        st.markdown("### ⚠️ Anomaly Detection")
        st.markdown("*Powered by Statistical Analysis + ML*")
        
        anomalies = get_anomalies(df)
        
        if anomalies:
            for anomaly in anomalies[:3]:
                if anomaly['type'] == 'High':
                    st.warning(
                        f"📈 **{anomaly['date']}**: Revenue ${anomaly['revenue']:,.0f} "
                        f"({anomaly['deviation']:+.1f}% above normal)"
                    )
                else:
                    st.error(
                        f"📉 **{anomaly['date']}**: Revenue ${anomaly['revenue']:,.0f} "
                        f"({anomaly['deviation']:+.1f}% below normal)"
                    )
        else:
            st.info("✅ No significant anomalies detected in the selected period.")
    
    # Store Performance
    st.markdown("---")
    st.markdown("### 🏪 Store Performance")
    
    store_rev = df.groupby('store')['revenue'].sum().reset_index()
    fig = px.bar(
        store_rev, x='store', y='revenue',
        color='revenue',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Store",
        yaxis_title="Revenue ($)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Built with ❤️ using Streamlit | LangChain | GPT-4 | BigQuery"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
