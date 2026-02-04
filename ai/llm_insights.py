"""
LLM-Powered Sales Insights Generator

Uses LangChain + OpenAI GPT-4 to generate natural language insights
from BigQuery sales data. Demonstrates:
- LangChain integration
- Prompt engineering
- LLM API usage
- Structured output parsing

Usage:
    from ai.llm_insights import SalesInsightsGenerator
    
    generator = SalesInsightsGenerator()
    insights = generator.analyze_sales_data(sales_df)
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class SalesInsight(BaseModel):
    """Structured output for sales insights."""
    summary: str = Field(description="Executive summary of sales performance")
    top_performers: List[str] = Field(description="Top performing products/categories")
    concerns: List[str] = Field(description="Areas of concern or declining trends")
    recommendations: List[str] = Field(description="Actionable recommendations")
    predicted_trend: str = Field(description="Prediction for next period")


class SalesInsightsGenerator:
    """
    LangChain-powered sales analysis engine.
    
    Transforms raw sales data into actionable business insights
    using GPT-4 with structured prompts.
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize the insights generator.
        
        Args:
            model: OpenAI model to use (gpt-4, gpt-3.5-turbo)
            temperature: Creativity level (0=focused, 1=creative)
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.output_parser = PydanticOutputParser(pydantic_object=SalesInsight)
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Configure prompt templates for sales analysis."""
        
        # Load custom prompt template
        prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/sales_analyst.txt")
        
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = self._default_system_prompt()
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessagePromptTemplate.from_template(
                "Analyze the following sales data and provide insights:\n\n"
                "{sales_summary}\n\n"
                "Format your response as:\n{format_instructions}"
            )
        ])
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for sales analyst persona."""
        return """You are a senior retail analytics expert with 15 years of experience.
Your role is to analyze sales data and provide actionable business insights.

Guidelines:
- Be concise but thorough
- Focus on actionable recommendations
- Highlight both opportunities and risks
- Use specific numbers when available
- Consider seasonal trends and market factors

Your analysis should help retail managers make data-driven decisions."""
    
    def analyze_sales_data(
        self,
        sales_data: Dict,
        period: str = "daily",
        include_forecast: bool = True
    ) -> SalesInsight:
        """
        Generate AI-powered insights from sales data.
        
        Args:
            sales_data: Dictionary containing sales metrics
            period: Analysis period (daily, weekly, monthly)
            include_forecast: Whether to include trend prediction
            
        Returns:
            SalesInsight object with structured analysis
        """
        # Format sales data as summary
        sales_summary = self._format_sales_summary(sales_data, period)
        
        # Generate insights using LangChain
        chain = self.prompt | self.llm | self.output_parser
        
        result = chain.invoke({
            "sales_summary": sales_summary,
            "format_instructions": self.output_parser.get_format_instructions()
        })
        
        return result
    
    def _format_sales_summary(self, data: Dict, period: str) -> str:
        """Format raw data into readable summary for LLM."""
        lines = [
            f"📊 Sales Report - {period.title()} Analysis",
            f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "-" * 40
        ]
        
        if "total_revenue" in data:
            lines.append(f"💰 Total Revenue: ${data['total_revenue']:,.2f}")
        
        if "total_transactions" in data:
            lines.append(f"🛒 Total Transactions: {data['total_transactions']:,}")
        
        if "avg_order_value" in data:
            lines.append(f"📈 Avg Order Value: ${data['avg_order_value']:.2f}")
        
        if "top_categories" in data:
            lines.append("\n🏆 Top Categories:")
            for cat, revenue in data["top_categories"].items():
                lines.append(f"   • {cat}: ${revenue:,.2f}")
        
        if "store_performance" in data:
            lines.append("\n🏪 Store Performance:")
            for store, metrics in data["store_performance"].items():
                lines.append(f"   • {store}: ${metrics.get('revenue', 0):,.2f}")
        
        if "comparison" in data:
            comp = data["comparison"]
            change = comp.get("revenue_change_pct", 0)
            emoji = "📈" if change > 0 else "📉"
            lines.append(f"\n{emoji} vs Previous Period: {change:+.1f}%")
        
        return "\n".join(lines)
    
    def generate_daily_report(self, bigquery_results: List[Dict]) -> str:
        """
        Generate a complete daily report from BigQuery results.
        
        Args:
            bigquery_results: Raw query results from BigQuery
            
        Returns:
            Formatted markdown report with AI insights
        """
        # Aggregate data
        total_revenue = sum(r.get("price", 0) * r.get("quantity", 1) for r in bigquery_results)
        total_txns = len(bigquery_results)
        
        # Group by category
        categories = {}
        for r in bigquery_results:
            cat = r.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + r.get("price", 0) * r.get("quantity", 1)
        
        # Prepare data for analysis
        sales_data = {
            "total_revenue": total_revenue,
            "total_transactions": total_txns,
            "avg_order_value": total_revenue / total_txns if total_txns > 0 else 0,
            "top_categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        }
        
        # Generate AI insights
        insights = self.analyze_sales_data(sales_data, period="daily")
        
        # Format final report
        report = f"""# 📊 Daily Sales Intelligence Report
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Executive Summary
{insights.summary}

## 🏆 Top Performers
{chr(10).join(f"- {item}" for item in insights.top_performers)}

## ⚠️ Areas of Concern
{chr(10).join(f"- {item}" for item in insights.concerns)}

## 💡 Recommendations
{chr(10).join(f"- {item}" for item in insights.recommendations)}

## 📈 Trend Prediction
{insights.predicted_trend}

---
*Powered by LangChain + GPT-4*
"""
        return report


# Example usage and testing
if __name__ == "__main__":
    # Sample data for testing
    sample_data = {
        "total_revenue": 45000.00,
        "total_transactions": 523,
        "avg_order_value": 86.04,
        "top_categories": {
            "T-Shirt": 15000,
            "Jeans": 12000,
            "Sneakers": 10000,
            "Dress": 5000,
            "Jacket": 3000
        },
        "comparison": {
            "revenue_change_pct": -5.2
        }
    }
    
    print("🔧 Testing LLM Insights Generator...")
    print("Note: Requires OPENAI_API_KEY environment variable")
    
    if os.environ.get("OPENAI_API_KEY"):
        generator = SalesInsightsGenerator()
        insights = generator.analyze_sales_data(sample_data)
        print(f"\n📊 Summary: {insights.summary}")
    else:
        print("⚠️ Set OPENAI_API_KEY to run full test")
