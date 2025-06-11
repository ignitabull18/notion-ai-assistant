"""
Workflow Manager for Notion AI Assistant
Handles multi-step workflows, automation, and process orchestration
"""
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from dataclasses import dataclass, field

from utils.logging import logger


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


class NotionWorkflowManager:
    """Manages Notion-specific workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> Dict[str, Workflow]:
        """Load predefined workflow templates"""
        return {
            "weekly_review": self._create_weekly_review_workflow(),
            "project_setup": self._create_project_setup_workflow(),
            "content_pipeline": self._create_content_pipeline_workflow(),
            "database_maintenance": self._create_database_maintenance_workflow(),
            "team_onboarding": self._create_team_onboarding_workflow()
        }
    
    def _create_weekly_review_workflow(self) -> Workflow:
        """Create a weekly review workflow template"""
        return Workflow(
            id="weekly_review_template",
            name="Weekly Review",
            description="Automated weekly review of tasks and projects",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="collect_completed",
                    name="Collect Completed Tasks",
                    description="Gather all tasks completed this week",
                    action="notion_query_database",
                    parameters={
                        "filter": {
                            "property": "Status",
                            "select": {"equals": "Done"},
                            "and": {
                                "property": "Completed Date",
                                "date": {"past_week": {}}
                            }
                        }
                    }
                ),
                WorkflowStep(
                    id="analyze_productivity",
                    name="Analyze Productivity",
                    description="Calculate productivity metrics",
                    action="analyze_task_metrics",
                    parameters={
                        "metrics": ["completion_rate", "average_duration", "priority_distribution"]
                    }
                ),
                WorkflowStep(
                    id="identify_blockers",
                    name="Identify Blockers",
                    description="Find overdue or blocked tasks",
                    action="notion_query_database",
                    parameters={
                        "filter": {
                            "or": [
                                {
                                    "property": "Status",
                                    "select": {"equals": "Blocked"}
                                },
                                {
                                    "property": "Due Date",
                                    "date": {"past": {}}
                                }
                            ]
                        }
                    }
                ),
                WorkflowStep(
                    id="create_summary",
                    name="Create Summary Page",
                    description="Create weekly review summary in Notion",
                    action="notion_create_page",
                    parameters={
                        "title": "Weekly Review - {date}",
                        "template": "weekly_review",
                        "parent": "reviews_database"
                    }
                ),
                WorkflowStep(
                    id="send_report",
                    name="Send Slack Report",
                    description="Send summary to Slack channel",
                    action="send_slack_message",
                    parameters={
                        "channel": "{context.channel_id}",
                        "format": "weekly_review_summary"
                    }
                )
            ]
        )
    
    def _create_project_setup_workflow(self) -> Workflow:
        """Create a project setup workflow template"""
        return Workflow(
            id="project_setup_template",
            name="Project Setup",
            description="Set up a new project with all required components",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="create_project_page",
                    name="Create Project Home",
                    description="Create main project page",
                    action="notion_create_page",
                    parameters={
                        "title": "{project_name}",
                        "template": "project_home",
                        "properties": {
                            "Status": "Planning",
                            "Start Date": "{start_date}",
                            "End Date": "{end_date}"
                        }
                    }
                ),
                WorkflowStep(
                    id="create_tasks_db",
                    name="Create Tasks Database",
                    description="Set up project tasks database",
                    action="notion_create_database",
                    parameters={
                        "title": "{project_name} - Tasks",
                        "parent": "{context.project_page_id}",
                        "properties": {
                            "Title": {"type": "title"},
                            "Status": {
                                "type": "select",
                                "options": ["To Do", "In Progress", "Review", "Done"]
                            },
                            "Assignee": {"type": "person"},
                            "Due Date": {"type": "date"},
                            "Priority": {
                                "type": "select",
                                "options": ["Low", "Medium", "High", "Critical"]
                            }
                        }
                    }
                ),
                WorkflowStep(
                    id="create_docs_folder",
                    name="Create Documentation Structure",
                    description="Set up documentation pages",
                    action="notion_create_page_batch",
                    parameters={
                        "pages": [
                            {"title": "Requirements", "parent": "{context.project_page_id}"},
                            {"title": "Design Documents", "parent": "{context.project_page_id}"},
                            {"title": "Meeting Notes", "parent": "{context.project_page_id}"}
                        ]
                    }
                ),
                WorkflowStep(
                    id="setup_views",
                    name="Configure Database Views",
                    description="Create useful database views",
                    action="notion_create_views",
                    parameters={
                        "database_id": "{context.tasks_db_id}",
                        "views": [
                            {"name": "Kanban", "type": "board", "group_by": "Status"},
                            {"name": "Calendar", "type": "calendar", "date_property": "Due Date"},
                            {"name": "My Tasks", "type": "table", "filter": "assignee = current_user"}
                        ]
                    }
                ),
                WorkflowStep(
                    id="notify_team",
                    name="Notify Team",
                    description="Send project setup notification",
                    action="send_slack_message",
                    parameters={
                        "channel": "{context.channel_id}",
                        "message": "Project '{project_name}' has been set up successfully!",
                        "blocks": "project_setup_complete"
                    }
                )
            ]
        )
    
    def _create_content_pipeline_workflow(self) -> Workflow:
        """Create a content creation pipeline workflow"""
        return Workflow(
            id="content_pipeline_template",
            name="Content Pipeline",
            description="Automated content creation and publishing workflow",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="create_content_item",
                    name="Create Content Item",
                    description="Add new content to pipeline",
                    action="notion_insert_database_row",
                    parameters={
                        "database": "content_calendar",
                        "properties": {
                            "Title": "{content_title}",
                            "Type": "{content_type}",
                            "Status": "Draft",
                            "Author": "{author}",
                            "Due Date": "{due_date}"
                        }
                    }
                ),
                WorkflowStep(
                    id="assign_reviewer",
                    name="Assign Reviewer",
                    description="Automatically assign content reviewer",
                    action="assign_team_member",
                    parameters={
                        "role": "editor",
                        "workload_balanced": True
                    }
                ),
                WorkflowStep(
                    id="create_tasks",
                    name="Create Sub-tasks",
                    description="Break down content into tasks",
                    action="create_content_tasks",
                    parameters={
                        "tasks": [
                            "Research and outline",
                            "First draft",
                            "Review and edit",
                            "Final polish",
                            "Publish"
                        ]
                    }
                ),
                WorkflowStep(
                    id="schedule_reminders",
                    name="Schedule Reminders",
                    description="Set up automated reminders",
                    action="schedule_notifications",
                    parameters={
                        "reminders": [
                            {"before_due": "3 days", "message": "Content draft due soon"},
                            {"before_due": "1 day", "message": "Content due tomorrow"},
                            {"on_status": "Review", "message": "Content ready for review"}
                        ]
                    }
                )
            ]
        )
    
    def _create_database_maintenance_workflow(self) -> Workflow:
        """Create a database maintenance workflow"""
        return Workflow(
            id="database_maintenance_template",
            name="Database Maintenance",
            description="Regular database cleanup and optimization",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="archive_old_items",
                    name="Archive Old Items",
                    description="Move completed items older than 90 days",
                    action="notion_bulk_update",
                    parameters={
                        "filter": {
                            "and": [
                                {"property": "Status", "select": {"equals": "Done"}},
                                {"property": "Completed Date", "date": {"before": "90 days ago"}}
                            ]
                        },
                        "update": {"property": "Archived", "checkbox": True}
                    }
                ),
                WorkflowStep(
                    id="clean_duplicates",
                    name="Find Duplicates",
                    description="Identify potential duplicate entries",
                    action="find_duplicate_entries",
                    parameters={
                        "match_properties": ["Title", "Created By"],
                        "similarity_threshold": 0.9
                    }
                ),
                WorkflowStep(
                    id="fix_relations",
                    name="Fix Broken Relations",
                    description="Repair broken database relations",
                    action="validate_relations",
                    parameters={
                        "fix_orphaned": True,
                        "update_bidirectional": True
                    }
                ),
                WorkflowStep(
                    id="optimize_formulas",
                    name="Optimize Formulas",
                    description="Review and optimize complex formulas",
                    action="analyze_formula_performance",
                    parameters={
                        "suggest_improvements": True
                    }
                ),
                WorkflowStep(
                    id="generate_report",
                    name="Generate Maintenance Report",
                    description="Create maintenance summary",
                    action="create_maintenance_report",
                    parameters={
                        "include_metrics": True,
                        "send_to_slack": True
                    }
                )
            ]
        )
    
    def _create_team_onboarding_workflow(self) -> Workflow:
        """Create a team member onboarding workflow"""
        return Workflow(
            id="team_onboarding_template",
            name="Team Onboarding",
            description="Onboard new team member to Notion workspace",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="create_user_page",
                    name="Create User Page",
                    description="Create personal workspace for new member",
                    action="notion_create_page",
                    parameters={
                        "title": "{member_name} - Workspace",
                        "template": "user_workspace",
                        "parent": "team_directory"
                    }
                ),
                WorkflowStep(
                    id="grant_permissions",
                    name="Set Permissions",
                    description="Grant appropriate workspace permissions",
                    action="set_user_permissions",
                    parameters={
                        "user_email": "{member_email}",
                        "role": "{member_role}",
                        "databases": ["tasks", "projects", "documents"]
                    }
                ),
                WorkflowStep(
                    id="create_onboarding_tasks",
                    name="Create Onboarding Tasks",
                    description="Set up onboarding checklist",
                    action="create_task_list",
                    parameters={
                        "tasks": [
                            "Review workspace structure",
                            "Complete profile information",
                            "Join relevant databases",
                            "Read team documentation",
                            "Schedule 1:1 with manager"
                        ],
                        "assign_to": "{member_name}"
                    }
                ),
                WorkflowStep(
                    id="send_welcome",
                    name="Send Welcome Message",
                    description="Send personalized welcome",
                    action="send_welcome_package",
                    parameters={
                        "include_guides": True,
                        "schedule_training": True
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
        agent_func: Callable
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
                    step_result = await self._execute_step(step, workflow.context, agent_func)
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
        agent_func: Callable
    ) -> Any:
        """Execute a single workflow step"""
        # Substitute context variables in parameters
        params = self._substitute_variables(step.parameters, context)
        
        # Build the command for the agent
        if step.action == "notion_create_page":
            command = f"Create a Notion page titled '{params.get('title')}'"
            if params.get('parent'):
                command += f" in {params['parent']}"
            if params.get('template'):
                command += f" using the {params['template']} template"
                
        elif step.action == "notion_query_database":
            command = "Query Notion database with filter: " + json.dumps(params.get('filter', {}))
            
        elif step.action == "notion_create_database":
            command = f"Create a Notion database called '{params.get('title')}' with properties: " + \
                     json.dumps(params.get('properties', {}))
                     
        elif step.action == "send_slack_message":
            # This would be handled differently - just return success for now
            return {"status": "sent", "channel": params.get('channel')}
            
        else:
            command = f"Execute {step.action} with parameters: {json.dumps(params)}"
        
        # Execute through agent
        result = await agent_func(
            user_id=context.get('user_id'),
            message=command,
            channel_id=context.get('channel_id')
        )
        
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