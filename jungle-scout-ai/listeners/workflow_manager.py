"""
Workflow Manager for Jungle Scout AI Assistant
Handles multi-step workflows for Amazon seller operations and research
"""
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from dataclasses import dataclass, field

from jungle_scout_ai.logging import logger


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Individual step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    id: str
    name: str
    description: str
    action: str  # The action to perform
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 3
    timeout_seconds: int = 300
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Workflow:
    """Represents a complete workflow"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[Dict[str, Any]] = None


class JungleScoutWorkflowManager:
    """Manages Jungle Scout-specific workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> Dict[str, Workflow]:
        """Load predefined workflow templates"""
        return {
            "product_launch": self._create_product_launch_workflow(),
            "competitor_monitoring": self._create_competitor_monitoring_workflow(),
            "inventory_management": self._create_inventory_management_workflow(),
            "market_research": self._create_market_research_workflow(),
            "listing_optimization": self._create_listing_optimization_workflow(),
            "ppc_campaign": self._create_ppc_campaign_workflow()
        }
    
    def _create_product_launch_workflow(self) -> Workflow:
        """Create a product launch workflow template"""
        return Workflow(
            id="product_launch_template",
            name="Product Launch",
            description="Complete product launch workflow from research to first sale",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="market_validation",
                    name="Market Validation",
                    description="Validate market opportunity",
                    action="jungle_scout_validate_market",
                    parameters={
                        "min_search_volume": 10000,
                        "max_competition": "medium",
                        "min_price": 20,
                        "max_price": 100
                    }
                ),
                WorkflowStep(
                    id="competitor_analysis",
                    name="Analyze Top Competitors",
                    description="Deep dive into top 10 competitors",
                    action="jungle_scout_analyze_competitors",
                    parameters={
                        "limit": 10,
                        "analyze": ["pricing", "keywords", "reviews", "sales_velocity"]
                    }
                ),
                WorkflowStep(
                    id="keyword_research",
                    name="Keyword Research",
                    description="Find high-value keywords",
                    action="jungle_scout_keyword_research",
                    parameters={
                        "seed_keywords": "{product_keywords}",
                        "min_volume": 1000,
                        "max_difficulty": 60,
                        "include_long_tail": True
                    }
                ),
                WorkflowStep(
                    id="sourcing_analysis",
                    name="Sourcing Cost Analysis",
                    description="Calculate sourcing and profit margins",
                    action="calculate_sourcing_costs",
                    parameters={
                        "target_margin": 30,
                        "include_shipping": True,
                        "include_fba_fees": True
                    }
                ),
                WorkflowStep(
                    id="create_listing",
                    name="Create Optimized Listing",
                    description="Generate SEO-optimized product listing",
                    action="create_product_listing",
                    parameters={
                        "use_ai": True,
                        "keywords": "{selected_keywords}",
                        "competitor_insights": True
                    }
                ),
                WorkflowStep(
                    id="launch_strategy",
                    name="Create Launch Strategy",
                    description="Plan launch campaign and promotions",
                    action="create_launch_plan",
                    parameters={
                        "strategy": "honeymoon_period",
                        "initial_units": "{launch_inventory}",
                        "ppc_budget": "{daily_ppc_budget}"
                    }
                ),
                WorkflowStep(
                    id="create_tracker",
                    name="Set Up Performance Tracking",
                    description="Configure automated tracking and alerts",
                    action="setup_product_tracking",
                    parameters={
                        "track_bsr": True,
                        "track_reviews": True,
                        "track_competitors": True,
                        "alert_thresholds": {
                            "bsr_drop": 20,
                            "negative_review": True,
                            "stock_low": 50
                        }
                    }
                )
            ]
        )
    
    def _create_competitor_monitoring_workflow(self) -> Workflow:
        """Create a competitor monitoring workflow"""
        return Workflow(
            id="competitor_monitoring_template",
            name="Competitor Monitoring",
            description="Track and respond to competitor activities",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="identify_competitors",
                    name="Identify Key Competitors",
                    description="Find main competitors to monitor",
                    action="find_competitors",
                    parameters={
                        "method": "keyword_based",
                        "keywords": "{target_keywords}",
                        "limit": 20
                    }
                ),
                WorkflowStep(
                    id="track_pricing",
                    name="Track Price Changes",
                    description="Monitor competitor pricing strategies",
                    action="track_competitor_prices",
                    parameters={
                        "check_frequency": "daily",
                        "alert_threshold": 5,  # 5% change
                        "include_coupons": True
                    }
                ),
                WorkflowStep(
                    id="monitor_inventory",
                    name="Monitor Stock Levels",
                    description="Track competitor inventory",
                    action="track_inventory_levels",
                    parameters={
                        "estimate_method": "bsr_velocity",
                        "track_stockouts": True
                    }
                ),
                WorkflowStep(
                    id="analyze_reviews",
                    name="Analyze New Reviews",
                    description="Monitor competitor review trends",
                    action="analyze_competitor_reviews",
                    parameters={
                        "sentiment_analysis": True,
                        "extract_keywords": True,
                        "find_weaknesses": True
                    }
                ),
                WorkflowStep(
                    id="track_marketing",
                    name="Track Marketing Activities",
                    description="Monitor PPC and promotions",
                    action="track_marketing_activities",
                    parameters={
                        "track_sponsored_products": True,
                        "track_deals": True,
                        "estimate_ad_spend": True
                    }
                ),
                WorkflowStep(
                    id="generate_insights",
                    name="Generate Competitive Insights",
                    description="Create actionable intelligence report",
                    action="create_competitive_report",
                    parameters={
                        "include_opportunities": True,
                        "include_threats": True,
                        "recommend_actions": True
                    }
                )
            ]
        )
    
    def _create_inventory_management_workflow(self) -> Workflow:
        """Create an inventory management workflow"""
        return Workflow(
            id="inventory_management_template",
            name="Inventory Management",
            description="Optimize inventory levels and prevent stockouts",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="analyze_velocity",
                    name="Analyze Sales Velocity",
                    description="Calculate current sales rate",
                    action="calculate_sales_velocity",
                    parameters={
                        "period": "last_30_days",
                        "include_seasonality": True,
                        "include_trends": True
                    }
                ),
                WorkflowStep(
                    id="forecast_demand",
                    name="Forecast Future Demand",
                    description="Predict inventory needs",
                    action="forecast_inventory_needs",
                    parameters={
                        "forecast_period": 90,  # days
                        "confidence_level": 0.95,
                        "include_promotions": True
                    }
                ),
                WorkflowStep(
                    id="calculate_reorder",
                    name="Calculate Reorder Points",
                    description="Determine when to reorder",
                    action="calculate_reorder_points",
                    parameters={
                        "lead_time_days": "{supplier_lead_time}",
                        "safety_stock_days": 14,
                        "min_order_quantity": "{moq}"
                    }
                ),
                WorkflowStep(
                    id="optimize_shipment",
                    name="Optimize Shipment Plan",
                    description="Plan optimal shipment schedule",
                    action="optimize_shipments",
                    parameters={
                        "shipping_method": "sea_freight",
                        "consolidate": True,
                        "minimize_storage_fees": True
                    }
                ),
                WorkflowStep(
                    id="create_po",
                    name="Generate Purchase Order",
                    description="Create PO for supplier",
                    action="generate_purchase_order",
                    parameters={
                        "include_variants": True,
                        "payment_terms": "{payment_terms}",
                        "quality_requirements": True
                    }
                ),
                WorkflowStep(
                    id="setup_alerts",
                    name="Configure Inventory Alerts",
                    description="Set up monitoring and alerts",
                    action="configure_inventory_alerts",
                    parameters={
                        "low_stock_threshold": "{reorder_point}",
                        "overstock_threshold": 180,  # days of supply
                        "expiry_warning": 60  # days before expiry
                    }
                )
            ]
        )
    
    def _create_market_research_workflow(self) -> Workflow:
        """Create a market research workflow"""
        return Workflow(
            id="market_research_template",
            name="Market Research",
            description="Comprehensive market analysis for new opportunities",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="identify_trends",
                    name="Identify Market Trends",
                    description="Find trending products and categories",
                    action="find_trending_products",
                    parameters={
                        "growth_threshold": 20,  # % monthly growth
                        "min_volume": 5000,
                        "emerging_only": False
                    }
                ),
                WorkflowStep(
                    id="analyze_categories",
                    name="Analyze Product Categories",
                    description="Deep dive into promising categories",
                    action="analyze_categories",
                    parameters={
                        "metrics": ["market_size", "growth_rate", "competition", "profitability"],
                        "depth": 3  # subcategory levels
                    }
                ),
                WorkflowStep(
                    id="customer_analysis",
                    name="Analyze Customer Needs",
                    description="Understand customer pain points",
                    action="analyze_customer_needs",
                    parameters={
                        "analyze_reviews": True,
                        "analyze_questions": True,
                        "sentiment_analysis": True,
                        "extract_features": True
                    }
                ),
                WorkflowStep(
                    id="gap_analysis",
                    name="Identify Market Gaps",
                    description="Find underserved opportunities",
                    action="find_market_gaps",
                    parameters={
                        "methods": ["feature_gap", "price_gap", "quality_gap"],
                        "min_opportunity_score": 7
                    }
                ),
                WorkflowStep(
                    id="validate_opportunities",
                    name="Validate Opportunities",
                    description="Score and rank opportunities",
                    action="validate_opportunities",
                    parameters={
                        "criteria": ["demand", "competition", "profitability", "barriers"],
                        "weight_factors": True
                    }
                ),
                WorkflowStep(
                    id="create_report",
                    name="Create Research Report",
                    description="Generate comprehensive report",
                    action="create_research_canvas",
                    parameters={
                        "format": "executive_summary",
                        "include_recommendations": True,
                        "include_action_plan": True
                    }
                )
            ]
        )
    
    def _create_listing_optimization_workflow(self) -> Workflow:
        """Create a listing optimization workflow"""
        return Workflow(
            id="listing_optimization_template",
            name="Listing Optimization",
            description="Optimize product listings for maximum conversion",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="audit_listing",
                    name="Audit Current Listing",
                    description="Analyze current listing performance",
                    action="audit_product_listing",
                    parameters={
                        "check_seo": True,
                        "check_images": True,
                        "check_content": True,
                        "compare_competitors": True
                    }
                ),
                WorkflowStep(
                    id="keyword_optimization",
                    name="Optimize Keywords",
                    description="Update keywords for better ranking",
                    action="optimize_listing_keywords",
                    parameters={
                        "backend_keywords": True,
                        "title_optimization": True,
                        "bullet_points": True,
                        "description": True
                    }
                ),
                WorkflowStep(
                    id="content_enhancement",
                    name="Enhance Content",
                    description="Improve listing copy and features",
                    action="enhance_listing_content",
                    parameters={
                        "use_ai": True,
                        "a_b_test": True,
                        "localization": True
                    }
                ),
                WorkflowStep(
                    id="image_optimization",
                    name="Optimize Images",
                    description="Improve visual content",
                    action="optimize_product_images",
                    parameters={
                        "analyze_competitors": True,
                        "lifestyle_images": True,
                        "infographics": True,
                        "video_content": True
                    }
                ),
                WorkflowStep(
                    id="price_optimization",
                    name="Optimize Pricing",
                    description="Find optimal price point",
                    action="optimize_pricing",
                    parameters={
                        "elasticity_test": True,
                        "competitor_analysis": True,
                        "profit_optimization": True
                    }
                ),
                WorkflowStep(
                    id="monitor_impact",
                    name="Monitor Optimization Impact",
                    description="Track listing performance changes",
                    action="track_optimization_impact",
                    parameters={
                        "metrics": ["conversion_rate", "click_through_rate", "sales", "ranking"],
                        "duration": 30  # days
                    }
                )
            ]
        )
    
    def _create_ppc_campaign_workflow(self) -> Workflow:
        """Create a PPC campaign workflow"""
        return Workflow(
            id="ppc_campaign_template",
            name="PPC Campaign Setup",
            description="Set up and optimize PPC campaigns",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="keyword_research",
                    name="PPC Keyword Research",
                    description="Find profitable PPC keywords",
                    action="research_ppc_keywords",
                    parameters={
                        "include_competitors": True,
                        "include_auto_targets": True,
                        "min_relevance": 0.8
                    }
                ),
                WorkflowStep(
                    id="structure_campaigns",
                    name="Structure Campaigns",
                    description="Create campaign architecture",
                    action="structure_ppc_campaigns",
                    parameters={
                        "campaign_types": ["sponsored_products", "sponsored_brands"],
                        "match_types": ["exact", "phrase", "broad"],
                        "segmentation": "performance_based"
                    }
                ),
                WorkflowStep(
                    id="set_bids",
                    name="Calculate Initial Bids",
                    description="Set competitive bid prices",
                    action="calculate_ppc_bids",
                    parameters={
                        "target_acos": "{target_acos}",
                        "bid_strategy": "aggressive_launch",
                        "dayparting": True
                    }
                ),
                WorkflowStep(
                    id="create_ads",
                    name="Create Ad Content",
                    description="Generate ad copy and creative",
                    action="create_ad_content",
                    parameters={
                        "ad_types": ["product_collection", "store_spotlight", "video"],
                        "a_b_testing": True
                    }
                ),
                WorkflowStep(
                    id="negative_keywords",
                    name="Build Negative Keywords",
                    description="Prevent wasted spend",
                    action="build_negative_keywords",
                    parameters={
                        "auto_discover": True,
                        "competitor_brands": True,
                        "irrelevant_terms": True
                    }
                ),
                WorkflowStep(
                    id="launch_monitor",
                    name="Launch and Monitor",
                    description="Launch campaigns with monitoring",
                    action="launch_ppc_campaigns",
                    parameters={
                        "auto_optimization": True,
                        "budget_pacing": True,
                        "performance_alerts": True
                    }
                )
            ]
        )
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        user_id: str,
        schedule: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Create a new workflow"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id[:8]}"
        
        workflow_steps = []
        for i, step_data in enumerate(steps):
            step = WorkflowStep(
                id=f"step_{i}",
                name=step_data.get("name", f"Step {i+1}"),
                description=step_data.get("description", ""),
                action=step_data["action"],
                parameters=step_data.get("parameters", {}),
                conditions=step_data.get("conditions", []),
                retry_count=step_data.get("retry_count", 3),
                timeout_seconds=step_data.get("timeout_seconds", 300)
            )
            workflow_steps.append(step)
        
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            created_by=user_id,
            schedule=schedule
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Created workflow: {workflow_id}")
        
        return workflow
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any],
        assistant
    ) -> Dict[str, Any]:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            if workflow_id in self.templates:
                workflow = self.templates[workflow_id]
            else:
                raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.context.update(context)
        
        results = {
            "workflow_id": workflow.id,
            "status": "running",
            "steps": [],
            "started_at": datetime.now().isoformat()
        }
        
        try:
            for i, step in enumerate(workflow.steps):
                workflow.current_step = i
                step.status = StepStatus.RUNNING
                
                # Check conditions
                if not self._check_conditions(step.conditions, workflow.context):
                    step.status = StepStatus.SKIPPED
                    results["steps"].append({
                        "step_id": step.id,
                        "name": step.name,
                        "status": "skipped",
                        "reason": "Conditions not met"
                    })
                    continue
                
                # Execute step
                try:
                    step_result = await self._execute_step(step, workflow.context, assistant)
                    step.status = StepStatus.COMPLETED
                    step.result = step_result
                    
                    # Update context with step results
                    workflow.context[f"step_{step.id}_result"] = step_result
                    
                    results["steps"].append({
                        "step_id": step.id,
                        "name": step.name,
                        "status": "completed",
                        "result": step_result
                    })
                    
                except Exception as e:
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    
                    results["steps"].append({
                        "step_id": step.id,
                        "name": step.name,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Retry logic
                    if step.retry_count > 0:
                        logger.warning(f"Step {step.id} failed, retrying...")
                        step.retry_count -= 1
                        i -= 1  # Retry this step
                    else:
                        workflow.status = WorkflowStatus.FAILED
                        break
            
            if workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
                results["status"] = "completed"
            else:
                results["status"] = "failed"
                
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            results["status"] = "failed"
            results["error"] = str(e)
            logger.error(f"Workflow {workflow_id} failed: {e}")
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        assistant
    ) -> Any:
        """Execute a single workflow step"""
        # Substitute context variables in parameters
        params = self._substitute_variables(step.parameters, context)
        
        # Build command based on action
        if step.action == "jungle_scout_validate_market":
            command = f"Validate market opportunity with search volume > {params['min_search_volume']} and competition <= {params['max_competition']}"
            
        elif step.action == "jungle_scout_analyze_competitors":
            command = f"Analyze top {params['limit']} competitors for: {', '.join(params['analyze'])}"
            
        elif step.action == "jungle_scout_keyword_research":
            command = f"Research keywords starting with '{params['seed_keywords']}' with volume > {params['min_volume']}"
            
        else:
            command = f"Execute {step.action} with parameters: {json.dumps(params)}"
        
        # Execute through assistant
        result = await assistant.process_command(command, context)
        return result
    
    def _check_conditions(self, conditions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """Check if step conditions are met"""
        if not conditions:
            return True
            
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            context_value = context.get(field)
            
            if operator == 'equals' and context_value != value:
                return False
            elif operator == 'not_equals' and context_value == value:
                return False
            elif operator == 'contains' and value not in str(context_value):
                return False
            elif operator == 'exists' and context_value is None:
                return False
                
        return True
    
    def _substitute_variables(self, data: Any, context: Dict[str, Any]) -> Any:
        """Substitute {variable} placeholders with context values"""
        if isinstance(data, str):
            # Replace {variable} with context values
            import re
            pattern = r'\{([^}]+)\}'
            
            def replacer(match):
                key = match.group(1)
                if '.' in key:
                    # Handle nested keys like context.channel_id
                    keys = key.split('.')
                    value = context
                    for k in keys:
                        if isinstance(value, dict):
                            value = value.get(k, match.group(0))
                        else:
                            return match.group(0)
                    return str(value)
                else:
                    return str(context.get(key, match.group(0)))
            
            return re.sub(pattern, replacer, data)
            
        elif isinstance(data, dict):
            return {k: self._substitute_variables(v, context) for k, v in data.items()}
            
        elif isinstance(data, list):
            return [self._substitute_variables(item, context) for item in data]
            
        else:
            return data
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        return {
            "workflow_id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "current_step": workflow.current_step,
            "total_steps": len(workflow.steps),
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "status": step.status.value,
                    "error": step.error
                }
                for step in workflow.steps
            ]
        }
    
    def list_workflows(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflows, optionally filtered by user"""
        workflows = []
        
        # Include templates
        for template_id, template in self.templates.items():
            workflows.append({
                "id": template_id,
                "name": template.name,
                "description": template.description,
                "type": "template",
                "steps": len(template.steps)
            })
        
        # Include user workflows
        for workflow in self.workflows.values():
            if user_id and workflow.created_by != user_id:
                continue
            workflows.append({
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "type": "custom",
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "steps": len(workflow.steps)
            })
        
        return workflows