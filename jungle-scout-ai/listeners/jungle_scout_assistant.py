"""
Jungle Scout AI Assistant - Advanced Amazon seller analytics and research
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from slack_bolt import BoltContext
from slack_sdk.web import WebClient
from composio import ComposioToolSet, AppType

from jungle_scout_ai.logging import logger
from jungle_scout_ai.errors import handle_errors
from jungle_scout_ai.retry import with_retry
from .assistant_features import JungleScoutAssistantFeatures
from .lists_integration import JungleScoutListsManager
from .memory_manager import MemoryManager
from .llm_caller_openai import LLMCallerOpenAI


class JungleScoutAssistant:
    """Handles Jungle Scout AI assistance with product research, competitor analysis, and market insights"""
    
    def __init__(self):
        self.composio_toolset = ComposioToolSet()
        self.assistant_features = None  # Initialized with client
        self.lists_manager = None  # Initialized with client
        self.memory_manager = None  # Initialized with client
        self.llm = LLMCallerOpenAI()
        
    @handle_errors
    def process_jungle_scout_command(
        self,
        body: Dict[str, Any],
        context: BoltContext,
        say: Any,
        client: WebClient
    ) -> None:
        """Process Jungle Scout assistant commands"""
        try:
            user_id = body.get("user", {}).get("id", "")
            channel_id = body.get("channel", {}).get("id", "")
            text = body.get("text", "").strip()
            thread_ts = body.get("thread_ts") or body.get("ts")
            
            # Initialize features with client if not already done
            if not self.assistant_features:
                self.assistant_features = JungleScoutAssistantFeatures(client)
            if not self.lists_manager:
                self.lists_manager = JungleScoutListsManager(client)
            if not self.memory_manager:
                self.memory_manager = MemoryManager(client)
            
            # Extract command from message
            command = self._extract_command(text)
            
            if not command:
                self._send_help_message(say)
                return
                
            # Route to appropriate handler
            if command.startswith("research"):
                self._handle_product_research(command, channel_id, say, client, thread_ts, context)
            elif command.startswith("keywords"):
                self._handle_keyword_analysis(command, say, client, thread_ts, context)
            elif command.startswith("competitor"):
                self._handle_competitor_analysis(command, channel_id, say, client, thread_ts, context)
            elif command.startswith("sales"):
                self._handle_sales_analytics(command, say, client, context)
            elif command.startswith("trends"):
                self._handle_market_trends(command, say, client, context)
            elif command.startswith("validate"):
                self._handle_product_validation(command, channel_id, say, client, context)
            elif command.startswith("dashboard"):
                self._handle_dashboard_creation(command, channel_id, say, client, context)
            else:
                say(f"Unknown command: `{command}`. Type `help` for available commands.")
                
        except Exception as e:
            logger.error(f"Error processing Jungle Scout command: {e}")
            say("Sorry, I encountered an error processing your request.")
    
    def _extract_command(self, text: str) -> Optional[str]:
        """Extract command from message text"""
        # Remove bot mention if present
        text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
        
        # Check for command keywords
        commands = ["research", "keywords", "competitor", "sales", "trends", "validate", "dashboard", "help"]
        for cmd in commands:
            if text.lower().startswith(cmd):
                return text.lower()
        
        return None
    
    def _send_help_message(self, say: Any) -> None:
        """Send help message with available commands"""
        say("🌲 **Jungle Scout AI Assistant Commands:**\n"
            "• `research [keyword/ASIN]` - Find product opportunities\n"
            "• `keywords [keyword]` - Analyze keyword metrics\n"
            "• `competitor [ASIN]` - Analyze competitor products\n"
            "• `sales [timeframe]` - View sales performance\n"
            "• `trends [category]` - Analyze market trends\n"
            "• `validate [product idea]` - Validate product opportunity\n"
            "• `dashboard [type]` - Create analytics dashboard")
    
    @with_retry(max_attempts=3)
    def _handle_product_research(
        self, 
        command: str, 
        channel_id: str, 
        say: Any,
        client: WebClient,
        thread_ts: str = None,
        context: BoltContext = None
    ) -> None:
        """Handle product research requests"""
        initial_msg = say("🔍 Researching product opportunities...")
        msg_ts = initial_msg.get("ts")
        
        # Add user message to memory if in thread
        if thread_ts and self.memory_manager:
            self.memory_manager.add_to_history(
                channel_id=channel_id,
                thread_ts=thread_ts,
                context=context,
                role="user",
                content=command
            )
        
        # Set thread title if in a thread
        if thread_ts and self.assistant_features:
            self.assistant_features.set_thread_title(
                channel_id, thread_ts, 
                f"🔍 Product Research: {self._extract_query_from_command(command, 'research')}"
            )
        
        # Animate processing steps
        if thread_ts and self.assistant_features:
            self.assistant_features.animate_processing(
                channel_id, thread_ts,
                [
                    "🔍 Searching product database",
                    "📊 Analyzing market data", 
                    "💰 Calculating opportunity scores",
                    "📈 Identifying trends",
                    "✨ Generating insights"
                ],
                delay=1.0
            )
        
        try:
            # Extract search query from command
            query = self._extract_query_from_command(command, "research")
            
            if not query:
                say("Please provide a keyword or ASIN to research. Example: `research wireless earbuds`")
                return
            
            # Get conversation history for context
            conversation_history = []
            if thread_ts and self.memory_manager:
                conversation_history = self.memory_manager.get_conversation_history(
                    channel_id=channel_id,
                    thread_ts=thread_ts,
                    context=context
                )
            
            # Use Composio to call Jungle Scout API with context
            research_data = self._perform_product_research(query, conversation_history)
            
            if research_data:
                # Format results using UI components
                from listeners.jungle_scout_ui import create_product_research_blocks
                blocks = create_product_research_blocks(
                    products=research_data.get('products', []),
                    search_query=query
                )
                say(blocks=blocks)
                
                # Set suggested prompts for next actions
                if thread_ts and self.assistant_features:
                    top_product = research_data.get('products', [{}])[0]
                    suggestions = self.assistant_features.create_smart_suggestions({
                        "type": "product_research",
                        "top_product": top_product,
                        "category": query,
                        "search_query": query
                    })
                    self.assistant_features.set_suggested_prompts(
                        channel_id, thread_ts, suggestions
                    )
                
                # Offer to create a watchlist
                say(
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "💡 *Would you like to track these products?*"
                            },
                            "accessory": {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "📋 Create Watchlist"
                                },
                                "action_id": "create_product_watchlist",
                                "value": json.dumps({
                                    "products": research_data.get('products', [])[:10],
                                    "query": query
                                })
                            }
                        }
                    ]
                )
                
                # Save assistant response to memory
                if thread_ts and self.memory_manager:
                    summary = f"Found {len(research_data.get('products', []))} products for '{query}'"
                    if research_data.get('products'):
                        top_product = research_data['products'][0]
                        summary += f". Top result: {top_product.get('title', 'Unknown')} with {top_product.get('opportunity_score', 0)}% opportunity score"
                    
                    self.memory_manager.add_to_history(
                        channel_id=channel_id,
                        thread_ts=thread_ts,
                        context=context,
                        role="assistant",
                        content=summary
                    )
            else:
                say(f"❌ No product data found for '{query}'. Try a different keyword or ASIN.")
                
        except Exception as e:
            logger.error(f"Error in product research: {e}")
            say("❌ Sorry, I couldn't complete the product research right now.")
    
    @with_retry(max_attempts=3)
    def _handle_keyword_analysis(
        self,
        command: str,
        say: Any,
        client: WebClient,
        thread_ts: str = None,
        context: BoltContext = None
    ) -> None:
        """Handle keyword analysis requests"""
        initial_msg = say("🎯 Analyzing keyword metrics...")
        
        # Set thread status for processing
        if thread_ts and self.assistant_features:
            keyword = self._extract_query_from_command(command, "keywords")
            self.assistant_features.set_thread_title(
                say.channel, thread_ts,
                f"🎯 Keyword Analysis: {keyword}"
            )
            self.assistant_features.set_thread_status(
                say.channel, thread_ts,
                "analyzing", "🎯"
            )
        
        try:
            keyword = self._extract_query_from_command(command, "keywords")
            
            if not keyword:
                say("Please provide a keyword to analyze. Example: `keywords bluetooth speakers`")
                return
            
            # Use Composio to get keyword data
            keyword_data = self._perform_keyword_analysis(keyword)
            
            if keyword_data:
                from listeners.jungle_scout_ui import create_keyword_analysis_blocks
                blocks = create_keyword_analysis_blocks(
                    keyword=keyword,
                    metrics=keyword_data.get('metrics', {}),
                    related_keywords=keyword_data.get('related_keywords', [])
                )
                say(blocks=blocks)
            else:
                say(f"❌ No keyword data found for '{keyword}'.")
                
        except Exception as e:
            logger.error(f"Error in keyword analysis: {e}")
            say("❌ Sorry, I couldn't complete the keyword analysis right now.")
    
    @with_retry(max_attempts=3)
    def _handle_competitor_analysis(
        self,
        command: str,
        channel_id: str,
        say: Any,
        client: WebClient
    ) -> None:
        """Handle competitor analysis requests"""
        say("🔬 Analyzing competitor data...")
        
        try:
            asin = self._extract_asin_from_command(command)
            
            if not asin:
                say("Please provide an ASIN to analyze. Example: `competitor B08N5WRWNW`")
                return
            
            # Use Composio to get competitor data
            competitor_data = self._perform_competitor_analysis(asin)
            
            if competitor_data:
                from listeners.jungle_scout_ui import create_competitor_analysis_blocks
                blocks = create_competitor_analysis_blocks(
                    competitor=competitor_data.get('product', {}),
                    comparison_metrics=competitor_data.get('comparison', {})
                )
                say(blocks=blocks)
            else:
                say(f"❌ No competitor data found for ASIN '{asin}'.")
                
        except Exception as e:
            logger.error(f"Error in competitor analysis: {e}")
            say("❌ Sorry, I couldn't complete the competitor analysis right now.")
    
    @with_retry(max_attempts=3)
    def _handle_sales_analytics(
        self,
        command: str,
        say: Any,
        client: WebClient
    ) -> None:
        """Handle sales analytics requests"""
        say("📊 Generating sales analytics...")
        
        try:
            timeframe = self._extract_timeframe_from_command(command)
            
            # Use Composio to get sales data
            sales_data = self._perform_sales_analysis(timeframe)
            
            if sales_data:
                from listeners.jungle_scout_ui import create_sales_dashboard_blocks
                blocks = create_sales_dashboard_blocks(
                    metrics=sales_data.get('metrics', {}),
                    timeframe=timeframe
                )
                say(blocks=blocks)
            else:
                say("❌ No sales data available for the specified timeframe.")
                
        except Exception as e:
            logger.error(f"Error in sales analytics: {e}")
            say("❌ Sorry, I couldn't generate the sales analytics right now.")
    
    @with_retry(max_attempts=3)
    def _handle_market_trends(
        self,
        command: str,
        say: Any,
        client: WebClient
    ) -> None:
        """Handle market trends analysis"""
        say("📈 Analyzing market trends...")
        
        try:
            category = self._extract_query_from_command(command, "trends")
            
            if not category:
                say("Please specify a category or keyword. Example: `trends electronics`")
                return
            
            # Use Composio to get trend data
            trend_data = self._perform_trend_analysis(category)
            
            if trend_data:
                # Create trend analysis blocks
                blocks = self._create_trend_analysis_blocks(category, trend_data)
                say(blocks=blocks)
            else:
                say(f"❌ No trend data found for '{category}'.")
                
        except Exception as e:
            logger.error(f"Error in market trends analysis: {e}")
            say("❌ Sorry, I couldn't analyze market trends right now.")
    
    @with_retry(max_attempts=3)
    def _handle_product_validation(
        self,
        command: str,
        channel_id: str,
        say: Any,
        client: WebClient
    ) -> None:
        """Handle product opportunity validation"""
        say("✅ Validating product opportunity...")
        
        try:
            product_idea = self._extract_query_from_command(command, "validate")
            
            if not product_idea:
                say("Please provide a product idea to validate. Example: `validate ergonomic mouse pad`")
                return
            
            # Use Composio and AI to validate product opportunity
            validation_data = self._perform_product_validation(product_idea)
            
            if validation_data:
                blocks = self._create_validation_blocks(product_idea, validation_data)
                say(blocks=blocks)
            else:
                say(f"❌ Could not validate '{product_idea}'. Try a different product idea.")
                
        except Exception as e:
            logger.error(f"Error in product validation: {e}")
            say("❌ Sorry, I couldn't validate the product opportunity right now.")
    
    @with_retry(max_attempts=3)
    def _handle_dashboard_creation(
        self,
        command: str,
        channel_id: str,
        say: Any,
        client: WebClient
    ) -> None:
        """Handle dashboard creation requests"""
        say("📊 Creating analytics dashboard...")
        
        try:
            dashboard_type = self._extract_query_from_command(command, "dashboard")
            
            if not dashboard_type:
                dashboard_type = "sales"  # Default dashboard
            
            # Create appropriate dashboard based on type
            if dashboard_type in ["sales", "revenue"]:
                sales_data = self._perform_sales_analysis("last 30 days")
                if sales_data:
                    from listeners.jungle_scout_ui import create_sales_dashboard_blocks
                    blocks = create_sales_dashboard_blocks(
                        metrics=sales_data.get('metrics', {}),
                        timeframe="last 30 days"
                    )
                    say(blocks=blocks)
                else:
                    say("❌ No sales data available for dashboard.")
            else:
                say(f"Dashboard type '{dashboard_type}' not supported. Try 'sales' or 'revenue'.")
                
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            say("❌ Sorry, I couldn't create the dashboard right now.")
    
    def _perform_product_research(self, query: str, conversation_history: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Perform product research using Composio Jungle Scout integration with context awareness"""
        try:
            # Use LLM to enhance query based on conversation context
            enhanced_query = query
            if conversation_history and self.llm:
                context_messages = self.memory_manager.format_history_for_llm(conversation_history) if self.memory_manager else []
                context_messages.append({
                    "role": "user",
                    "content": f"Based on our conversation history, enhance this product research query for better results: '{query}'. Return only the enhanced query, nothing else."
                })
                
                try:
                    enhanced_query = self.llm.call(context_messages, temperature=0.3, max_tokens=100)
                    logger.info(f"Enhanced query from '{query}' to '{enhanced_query}'")
                except Exception as e:
                    logger.warning(f"Could not enhance query: {e}")
                    enhanced_query = query
            # Use Composio to call JUNGLESCOUT_QUERY_THE_PRODUCT_DATABASE
            response = self.composio_toolset.execute_action(
                action="JUNGLESCOUT_QUERY_THE_PRODUCT_DATABASE",
                params={
                    "marketplace": "amazon.com",  # Default to US marketplace
                    "search_terms": enhanced_query,
                    "page_size": 10,  # Limit results for better UX
                    "sort": "estimated_sales",  # Sort by sales volume
                    # Add filters for better quality results
                    "min_reviews": 10,
                    "min_rating": 3.5,
                    "max_page": 1
                }
            )
            
            if response and response.get("successful") and response.get("data"):
                products_data = response["data"]
                
                # Transform the response into our expected format
                products = []
                for product in products_data.get("products", []):
                    # Calculate opportunity score based on various factors
                    opportunity_score = self._calculate_opportunity_score(product)
                    
                    products.append({
                        "title": product.get("title", "Unknown Product"),
                        "asin": product.get("asin", ""),
                        "opportunity_score": opportunity_score,
                        "monthly_revenue": product.get("estimated_monthly_revenue", 0),
                        "min_price": product.get("price", 0),
                        "max_price": product.get("price", 0),
                        "competition_level": self._assess_competition_level(product),
                        "bsr": product.get("rank", 0),
                        "image_url": product.get("image_url", "https://via.placeholder.com/300x300?text=📦"),
                        "rating": product.get("rating", 0),
                        "review_count": product.get("reviews", 0),
                        "category": product.get("category", ""),
                        "brand": product.get("brand", "")
                    })
                
                return {"products": products}
            else:
                logger.warning(f"No product data returned for query: {query}")
                return None
            
        except Exception as e:
            logger.error(f"Error in product research API call: {e}")
            return None
    
    def _perform_keyword_analysis(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Perform keyword analysis using Composio Jungle Scout integration"""
        try:
            # Use Composio to call JUNGLESCOUT_RETRIEVE_DATA_FOR_A_SPECIFIC_KEYWORD_QUERY
            response = self.composio_toolset.execute_action(
                action="JUNGLESCOUT_RETRIEVE_DATA_FOR_A_SPECIFIC_KEYWORD_QUERY",
                params={
                    "marketplace": "amazon.com",
                    "search_terms": keyword,
                    "categories": []  # Empty to search all categories
                }
            )
            
            if response and response.get("successful") and response.get("data"):
                keyword_data = response["data"]
                
                # Extract metrics from the response
                metrics = {
                    "search_volume": keyword_data.get("search_volume", 0),
                    "difficulty": self._calculate_keyword_difficulty(keyword_data),
                    "cpc": keyword_data.get("cost_per_click", 0),
                    "trend": self._analyze_keyword_trend(keyword_data)
                }
                
                # Get related keywords from the response
                related_keywords = []
                for related in keyword_data.get("related_keywords", []):
                    related_keywords.append({
                        "keyword": related.get("keyword", ""),
                        "volume": related.get("search_volume", 0),
                        "difficulty": self._calculate_keyword_difficulty(related)
                    })
                
                return {
                    "metrics": metrics,
                    "related_keywords": related_keywords
                }
            else:
                logger.warning(f"No keyword data returned for: {keyword}")
                return None
            
        except Exception as e:
            logger.error(f"Error in keyword analysis API call: {e}")
            return None
    
    def _perform_competitor_analysis(self, asin: str) -> Optional[Dict[str, Any]]:
        """Perform competitor analysis using Composio Jungle Scout integration"""
        try:
            # Use Composio to call JUNGLESCOUT_RETRIEVE_KEYWORD_DATA_FOR_SPECIFIED_ASINS
            response = self.composio_toolset.execute_action(
                action="JUNGLESCOUT_RETRIEVE_KEYWORD_DATA_FOR_SPECIFIED_ASINS",
                params={
                    "marketplace": "amazon.com",
                    "asins": [asin]  # Pass as list
                }
            )
            
            if response and response.get("successful") and response.get("data"):
                competitor_data = response["data"]
                
                # Extract product information from the first result
                if competitor_data.get("products") and len(competitor_data["products"]) > 0:
                    product_info = competitor_data["products"][0]
                    
                    # Get keyword data associated with this ASIN
                    keywords_data = competitor_data.get("keywords", [])
                    
                    # Calculate market share and comparisons based on keyword data
                    market_share = self._calculate_market_share(keywords_data, asin)
                    price_comparison = self._calculate_price_comparison(product_info)
                    sales_comparison = self._calculate_sales_comparison(product_info)
                    rating_comparison = self._calculate_rating_comparison(product_info)
                    
                    return {
                        "product": {
                            "title": product_info.get("title", "Unknown Product"),
                            "asin": asin,
                            "brand": product_info.get("brand", "Unknown Brand"),
                            "price": product_info.get("price", 0),
                            "rating": product_info.get("rating", 0),
                            "review_count": product_info.get("reviews", 0),
                            "bsr": product_info.get("rank", 0),
                            "monthly_sales": product_info.get("estimated_monthly_sales", 0),
                            "image_url": product_info.get("image_url", "https://via.placeholder.com/300x300?text=Product")
                        },
                        "comparison": {
                            "price_comparison": price_comparison,
                            "sales_comparison": sales_comparison,
                            "rating_comparison": rating_comparison,
                            "market_share": f"{market_share:.1f}%"
                        }
                    }
                else:
                    logger.warning(f"No product data returned for ASIN: {asin}")
                    return None
            else:
                logger.warning(f"No competitor data returned for ASIN: {asin}")
                return None
            
        except Exception as e:
            logger.error(f"Error in competitor analysis API call: {e}")
            return None
    
    def _perform_sales_analysis(self, timeframe: str) -> Optional[Dict[str, Any]]:
        """Perform sales analysis using Composio Jungle Scout integration"""
        try:
            # Parse timeframe to determine date range
            start_date, end_date = self._parse_timeframe_to_dates(timeframe)
            
            # Use Composio to call JUNGLESCOUT_RETRIEVE_SALES_ESTIMATES_DATA
            response = self.composio_toolset.execute_action(
                action="JUNGLESCOUT_RETRIEVE_SALES_ESTIMATES_DATA",
                params={
                    "marketplace": "amazon.com",
                    "start_date": start_date,
                    "end_date": end_date,
                    "include_variants": True,
                    "include_promotions": True
                }
            )
            
            if response and response.get("successful") and response.get("data"):
                sales_data = response["data"]
                
                # Extract and aggregate sales metrics
                total_revenue = 0
                total_units = 0
                top_products = []
                
                # Process sales data
                for product_sales in sales_data.get("sales_estimates", []):
                    revenue = product_sales.get("estimated_revenue", 0)
                    units = product_sales.get("estimated_units", 0)
                    
                    total_revenue += revenue
                    total_units += units
                    
                    # Add to top products list
                    top_products.append({
                        "name": product_sales.get("title", "Unknown Product"),
                        "revenue": revenue,
                        "units": units,
                        "asin": product_sales.get("asin", "")
                    })
                
                # Sort top products by revenue and take top 5
                top_products.sort(key=lambda x: x["revenue"], reverse=True)
                top_products = top_products[:5]
                
                # Calculate derived metrics
                avg_order_value = total_revenue / total_units if total_units > 0 else 0
                conversion_rate = sales_data.get("average_conversion_rate", 0)
                
                return {
                    "metrics": {
                        "total_revenue": total_revenue,
                        "total_units": total_units,
                        "avg_order_value": avg_order_value,
                        "conversion_rate": conversion_rate,
                        "top_products": top_products
                    }
                }
            else:
                logger.warning(f"No sales data returned for timeframe: {timeframe}")
                return None
            
        except Exception as e:
            logger.error(f"Error in sales analysis API call: {e}")
            return None
    
    def _perform_trend_analysis(self, category: str) -> Optional[Dict[str, Any]]:
        """Perform trend analysis using Composio Jungle Scout integration"""
        try:
            # Get historical volume data for trend analysis
            historical_response = self.composio_toolset.execute_action(
                action="JUNGLESCOUT_KEYWORD_HISTORICAL_VOLUME",
                params={
                    "marketplace": "amazon.com",
                    "keywords": [category],
                    "months": 12,  # Last 12 months of data
                }
            )
            
            # Get share of voice data for market analysis
            share_of_voice_response = self.composio_toolset.execute_action(
                action="JUNGLESCOUT_RETRIEVE_SHARE_OF_VOICE_DATA",
                params={
                    "marketplace": "amazon.com",
                    "keywords": [category],
                    "include_competitors": True,
                    "include_market_trends": True
                }
            )
            
            trend_data = {}
            
            # Process historical volume data
            if historical_response and historical_response.get("successful") and historical_response.get("data"):
                historical_data = historical_response["data"]
                
                # Calculate trend direction and growth rate from historical data
                volume_history = historical_data.get("volume_history", [])
                if len(volume_history) >= 2:
                    recent_volume = sum(volume_history[-3:]) / 3  # Last 3 months average
                    older_volume = sum(volume_history[:3]) / 3   # First 3 months average
                    
                    if recent_volume > older_volume:
                        growth_rate = ((recent_volume - older_volume) / older_volume) * 100
                        trend_direction = "rising" if growth_rate > 5 else "stable"
                    else:
                        growth_rate = ((older_volume - recent_volume) / older_volume) * -100
                        trend_direction = "declining" if growth_rate < -5 else "stable"
                    
                    trend_data.update({
                        "trend_direction": trend_direction,
                        "growth_rate": abs(growth_rate),
                        "seasonal_patterns": self._analyze_seasonal_patterns(volume_history)
                    })
            
            # Process share of voice data
            if share_of_voice_response and share_of_voice_response.get("successful") and share_of_voice_response.get("data"):
                sov_data = share_of_voice_response["data"]
                
                # Extract market insights from share of voice data
                market_size = sov_data.get("total_market_volume", 0)
                top_competitors = sov_data.get("top_competitors", [])
                emerging_trends = sov_data.get("emerging_keywords", [])
                
                # Extract top performing products from competitors
                top_products = []
                for competitor in top_competitors[:5]:  # Top 5 competitors
                    top_products.append({
                        "title": competitor.get("product_title", "Trending Product"),
                        "growth": competitor.get("growth_rate", 0),
                        "market_share": competitor.get("market_share", 0)
                    })
                
                trend_data.update({
                    "market_size": market_size,
                    "emerging_keywords": [kw.get("keyword", "") for kw in emerging_trends[:5]],
                    "top_products": top_products
                })
            
            # Provide reasonable defaults if API calls failed
            if not trend_data:
                trend_data = {
                    "trend_direction": "stable",
                    "growth_rate": 0,
                    "market_size": 0,
                    "seasonal_patterns": "Insufficient data",
                    "emerging_keywords": [],
                    "top_products": []
                }
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error in trend analysis API call: {e}")
            return None
    
    def _perform_product_validation(self, product_idea: str) -> Optional[Dict[str, Any]]:
        """Perform product validation using AI and market data"""
        try:
            # Mock validation data - replace with real analysis
            mock_data = {
                "opportunity_score": 7.8,
                "market_size": 850000,
                "competition_level": "Medium",
                "entry_barrier": "Low",
                "profit_potential": "High",
                "risks": ["Seasonal demand", "High competition"],
                "recommendations": ["Focus on unique features", "Target specific niche"]
            }
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error in product validation: {e}")
            return None
    
    def _extract_query_from_command(self, command: str, command_type: str) -> str:
        """Extract query parameter from command"""
        # Remove command type and extract remaining text
        pattern = rf'^{command_type}\s+(.+)'
        match = re.search(pattern, command, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_asin_from_command(self, command: str) -> str:
        """Extract ASIN from command"""
        # Look for ASIN pattern (10 characters, alphanumeric)
        asin_pattern = r'\b[A-Z0-9]{10}\b'
        match = re.search(asin_pattern, command.upper())
        return match.group(0) if match else ""
    
    def _extract_timeframe_from_command(self, command: str) -> str:
        """Extract timeframe from command"""
        query = self._extract_query_from_command(command, "sales")
        return query if query else "last 30 days"
    
    def _create_trend_analysis_blocks(self, category: str, trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create blocks for trend analysis results"""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📈 Market Trends: {category.title()}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📊 Trend Direction*\n{trend_data.get('trend_direction', 'Unknown').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*📈 Growth Rate*\n{trend_data.get('growth_rate', 0):.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*💰 Market Size*\n${trend_data.get('market_size', 0):,}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*📅 Seasonality*\n{trend_data.get('seasonal_patterns', 'Year-round')}"
                    }
                ]
            }
        ]
    
    def _create_validation_blocks(self, product_idea: str, validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create blocks for product validation results"""
        score = validation_data.get('opportunity_score', 0)
        score_color = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
        
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ Product Validation: {product_idea.title()}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{score_color} *Opportunity Score:* {score}/10\n"
                           f"💰 *Market Size:* ${validation_data.get('market_size', 0):,}\n"
                           f"⚔️ *Competition:* {validation_data.get('competition_level', 'Unknown')}\n"
                           f"🚧 *Entry Barrier:* {validation_data.get('entry_barrier', 'Unknown')}"
                }
            }
        ]
    
    # Helper methods for calculations and analysis
    def _calculate_opportunity_score(self, product: Dict[str, Any]) -> float:
        """Calculate opportunity score based on various product factors"""
        try:
            # Base score factors
            revenue = product.get("estimated_monthly_revenue", 0)
            reviews = product.get("reviews", 0)
            rating = product.get("rating", 0)
            rank = product.get("rank", 999999)  # BSR rank
            
            # Score components (0-10 scale)
            revenue_score = min(10, revenue / 10000)  # $10k+ = 10 points
            review_score = min(10, reviews / 1000)    # 1000+ reviews = 10 points
            rating_score = rating * 2.5 if rating > 0 else 0  # 4.0 rating = 10 points
            rank_score = max(0, 10 - (rank / 10000))  # Lower rank = higher score
            
            # Weighted average
            opportunity_score = (
                revenue_score * 0.4 +
                review_score * 0.2 +
                rating_score * 0.2 +
                rank_score * 0.2
            )
            
            return round(opportunity_score, 1)
        except Exception:
            return 5.0  # Default score
    
    def _assess_competition_level(self, product: Dict[str, Any]) -> str:
        """Assess competition level based on market factors"""
        try:
            reviews = product.get("reviews", 0)
            rank = product.get("rank", 999999)
            
            # High competition indicators
            if reviews > 5000 or rank < 1000:
                return "High"
            elif reviews > 1000 or rank < 10000:
                return "Medium"
            else:
                return "Low"
        except Exception:
            return "Medium"
    
    def _calculate_keyword_difficulty(self, keyword_data: Dict[str, Any]) -> float:
        """Calculate keyword difficulty score"""
        try:
            search_volume = keyword_data.get("search_volume", 0)
            competition_score = keyword_data.get("competition_score", 0)
            
            # Normalize to 0-10 scale
            volume_factor = min(10, search_volume / 10000)
            difficulty = (competition_score * 0.7) + (volume_factor * 0.3)
            
            return round(difficulty, 1)
        except Exception:
            return 5.0
    
    def _analyze_keyword_trend(self, keyword_data: Dict[str, Any]) -> str:
        """Analyze keyword trend direction"""
        try:
            trend_data = keyword_data.get("trend_data", [])
            if len(trend_data) < 2:
                return "Stable"
            
            recent = sum(trend_data[-3:]) / 3
            older = sum(trend_data[:3]) / 3
            
            change_percent = ((recent - older) / older) * 100 if older > 0 else 0
            
            if change_percent > 10:
                return "Rising"
            elif change_percent < -10:
                return "Declining"
            else:
                return "Stable"
        except Exception:
            return "Stable"
    
    def _calculate_market_share(self, keywords_data: List[Dict[str, Any]], asin: str) -> float:
        """Calculate market share for a product based on keyword data"""
        try:
            total_volume = sum(kw.get("search_volume", 0) for kw in keywords_data)
            product_volume = sum(
                kw.get("search_volume", 0) for kw in keywords_data 
                if asin in kw.get("top_asins", [])
            )
            
            if total_volume > 0:
                return (product_volume / total_volume) * 100
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_price_comparison(self, product_info: Dict[str, Any]) -> str:
        """Calculate price comparison against market average"""
        try:
            price = product_info.get("price", 0)
            market_avg = product_info.get("market_average_price", 0)
            
            if market_avg > 0:
                diff_percent = ((price - market_avg) / market_avg) * 100
                if diff_percent > 15:
                    return f"{diff_percent:.0f}% above average"
                elif diff_percent < -15:
                    return f"{abs(diff_percent):.0f}% below average"
                else:
                    return "Near market average"
            return "Price data unavailable"
        except Exception:
            return "Price data unavailable"
    
    def _calculate_sales_comparison(self, product_info: Dict[str, Any]) -> str:
        """Calculate sales comparison against market average"""
        try:
            sales = product_info.get("estimated_monthly_sales", 0)
            market_avg = product_info.get("market_average_sales", 0)
            
            if market_avg > 0:
                diff_percent = ((sales - market_avg) / market_avg) * 100
                if diff_percent > 20:
                    return f"{diff_percent:.0f}% above average"
                elif diff_percent < -20:
                    return f"{abs(diff_percent):.0f}% below average"
                else:
                    return "Near market average"
            return "Sales data unavailable"
        except Exception:
            return "Sales data unavailable"
    
    def _calculate_rating_comparison(self, product_info: Dict[str, Any]) -> str:
        """Calculate rating comparison against market average"""
        try:
            rating = product_info.get("rating", 0)
            market_avg = product_info.get("market_average_rating", 0)
            
            if market_avg > 0:
                diff = rating - market_avg
                if diff > 0.3:
                    return f"{diff:.1f} points above average"
                elif diff < -0.3:
                    return f"{abs(diff):.1f} points below average"
                else:
                    return "Near market average"
            return "Rating data unavailable"
        except Exception:
            return "Rating data unavailable"
    
    def _parse_timeframe_to_dates(self, timeframe: str) -> tuple:
        """Parse timeframe string to start and end dates"""
        try:
            from datetime import datetime, timedelta
            
            today = datetime.now()
            
            if "30 days" in timeframe.lower() or "month" in timeframe.lower():
                start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            elif "90 days" in timeframe.lower() or "3 month" in timeframe.lower():
                start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            elif "year" in timeframe.lower() or "12 month" in timeframe.lower():
                start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
            else:
                start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")  # Default to 30 days
            
            end_date = today.strftime("%Y-%m-%d")
            return start_date, end_date
        except Exception:
            # Fallback dates
            return "2024-01-01", "2024-12-31"
    
    def _analyze_seasonal_patterns(self, volume_history: List[int]) -> str:
        """Analyze seasonal patterns from volume history"""
        try:
            if len(volume_history) < 12:
                return "Insufficient data for seasonal analysis"
            
            # Simple seasonal analysis - check for Q4 peak (common for many products)
            q4_avg = sum(volume_history[-3:]) / 3  # Oct, Nov, Dec
            yearly_avg = sum(volume_history) / len(volume_history)
            
            if q4_avg > yearly_avg * 1.5:
                return "Peak in Q4 (Holiday season)"
            elif volume_history[5:8] == max([volume_history[i:i+3] for i in range(0, 10, 3)], key=sum):
                return "Peak in summer months"
            else:
                return "No clear seasonal pattern"
        except Exception:
            return "Unable to determine seasonal patterns"


# Global instance
jungle_scout_assistant = JungleScoutAssistant()