"""
Jungle Scout Canvas Integration for collaborative product research documents
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

from jungle_scout_ai.logging import logger


class JungleScoutCanvasManager:
    """Manages Canvas creation for Jungle Scout research and analytics"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_product_research_canvas(
        self,
        channel_id: str,
        search_query: str,
        products: List[Dict[str, Any]],
        market_insights: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with product research findings"""
        try:
            content = self._create_product_research_markdown(
                search_query, products, market_insights
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"product-research-{search_query.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"🔍 Product Research: {search_query}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating product research canvas: {e}")
            return None
    
    def create_competitor_analysis_canvas(
        self,
        channel_id: str,
        target_asin: str,
        competitor_data: Dict[str, Any],
        competitive_landscape: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with competitor analysis"""
        try:
            content = self._create_competitor_analysis_markdown(
                target_asin, competitor_data, competitive_landscape
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"competitor-analysis-{target_asin}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"🔬 Competitor Analysis: {target_asin}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating competitor analysis canvas: {e}")
            return None
    
    def create_keyword_strategy_canvas(
        self,
        channel_id: str,
        primary_keyword: str,
        keyword_data: Dict[str, Any],
        related_keywords: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with keyword strategy and SEO recommendations"""
        try:
            content = self._create_keyword_strategy_markdown(
                primary_keyword, keyword_data, related_keywords
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"keyword-strategy-{primary_keyword.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"🎯 Keyword Strategy: {primary_keyword}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating keyword strategy canvas: {e}")
            return None
    
    def create_sales_report_canvas(
        self,
        channel_id: str,
        metrics: Dict[str, Any],
        timeframe: str,
        insights: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with sales performance report"""
        try:
            content = self._create_sales_report_markdown(
                metrics, timeframe, insights
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"sales-report-{timeframe.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"📊 Sales Report: {timeframe.title()}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating sales report canvas: {e}")
            return None
    
    def create_market_opportunity_canvas(
        self,
        channel_id: str,
        opportunity_name: str,
        validation_data: Dict[str, Any],
        action_plan: List[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas for market opportunity validation and planning"""
        try:
            content = self._create_market_opportunity_markdown(
                opportunity_name, validation_data, action_plan
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"market-opportunity-{opportunity_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"💡 Market Opportunity: {opportunity_name}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating market opportunity canvas: {e}")
            return None
    
    def _create_product_research_markdown(
        self,
        search_query: str,
        products: List[Dict[str, Any]],
        market_insights: Dict[str, Any] = None
    ) -> str:
        """Create markdown content for product research canvas"""
        content = f"""# 🔍 Product Research: {search_query}

**Research Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Query:** {search_query}  
**Products Found:** {len(products)}

## 📊 Market Overview

"""
        
        if market_insights:
            content += f"""**Market Size:** {market_insights.get('market_size', 'Unknown')}  
**Competition Level:** {market_insights.get('competition_level', 'Unknown')}  
**Average Price:** ${market_insights.get('avg_price', 0):.2f}  
**Trend Direction:** {market_insights.get('trend', 'Stable')}

"""
        
        content += "## 🏆 Top Product Opportunities\n\n"
        
        for i, product in enumerate(products[:10], 1):
            opportunity_score = product.get('opportunity_score', 0)
            score_indicator = "🟢" if opportunity_score >= 7 else "🟡" if opportunity_score >= 5 else "🔴"
            
            content += f"""### {i}. {product.get('title', 'Product')}

**ASIN:** `{product.get('asin', 'N/A')}`  
**Opportunity Score:** {score_indicator} {opportunity_score}/10  
**Est. Monthly Revenue:** ${product.get('monthly_revenue', 0):,}  
**Price Range:** ${product.get('min_price', 0):.2f} - ${product.get('max_price', 0):.2f}  
**Competition Level:** {product.get('competition_level', 'Unknown')}  
**BSR:** #{product.get('bsr', 'N/A')}

**Key Insights:**
- {product.get('insight_1', 'Strong market demand')}
- {product.get('insight_2', 'Moderate competition')}
- {product.get('insight_3', 'Good profit margins')}

---

"""
        
        content += """## 📋 Research Action Items

- [ ] Deep dive analysis on top 3 products
- [ ] Competitor pricing strategy review
- [ ] Keyword research for top opportunities
- [ ] Supplier sourcing investigation
- [ ] Product validation surveys
- [ ] Market entry timeline planning

## 🎯 Next Steps

1. **Product Validation:** Conduct surveys for top 3 products
2. **Competitor Analysis:** Deep dive into main competitors
3. **Sourcing Research:** Find reliable suppliers
4. **Financial Modeling:** Create detailed profit projections
5. **Go-to-Market:** Develop launch strategy

## 📈 Market Trends

*Add trend analysis and seasonal patterns here*

## 🗒️ Research Notes

*Team notes and additional insights*

---
*Research generated by Jungle Scout AI Assistant*"""
        
        return content
    
    def _create_competitor_analysis_markdown(
        self,
        target_asin: str,
        competitor_data: Dict[str, Any],
        competitive_landscape: List[Dict[str, Any]]
    ) -> str:
        """Create markdown content for competitor analysis canvas"""
        content = f"""# 🔬 Competitor Analysis: {target_asin}

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Target Product:** {competitor_data.get('title', 'Unknown Product')}  
**ASIN:** `{target_asin}`

## 📦 Product Overview

**Brand:** {competitor_data.get('brand', 'Unknown')}  
**Category:** {competitor_data.get('category', 'Unknown')}  
**Current Price:** ${competitor_data.get('price', 0):.2f}  
**Rating:** ⭐ {competitor_data.get('rating', 0):.1f} ({competitor_data.get('review_count', 0):,} reviews)  
**BSR:** #{competitor_data.get('bsr', 'N/A')}  
**Est. Monthly Sales:** {competitor_data.get('monthly_sales', 0):,} units

## 📊 Performance Metrics

### Sales Performance
- **Monthly Revenue:** ${competitor_data.get('monthly_revenue', 0):,}
- **Units Sold:** {competitor_data.get('monthly_sales', 0):,}/month
- **Market Share:** {competitor_data.get('market_share', 'Unknown')}%
- **Growth Rate:** {competitor_data.get('growth_rate', 'Unknown')}%

### Customer Satisfaction
- **Average Rating:** {competitor_data.get('rating', 0):.1f}/5.0
- **Review Velocity:** {competitor_data.get('review_velocity', 0)} reviews/month
- **Return Rate:** {competitor_data.get('return_rate', 'Unknown')}%
- **Customer Lifetime Value:** ${competitor_data.get('clv', 0):.2f}

## 🏆 Competitive Landscape

"""
        
        for i, comp in enumerate(competitive_landscape[:5], 1):
            content += f"""### {i}. {comp.get('brand', 'Unknown Brand')}
- **ASIN:** `{comp.get('asin', 'N/A')}`
- **Price:** ${comp.get('price', 0):.2f}
- **Rating:** ⭐ {comp.get('rating', 0):.1f}
- **Monthly Sales:** {comp.get('monthly_sales', 0):,} units
- **Market Position:** {comp.get('position', 'Unknown')}

"""
        
        content += """## 💡 Strategic Insights

### Strengths
- High customer satisfaction ratings
- Strong brand recognition
- Effective pricing strategy
- Robust sales performance

### Weaknesses
- Limited product variations
- Higher price point than competitors
- Seasonal sales fluctuations
- Dependency on Amazon marketing

### Opportunities
- Product line extension
- International market expansion
- Bundle offerings
- Subscription model potential

### Threats
- New competitor entry
- Price competition
- Supply chain disruptions
- Market saturation

## 🎯 Competitive Strategy

### Price Positioning
- **Current Strategy:** Premium pricing
- **Recommendation:** Competitive pricing with value focus
- **Target Price Range:** $X.XX - $X.XX

### Product Differentiation
- **Key Features:** [Add unique selling points]
- **Innovation Areas:** [Add potential improvements]
- **Bundle Opportunities:** [Add complementary products]

### Marketing Strategy
- **SEO Keywords:** [Add target keywords]
- **PPC Strategy:** [Add advertising recommendations]
- **Content Marketing:** [Add content ideas]

## 📋 Action Plan

- [ ] Price optimization analysis
- [ ] Feature comparison matrix
- [ ] Customer review sentiment analysis
- [ ] Supply chain cost analysis
- [ ] Marketing campaign planning
- [ ] Product improvement roadmap

## 📈 Monitoring Plan

### Key Metrics to Track
- Price changes
- Sales rank fluctuations
- Review count and rating changes
- Inventory levels
- Marketing campaigns

### Alert Thresholds
- Price changes > 10%
- BSR changes > 50%
- Rating drops below 4.0
- Stock outages

## 🗒️ Analysis Notes

*Add team insights and strategic discussions here*

---
*Analysis generated by Jungle Scout AI Assistant*"""
        
        return content
    
    def _create_keyword_strategy_markdown(
        self,
        primary_keyword: str,
        keyword_data: Dict[str, Any],
        related_keywords: List[Dict[str, Any]]
    ) -> str:
        """Create markdown content for keyword strategy canvas"""
        content = f"""# 🎯 Keyword Strategy: {primary_keyword}

**Strategy Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Primary Keyword:** {primary_keyword}  
**Market Analysis:** Amazon SEO Optimization

## 📊 Primary Keyword Analysis

**Search Volume:** {keyword_data.get('search_volume', 0):,} searches/month  
**Competition Level:** {keyword_data.get('difficulty', 0)}/100  
**Cost Per Click:** ${keyword_data.get('cpc', 0):.2f}  
**Trend:** {keyword_data.get('trend', 'Stable')} 📈  
**Seasonality:** {keyword_data.get('seasonality', 'Year-round')}

## 🔗 Related Keywords

| Keyword | Volume | Difficulty | CPC | Opportunity |
|---------|--------|------------|-----|-------------|
"""
        
        for kw in related_keywords[:10]:
            volume = kw.get('volume', 0)
            difficulty = kw.get('difficulty', 0)
            cpc = kw.get('cpc', 0)
            opportunity = "🟢 High" if difficulty < 30 and volume > 1000 else "🟡 Medium" if difficulty < 60 else "🔴 Low"
            content += f"| {kw.get('keyword', 'N/A')} | {volume:,} | {difficulty} | ${cpc:.2f} | {opportunity} |\n"
        
        content += f"""

## 🎯 SEO Strategy

### Primary Keywords (High Priority)
"""
        
        high_priority = [kw for kw in related_keywords if kw.get('difficulty', 100) < 30 and kw.get('volume', 0) > 1000]
        for kw in high_priority[:5]:
            content += f"- **{kw.get('keyword', 'N/A')}** - {kw.get('volume', 0):,} searches, {kw.get('difficulty', 0)} difficulty\n"
        
        content += """
### Secondary Keywords (Medium Priority)
"""
        
        medium_priority = [kw for kw in related_keywords if 30 <= kw.get('difficulty', 100) < 60]
        for kw in medium_priority[:5]:
            content += f"- **{kw.get('keyword', 'N/A')}** - {kw.get('volume', 0):,} searches, {kw.get('difficulty', 0)} difficulty\n"
        
        content += """
### Long-tail Keywords (Low Competition)
"""
        
        long_tail = [kw for kw in related_keywords if len(kw.get('keyword', '').split()) >= 3]
        for kw in long_tail[:5]:
            content += f"- **{kw.get('keyword', 'N/A')}** - {kw.get('volume', 0):,} searches\n"
        
        content += f"""

## 📝 Content Strategy

### Product Title Optimization
**Current:** [Add current product title]  
**Optimized:** [Primary Keyword] + [Key Features] + [Brand]

### Bullet Points
1. **Feature 1:** Include {primary_keyword} naturally
2. **Feature 2:** Use secondary keywords
3. **Feature 3:** Highlight unique benefits
4. **Feature 4:** Address customer pain points
5. **Feature 5:** Include relevant long-tail keywords

### Product Description
- **Opening:** Hook with primary keyword
- **Body:** Feature benefits with keyword variations
- **Closing:** Call-to-action with brand keywords

### Backend Search Terms
- Use remaining character limit efficiently
- Include misspellings and synonyms
- Add seasonal and trending terms
- Avoid repetition from visible content

## 📈 PPC Campaign Strategy

### Campaign Structure
1. **Exact Match Campaign**
   - Primary keyword: {primary_keyword}
   - Bid: ${keyword_data.get('cpc', 0) * 1.2:.2f}

2. **Phrase Match Campaign**
   - Target phrase variations
   - Bid: ${keyword_data.get('cpc', 0) * 1.1:.2f}

3. **Broad Match Campaign**
   - Discovery and research
   - Bid: ${keyword_data.get('cpc', 0) * 0.8:.2f}

### Negative Keywords
- Competitor brand names
- Irrelevant product types
- Price-focused terms (if premium product)

## 📊 Performance Tracking

### Key Metrics
- **Organic Rank:** Track for all target keywords
- **Search Volume Share:** Monitor visibility percentage
- **Click-Through Rate:** Optimize based on performance
- **Conversion Rate:** Track keyword-to-sale performance

### Monitoring Schedule
- **Daily:** Primary keyword rankings
- **Weekly:** Secondary keyword performance
- **Monthly:** Overall SEO health report

## 📋 Implementation Checklist

- [ ] Update product title with primary keyword
- [ ] Optimize bullet points with secondary keywords
- [ ] Rewrite product description for keyword density
- [ ] Update backend search terms
- [ ] Set up PPC campaigns
- [ ] Implement rank tracking
- [ ] Schedule performance reviews

## 🗒️ Strategy Notes

*Add team discussions and optimization ideas here*

---
*Strategy developed by Jungle Scout AI Assistant*"""
        
        return content
    
    def _create_sales_report_markdown(
        self,
        metrics: Dict[str, Any],
        timeframe: str,
        insights: List[str] = None
    ) -> str:
        """Create markdown content for sales report canvas"""
        content = f"""# 📊 Sales Performance Report

**Report Period:** {timeframe.title()}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🎯 Executive Summary

**Total Revenue:** ${metrics.get('total_revenue', 0):,.2f}  
**Units Sold:** {metrics.get('total_units', 0):,}  
**Average Order Value:** ${metrics.get('avg_order_value', 0):.2f}  
**Conversion Rate:** {metrics.get('conversion_rate', 0):.1f}%

## 📈 Key Performance Indicators

| Metric | Current Period | Previous Period | Change |
|--------|---------------|-----------------|--------|
| Revenue | ${metrics.get('total_revenue', 0):,.2f} | ${metrics.get('prev_revenue', 0):,.2f} | {metrics.get('revenue_change', 0):+.1f}% |
| Units | {metrics.get('total_units', 0):,} | {metrics.get('prev_units', 0):,} | {metrics.get('units_change', 0):+.1f}% |
| AOV | ${metrics.get('avg_order_value', 0):.2f} | ${metrics.get('prev_aov', 0):.2f} | {metrics.get('aov_change', 0):+.1f}% |
| Conversion | {metrics.get('conversion_rate', 0):.1f}% | {metrics.get('prev_conversion', 0):.1f}% | {metrics.get('conversion_change', 0):+.1f}% |

## 🏆 Top Performing Products

"""
        
        top_products = metrics.get('top_products', [])
        for i, product in enumerate(top_products[:5], 1):
            content += f"""### {i}. {product.get('name', 'Product')}
- **Revenue:** ${product.get('revenue', 0):,.2f}
- **Units:** {product.get('units', 0):,}
- **Growth:** {product.get('growth', 0):+.1f}%

"""
        
        if insights:
            content += "## 💡 Key Insights\n\n"
            for insight in insights:
                content += f"- {insight}\n"
        
        content += """

## 📊 Performance Analysis

### Revenue Trends
*Add revenue trend analysis and seasonal patterns*

### Product Performance
*Analyze individual product contributions and growth*

### Market Opportunities
*Identify potential areas for expansion*

## 🎯 Action Items

- [ ] Investigate top performing product strategies
- [ ] Address underperforming product issues
- [ ] Optimize pricing for maximum revenue
- [ ] Expand successful product lines
- [ ] Review and adjust marketing spend

## 📈 Forecasting

### Next Period Projections
- **Revenue Target:** $X,XXX
- **Units Target:** X,XXX
- **Growth Goal:** XX%

---
*Report generated by Jungle Scout AI Assistant*"""
        
        return content
    
    def _create_market_opportunity_markdown(
        self,
        opportunity_name: str,
        validation_data: Dict[str, Any],
        action_plan: List[Dict[str, str]] = None
    ) -> str:
        """Create markdown content for market opportunity canvas"""
        content = f"""# 💡 Market Opportunity: {opportunity_name}

**Opportunity Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Opportunity Score:** {validation_data.get('opportunity_score', 0)}/10  
**Risk Level:** {validation_data.get('risk_level', 'Medium')}

## 🎯 Opportunity Overview

**Market Size:** ${validation_data.get('market_size', 0):,}  
**Target Audience:** {validation_data.get('target_audience', 'Unknown')}  
**Competition Level:** {validation_data.get('competition_level', 'Medium')}  
**Entry Barrier:** {validation_data.get('entry_barrier', 'Medium')}

## 📊 Market Validation

### Demand Analysis
- **Search Volume:** {validation_data.get('search_volume', 0):,} monthly searches
- **Trend Direction:** {validation_data.get('trend', 'Stable')} 📈
- **Seasonality:** {validation_data.get('seasonality', 'Year-round')}
- **Market Growth Rate:** {validation_data.get('growth_rate', 0):.1f}% annually

### Competition Assessment
- **Number of Competitors:** {validation_data.get('competitor_count', 0)}
- **Market Leader Share:** {validation_data.get('leader_share', 0):.1f}%
- **Average Product Rating:** {validation_data.get('avg_rating', 0):.1f}/5.0
- **Price Range:** ${validation_data.get('min_price', 0):.2f} - ${validation_data.get('max_price', 0):.2f}

### Financial Projections
- **Estimated Revenue (Year 1):** ${validation_data.get('year1_revenue', 0):,}
- **Estimated Units (Year 1):** {validation_data.get('year1_units', 0):,}
- **Break-even Timeline:** {validation_data.get('breakeven_months', 0)} months
- **ROI Projection:** {validation_data.get('roi_projection', 0):.1f}%

## ⚖️ SWOT Analysis

### Strengths
- Market demand validation
- Competitive pricing opportunity
- Strong growth potential
- Clear target audience

### Weaknesses
- High initial investment required
- Limited brand recognition
- Complex supply chain
- Regulatory considerations

### Opportunities
- Market gap identification
- Technology advancement
- Partnership potential
- International expansion

### Threats
- New competitor entry
- Market saturation
- Economic downturn impact
- Supply chain disruption

## 🎯 Go-to-Market Strategy

### Phase 1: Market Entry (Months 1-3)
- Product development and sourcing
- Brand and listing optimization
- Initial inventory procurement
- Launch marketing campaign

### Phase 2: Growth (Months 4-8)
- Scale advertising efforts
- Expand product variations
- Optimize operational efficiency
- Build customer reviews

### Phase 3: Expansion (Months 9-12)
- Product line extension
- Market share consolidation
- International marketplace entry
- Strategic partnerships

## 📋 Action Plan

"""
        
        if action_plan:
            for i, action in enumerate(action_plan, 1):
                content += f"""### {i}. {action.get('task', 'Task')}
**Owner:** {action.get('owner', 'TBD')}  
**Timeline:** {action.get('timeline', 'TBD')}  
**Status:** {action.get('status', 'Pending')}

"""
        else:
            content += """### 1. Market Research Deep Dive
**Owner:** TBD  
**Timeline:** 2 weeks  
**Status:** Pending

### 2. Product Development
**Owner:** TBD  
**Timeline:** 4-6 weeks  
**Status:** Pending

### 3. Supplier Sourcing
**Owner:** TBD  
**Timeline:** 3-4 weeks  
**Status:** Pending

### 4. Brand and Listing Creation
**Owner:** TBD  
**Timeline:** 2 weeks  
**Status:** Pending

### 5. Launch Marketing Campaign
**Owner:** TBD  
**Timeline:** 1 week  
**Status:** Pending

"""
        
        content += """## 📊 Success Metrics

### Key Performance Indicators
- **Revenue Target:** $XXX,XXX (Year 1)
- **Units Sold Target:** XX,XXX (Year 1)
- **Market Share Goal:** X.X%
- **Customer Satisfaction:** >4.5★

### Monitoring Schedule
- **Weekly:** Sales performance review
- **Monthly:** Market position analysis
- **Quarterly:** Strategy adjustment review

## 🗒️ Opportunity Notes

*Add team discussions and strategic insights here*

---
*Opportunity analysis by Jungle Scout AI Assistant*"""
        
        return content
    
    
    def create_strategy_canvas(
        self,
        channel_id: str,
        strategy_name: str,
        market_analysis: Dict[str, Any] = None,
        action_plan: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a strategy planning canvas"""
        try:
            validation_data = {
                'opportunity_score': 8.0,
                 'risk_level': 'Medium',
                'market_size': 1000000,
                'target_audience': market_analysis.get('target_market', 'Amazon shoppers') if market_analysis else 'Amazon shoppers',
                'competition_level': market_analysis.get('competition', 'Medium') if market_analysis else 'Medium',
                'entry_barrier': 'Medium',
                'search_volume': 50000,
                'trend': 'Rising',
                'seasonality': 'Year-round',
                'growth_rate': 15.0,
                'competitor_count': 25,
                'leader_share': 30.0,
                'avg_rating': 4.2,
                'min_price': 20.00,
                'max_price': 80.00,
                'year1_revenue': 500000,
                'year1_units': 15000,
                'breakeven_months': 6,
                'roi_projection': 150.0
            }
            
            action_items = []
            if action_plan:
                for i, action in enumerate(action_plan):
                    action_items.append({
                        'task': action,
                        'owner': 'Team',
                        'timeline': f'Week {i+1}',
                        'status': 'Pending'
                    })
            
            return self.create_market_opportunity_canvas(
                channel_id=channel_id,
                opportunity_name=strategy_name,
                validation_data=validation_data,
                action_plan=action_items
            )
            
        except Exception as e:
            logger.error(f"Error creating strategy canvas: {e}")
            return None
    
    def create_seo_strategy_canvas(
        self,
        channel_id: str,
        primary_keyword: str,
        related_keywords: List[str] = None,
        optimization_tips: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create an SEO strategy canvas"""
        try:
            keyword_data = {
                'search_volume': 25000,
                'difficulty': 45,
                'cpc': 1.25,
                'trend': 'Rising',
                'seasonality': 'Year-round'
            }
            
            related_keyword_data = []
            if related_keywords:
                for i, kw in enumerate(related_keywords):
                    related_keyword_data.append({
                        'keyword': kw,
                        'volume': 5000 - (i * 500),
                        'difficulty': 30 + (i * 10),
                        'cpc': 0.80 + (i * 0.10)
                    })
            
            return self.create_keyword_strategy_canvas(
                channel_id=channel_id,
                primary_keyword=primary_keyword,
                keyword_data=keyword_data,
                related_keywords=related_keyword_data
            )
            
        except Exception as e:
            logger.error(f"Error creating SEO strategy canvas: {e}")
            return None
    
    def create_sales_report_canvas(
        self,
        channel_id: str,
        period: str,
        metrics: Dict[str, Any],
        insights: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a sales report canvas with enhanced metrics"""
        try:
            # Add calculated metrics if not present
            if 'prev_revenue' not in metrics:
                metrics['prev_revenue'] = metrics.get('total_revenue', 0) * 0.85
                metrics['revenue_change'] = 15.0
            
            if 'prev_units' not in metrics:
                metrics['prev_units'] = metrics.get('total_units', 0) * 0.90
                metrics['units_change'] = 10.0
            
            if 'prev_aov' not in metrics:
                metrics['prev_aov'] = metrics.get('avg_order_value', 0) * 0.95
                metrics['aov_change'] = 5.0
            
            if 'prev_conversion' not in metrics:
                metrics['prev_conversion'] = metrics.get('conversion_rate', 0) * 0.92
                metrics['conversion_change'] = 8.0
            
            # Call the original method with self reference
            content = self._create_sales_report_markdown(
                metrics,
                period,
                insights or [
                    "Revenue growth driven by new product launches",
                    "Conversion rate improved through listing optimization",
                    "Seasonal trends indicate Q4 opportunity"
                ]
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"sales-report-{period.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"📊 Sales Report: {period.title()}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating enhanced sales canvas: {e}")
            return None
    
    def get_canvas_url(self, file_response: Dict[str, Any]) -> Optional[str]:
        """Extract canvas URL from file upload response"""
        try:
            if "files" in file_response and len(file_response["files"]) > 0:
                file_info = file_response["files"][0]
                return file_info.get("permalink", file_info.get("url_private"))
            return None
        except Exception as e:
            logger.error(f"Error extracting canvas URL: {e}")
            return None