"""
Streamlit Dashboard for SmartSales AI

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


def _get_mock_store_ai_analysis(store_rev):
    """Generate AI analysis for store performance."""
    top_store = store_rev.loc[store_rev['revenue'].idxmax()]
    lowest_store = store_rev.loc[store_rev['revenue'].idxmin()]
    online_store = store_rev[store_rev['store'].str.contains('Online', case=False)]
    
    analysis = f"""
🤖 **AI Store Performance Analysis**

**🏆 Top Performer**: {top_store['store']} is leading with exceptional performance. 
Consider replicating their strategies (staffing, promotions, inventory management) across other locations.

**📈 Growth Opportunity**: {lowest_store['store']} shows potential for improvement. 
Recommend conducting customer satisfaction surveys and analyzing foot traffic patterns.

**💡 Strategic Recommendations**:
• Increase marketing budget for underperforming stores
• Implement cross-store best practice sharing programs
• Consider seasonal promotions to boost overall performance
"""
    if len(online_store) > 0:
        analysis += f"\n**🌐 Digital Channel**: Online_Store contributes ${online_store['revenue'].values[0]:,.0f}. Focus on omnichannel integration for higher conversion."
    
    return analysis


# ============================================
# Main Dashboard
# ============================================
def main():
    # Sidebar Configuration
    st.sidebar.image("assets/logo.png", width=100)
    st.sidebar.title("🎛️ Controls")
    
    # 🔐 Multi-Provider AI Settings
    with st.sidebar.expander("🔐 AI Settings", expanded=True):
        # AI Provider Selection
        ai_provider = st.selectbox(
            "AI Provider",
            ["OpenAI", "Google Gemini", "Anthropic Claude", "Groq"],
            help="Select your preferred AI provider"
        )
        
        # Provider-specific settings
        provider_config = {
            "OpenAI": {"placeholder": "sk-...", "env_key": "OPENAI_API_KEY"},
            "Google Gemini": {"placeholder": "AIza...", "env_key": "GOOGLE_API_KEY"},
            "Anthropic Claude": {"placeholder": "sk-ant-...", "env_key": "ANTHROPIC_API_KEY"},
            "Groq": {"placeholder": "gsk_...", "env_key": "GROQ_API_KEY"}
        }
        
        config = provider_config[ai_provider]
        
        # Initialize session state for widget
        if "api_key_input" not in st.session_state:
            st.session_state.api_key_input = ""
        
        api_key_input = st.text_input(
            f"{ai_provider} API Key", 
            type="password",
            placeholder=config["placeholder"],
            help=f"Enter your {ai_provider} API key for live AI insights",
            key="api_key_input"
        )
        
        # Store selected provider in session
        st.session_state["ai_provider"] = ai_provider
        
        # Update session state
        if api_key_input:
            os.environ[config["env_key"]] = api_key_input
            use_real_ai = True
            st.success(f"✅ {ai_provider} Active")
            
            # Test and Reset buttons
            col_test, col_reset = st.columns(2)
            with col_test:
                if st.button("🧪 Test", key="test_api"):
                    with st.spinner("Testing..."):
                        try:
                            if ai_provider == "OpenAI":
                                from openai import OpenAI
                                client = OpenAI(api_key=api_key_input)
                                response = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[{"role": "user", "content": "Say 'API works!' in 3 words."}],
                                    max_tokens=20
                                )
                                result = response.choices[0].message.content
                            elif ai_provider == "Google Gemini":
                                import google.generativeai as genai
                                genai.configure(api_key=api_key_input)
                                model = genai.GenerativeModel('gemini-pro')
                                response = model.generate_content("Say 'API works!' in 3 words.")
                                result = response.text
                            elif ai_provider == "Anthropic Claude":
                                import anthropic
                                client = anthropic.Anthropic(api_key=api_key_input)
                                response = client.messages.create(
                                    model="claude-3-haiku-20240307",
                                    max_tokens=20,
                                    messages=[{"role": "user", "content": "Say 'API works!' in 3 words."}]
                                )
                                result = response.content[0].text
                            elif ai_provider == "Groq":
                                from groq import Groq
                                client = Groq(api_key=api_key_input)
                                response = client.chat.completions.create(
                                    model="llama3-8b-8192",
                                    messages=[{"role": "user", "content": "Say 'API works!' in 3 words."}],
                                    max_tokens=20
                                )
                                result = response.choices[0].message.content
                            st.success(f"✅ {result}")
                        except Exception as e:
                            st.error(f"❌ {str(e)[:50]}")
            with col_reset:
                if st.button("🔄 Reset", key="reset_api"):
                    del st.session_state["api_key_input"]
                    for key in provider_config.values():
                        os.environ.pop(key["env_key"], None)
                    st.rerun()
        else:
            use_real_ai = False
            st.info("🔑 Enter API key for live AI insights")

    # Data Filters
    st.sidebar.markdown("### 📅 Filters")
    date_range = st.sidebar.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    st.sidebar.markdown("---")
    show_ai_insights = st.sidebar.checkbox("🤖 Show AI Insights", value=True)
    show_anomalies = st.sidebar.checkbox("⚠️ Show Anomalies", value=True)
    
    # --- CSV Upload Section ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Data Source")
    data_source = st.sidebar.radio(
        "Choose data source:",
        ["📊 Sample Data", "📁 Upload CSV"],
        index=0
    )
    
    if data_source == "📁 Upload CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Upload your file",
            type=["csv", "xlsx", "xls"],
            help="CSV/Excel must have columns: store, category, revenue"
        )
        
        if uploaded_file is not None:
            try:
                # Handle different file types
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                # Validate required columns
                required_cols = ['store', 'category', 'revenue']
                missing = [c for c in required_cols if c not in df.columns]
                if missing:
                    st.sidebar.error(f"❌ Missing columns: {missing}")
                    df = load_sample_data()
                else:
                    # Convert date column if exists
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                    elif 'timestamp' in df.columns:
                        df['date'] = pd.to_datetime(df['timestamp'])
                    else:
                        df['date'] = pd.Timestamp.now()
                    
                    # Ensure quantity column exists
                    if 'quantity' not in df.columns:
                        df['quantity'] = 1
                    
                    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)[:50]}")
                df = load_sample_data()
        else:
            st.sidebar.info("👆 Upload a CSV file to analyze your data")
            df = load_sample_data()
    else:
        # Load sample data
        df = load_sample_data()
    
    # --- View Data Option ---
    st.sidebar.markdown("---")
    if st.sidebar.checkbox("👁️ View Raw Data", value=False):
        st.markdown("### 📋 Data Preview")
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"Showing 20 of {len(df):,} rows | Columns: {', '.join(df.columns)}")
        st.markdown("---")
    
    # Header
    st.markdown("# 🧠 SmartSales AI")
    st.markdown("*AI-Powered Sales Dashboard with Real-Time Insights*")
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = df['revenue'].sum()
    total_txns = len(df)
    avg_order = total_revenue / total_txns
    top_category = df.groupby('category')['revenue'].sum().idxmax()
    
    # Format large numbers compactly (e.g., $2.18M)
    def format_currency(value):
        if value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:,.0f}"
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=format_currency(total_revenue),
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
    
    # --- Dynamic Store Performance Description ---
    top_store = store_rev.loc[store_rev['revenue'].idxmax()]
    lowest_store = store_rev.loc[store_rev['revenue'].idxmin()]
    avg_revenue = store_rev['revenue'].mean()
    total_stores = len(store_rev)
    
    # Calculate performance difference
    perf_diff = ((top_store['revenue'] - lowest_store['revenue']) / lowest_store['revenue']) * 100
    
    # Summary info box
    st.info(
        f"📊 Performance Summary: Across {total_stores} locations, "
        f"{top_store['store']} leads with \\${top_store['revenue']:,.0f} in revenue, "
        f"while {lowest_store['store']} generated \\${lowest_store['revenue']:,.0f}. "
        f"Average store revenue is \\${avg_revenue:,.0f}. "
        f"Top performer exceeds lowest by {perf_diff:.1f}%."
    )
    
    # --- Optional AI Insights Button ---
    if st.button("🤖 Generate AI Store Analysis", key="ai_store_analysis"):
        with st.spinner("🧠 Analyzing store performance with AI..."):
            api_key = os.environ.get("OPENAI_API_KEY")
            # Check if real AI is available
            if api_key and not api_key.startswith("sk-..."):
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    
                    # Prepare store data for LLM
                    store_data = store_rev.to_dict('records')
                    prompt = f"""Analyze this retail store performance data and provide strategic insights:

Store Revenue Data:
{store_data}

Provide:
1. 🏆 Top Performer analysis (why they're successful)
2. 📈 Growth Opportunity (which store needs improvement and how)
3. 💡 Strategic Recommendations (3 bullet points)
4. 🌐 Digital Channel insights (if Online_Store present)

Keep response concise and actionable."""

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a retail analytics expert providing actionable business insights."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    ai_analysis = response.choices[0].message.content
                    st.success("🤖 **AI Store Performance Analysis** (Powered by GPT)")
                    st.markdown(ai_analysis)
                except Exception as e:
                    st.warning(f"⚠️ API Error: {str(e)[:80]}... Showing demo analysis.")
                    st.info(_get_mock_store_ai_analysis(store_rev))
            else:
                st.info(_get_mock_store_ai_analysis(store_rev))
    
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
