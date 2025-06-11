"""
Workflow Manager for Slack AI Assistant
Handles multi-step workflows, automation, and process orchestration for Slack operations
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


class SlackWorkflowManager:
    """Manages Slack-specific workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> Dict[str, Workflow]:
        """Load predefined workflow templates"""
        return {
            "channel_cleanup": self._create_channel_cleanup_workflow(),
            "team_standup": self._create_team_standup_workflow(),
            "incident_response": self._create_incident_response_workflow(),
            "onboarding": self._create_onboarding_workflow(),
            "content_moderation": self._create_content_moderation_workflow(),
            "meeting_automation": self._create_meeting_automation_workflow()
        }
    
    def _create_channel_cleanup_workflow(self) -> Workflow:
        """Create a channel cleanup workflow template"""
        return Workflow(
            id="channel_cleanup_template",
            name="Channel Cleanup",
            description="Automated cleanup of old messages and files in channels",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="identify_channels",
                    name="Identify Inactive Channels",
                    description="Find channels with no activity in 30+ days",
                    action="slack_list_channels",
                    parameters={
                        "filter": "inactive",
                        "days_inactive": 30,
                        "exclude_archived": True
                    }
                ),
                WorkflowStep(
                    id="analyze_content",
                    name="Analyze Channel Content",
                    description="Check for important pinned messages or files",
                    action="slack_analyze_channel",
                    parameters={
                        "check_pins": True,
                        "check_files": True,
                        "important_keywords": ["important", "reference", "documentation"]
                    }
                ),
                WorkflowStep(
                    id="archive_old_files",
                    name="Archive Old Files",
                    description="Move old files to external storage",
                    action="slack_archive_files",
                    parameters={
                        "older_than_days": 90,
                        "exclude_pinned": True,
                        "create_index": True
                    },
                    conditions=[
                        {"field": "has_old_files", "operator": "equals", "value": True}
                    ]
                ),
                WorkflowStep(
                    id="notify_owners",
                    name="Notify Channel Owners",
                    description="Send cleanup summary to channel owners",
                    action="slack_send_dm",
                    parameters={
                        "recipient": "{channel_owner}",
                        "message_template": "channel_cleanup_notice"
                    }
                ),
                WorkflowStep(
                    id="create_report",
                    name="Create Cleanup Report",
                    description="Generate and post cleanup summary",
                    action="slack_create_canvas",
                    parameters={
                        "title": "Channel Cleanup Report - {date}",
                        "template": "cleanup_report",
                        "post_to": "{admin_channel}"
                    }
                )
            ]
        )
    
    def _create_team_standup_workflow(self) -> Workflow:
        """Create a daily standup workflow template"""
        return Workflow(
            id="team_standup_template",
            name="Team Standup",
            description="Automated daily standup collection and summary",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="send_prompts",
                    name="Send Standup Prompts",
                    description="DM team members for standup updates",
                    action="slack_send_standup_prompts",
                    parameters={
                        "team_members": "{team_list}",
                        "questions": [
                            "What did you complete yesterday?",
                            "What are you working on today?",
                            "Any blockers or concerns?"
                        ],
                        "deadline_minutes": 30
                    }
                ),
                WorkflowStep(
                    id="collect_responses",
                    name="Collect Responses",
                    description="Gather standup responses",
                    action="slack_collect_responses",
                    parameters={
                        "wait_time_minutes": 30,
                        "send_reminders": True,
                        "reminder_after_minutes": 15
                    }
                ),
                WorkflowStep(
                    id="analyze_blockers",
                    name="Analyze Blockers",
                    description="Identify and categorize blockers",
                    action="analyze_standup_blockers",
                    parameters={
                        "categorize": True,
                        "find_patterns": True,
                        "suggest_solutions": True
                    }
                ),
                WorkflowStep(
                    id="create_summary",
                    name="Create Standup Summary",
                    description="Generate formatted standup summary",
                    action="create_standup_summary",
                    parameters={
                        "format": "by_person",
                        "highlight_blockers": True,
                        "include_metrics": True
                    }
                ),
                WorkflowStep(
                    id="post_summary",
                    name="Post to Team Channel",
                    description="Share standup summary with team",
                    action="slack_post_message",
                    parameters={
                        "channel": "{team_channel}",
                        "pin_message": True,
                        "thread_responses": True
                    }
                )
            ]
        )
    
    def _create_incident_response_workflow(self) -> Workflow:
        """Create an incident response workflow"""
        return Workflow(
            id="incident_response_template",
            name="Incident Response",
            description="Coordinate incident response and communication",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="create_channel",
                    name="Create Incident Channel",
                    description="Create dedicated incident channel",
                    action="slack_create_channel",
                    parameters={
                        "name": "incident-{timestamp}",
                        "topic": "{incident_description}",
                        "private": False
                    }
                ),
                WorkflowStep(
                    id="assemble_team",
                    name="Assemble Response Team",
                    description="Invite relevant team members",
                    action="slack_invite_users",
                    parameters={
                        "channel": "{incident_channel}",
                        "users": "{response_team}",
                        "notify": True
                    }
                ),
                WorkflowStep(
                    id="post_runbook",
                    name="Post Incident Runbook",
                    description="Share incident response procedures",
                    action="slack_post_canvas",
                    parameters={
                        "template": "incident_runbook",
                        "variables": {
                            "incident_type": "{incident_type}",
                            "severity": "{severity}"
                        }
                    }
                ),
                WorkflowStep(
                    id="start_timeline",
                    name="Start Incident Timeline",
                    description="Begin tracking incident timeline",
                    action="create_incident_timeline",
                    parameters={
                        "auto_capture": True,
                        "capture_edits": True,
                        "capture_reactions": True
                    }
                ),
                WorkflowStep(
                    id="schedule_updates",
                    name="Schedule Status Updates",
                    description="Set up regular status update reminders",
                    action="schedule_reminders",
                    parameters={
                        "interval_minutes": 30,
                        "recipient": "{incident_commander}",
                        "message": "Time for incident status update"
                    }
                ),
                WorkflowStep(
                    id="notify_stakeholders",
                    name="Notify Stakeholders",
                    description="Send initial incident notification",
                    action="slack_notify_group",
                    parameters={
                        "groups": ["leadership", "customer_success"],
                        "template": "incident_notification",
                        "severity_based": True
                    }
                )
            ]
        )
    
    def _create_onboarding_workflow(self) -> Workflow:
        """Create an employee onboarding workflow"""
        return Workflow(
            id="onboarding_template",
            name="Employee Onboarding",
            description="Automate new employee Slack onboarding",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="send_welcome",
                    name="Send Welcome Message",
                    description="Send personalized welcome DM",
                    action="slack_send_welcome",
                    parameters={
                        "user": "{new_employee}",
                        "template": "employee_welcome",
                        "include_resources": True
                    }
                ),
                WorkflowStep(
                    id="add_to_channels",
                    name="Add to Team Channels",
                    description="Add user to relevant channels",
                    action="slack_add_to_channels",
                    parameters={
                        "user": "{new_employee}",
                        "channels": {
                            "required": ["general", "announcements", "{team_channel}"],
                            "optional": ["social", "random", "help"]
                        }
                    }
                ),
                WorkflowStep(
                    id="introduce_to_team",
                    name="Post Team Introduction",
                    description="Post introduction in team channel",
                    action="slack_post_introduction",
                    parameters={
                        "channel": "{team_channel}",
                        "user": "{new_employee}",
                        "bio": "{employee_bio}",
                        "fun_fact": "{fun_fact}"
                    }
                ),
                WorkflowStep(
                    id="schedule_meetings",
                    name="Schedule Onboarding Meetings",
                    description="Set up 1:1s and team meetings",
                    action="schedule_meetings",
                    parameters={
                        "meetings": [
                            {"with": "{manager}", "topic": "Welcome 1:1", "day": 1},
                            {"with": "{buddy}", "topic": "Buddy intro", "day": 1},
                            {"with": "{team}", "topic": "Team meeting", "day": 2}
                        ]
                    }
                ),
                WorkflowStep(
                    id="create_checklist",
                    name="Create Onboarding Checklist",
                    description="Generate interactive checklist",
                    action="create_onboarding_checklist",
                    parameters={
                        "assign_to": "{new_employee}",
                        "cc": ["{manager}", "{buddy}"],
                        "due_dates": True
                    }
                )
            ]
        )
    
    def _create_content_moderation_workflow(self) -> Workflow:
        """Create a content moderation workflow"""
        return Workflow(
            id="content_moderation_template",
            name="Content Moderation",
            description="Monitor and moderate channel content",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="scan_messages",
                    name="Scan Recent Messages",
                    description="Check messages for policy violations",
                    action="slack_scan_messages",
                    parameters={
                        "channels": "{monitored_channels}",
                        "time_range": "last_hour",
                        "check_for": ["inappropriate_content", "spam", "sensitive_data"]
                    }
                ),
                WorkflowStep(
                    id="analyze_sentiment",
                    name="Analyze Sentiment",
                    description="Check for negative sentiment patterns",
                    action="analyze_message_sentiment",
                    parameters={
                        "threshold": -0.7,
                        "context_window": 5,
                        "check_threads": True
                    }
                ),
                WorkflowStep(
                    id="flag_violations",
                    name="Flag Policy Violations",
                    description="Mark messages that violate policies",
                    action="flag_messages",
                    parameters={
                        "add_reaction": "warning",
                        "notify_moderators": True,
                        "create_report": True
                    },
                    conditions=[
                        {"field": "violations_found", "operator": "equals", "value": True}
                    ]
                ),
                WorkflowStep(
                    id="notify_users",
                    name="Notify Users",
                    description="Send policy reminder to violators",
                    action="slack_send_policy_reminder",
                    parameters={
                        "tone": "friendly",
                        "include_resources": True,
                        "escalate_repeat": True
                    }
                ),
                WorkflowStep(
                    id="generate_report",
                    name="Generate Moderation Report",
                    description="Create summary for moderators",
                    action="create_moderation_report",
                    parameters={
                        "include_trends": True,
                        "compare_previous": True,
                        "suggestions": True
                    }
                )
            ]
        )
    
    def _create_meeting_automation_workflow(self) -> Workflow:
        """Create a meeting automation workflow"""
        return Workflow(
            id="meeting_automation_template",
            name="Meeting Automation",
            description="Automate meeting preparation and follow-up",
            created_by="system",
            steps=[
                WorkflowStep(
                    id="send_agenda_reminder",
                    name="Send Agenda Reminder",
                    description="Remind organizer to share agenda",
                    action="slack_send_reminder",
                    parameters={
                        "recipient": "{meeting_organizer}",
                        "before_meeting_hours": 24,
                        "message": "Don't forget to share the agenda for tomorrow's {meeting_name}"
                    }
                ),
                WorkflowStep(
                    id="create_meeting_channel",
                    name="Create Meeting Thread",
                    description="Create dedicated thread for meeting",
                    action="slack_create_thread",
                    parameters={
                        "channel": "{meeting_channel}",
                        "title": "{meeting_name} - {date}",
                        "pin": True
                    }
                ),
                WorkflowStep(
                    id="share_prep_materials",
                    name="Share Preparation Materials",
                    description="Post relevant documents and context",
                    action="slack_share_files",
                    parameters={
                        "thread": "{meeting_thread}",
                        "files": "{prep_materials}",
                        "add_context": True
                    }
                ),
                WorkflowStep(
                    id="start_note_taking",
                    name="Initialize Meeting Notes",
                    description="Create collaborative meeting notes",
                    action="create_meeting_canvas",
                    parameters={
                        "template": "meeting_notes",
                        "attendees": "{meeting_attendees}",
                        "agenda": "{meeting_agenda}"
                    }
                ),
                WorkflowStep(
                    id="send_followup",
                    name="Send Follow-up Tasks",
                    description="Distribute action items after meeting",
                    action="distribute_action_items",
                    parameters={
                        "extract_from_notes": True,
                        "assign_owners": True,
                        "set_due_dates": True,
                        "create_reminders": True
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
        slack_client,
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
                    step_result = await self._execute_step(
                        step, workflow.context, slack_client, assistant
                    )
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
        slack_client,
        assistant
    ) -> Any:
        """Execute a single workflow step"""
        # Substitute context variables in parameters
        params = self._substitute_variables(step.parameters, context)
        
        # Execute based on action type
        if step.action == "slack_create_channel":
            result = slack_client.conversations_create(
                name=params["name"],
                is_private=params.get("private", False)
            )
            return {"channel_id": result["channel"]["id"]}
            
        elif step.action == "slack_send_message":
            result = slack_client.chat_postMessage(
                channel=params["channel"],
                text=params.get("text", ""),
                blocks=params.get("blocks", [])
            )
            return {"message_ts": result["ts"]}
            
        elif step.action == "slack_invite_users":
            channel = params["channel"]
            users = params["users"]
            if isinstance(users, str):
                users = [users]
            
            for user in users:
                slack_client.conversations_invite(
                    channel=channel,
                    users=user
                )
            return {"invited": len(users)}
            
        elif step.action == "slack_create_canvas":
            # Use the canvas manager
            from .canvas_integration import CanvasManager
            canvas_manager = CanvasManager(slack_client)
            
            result = canvas_manager.create_workflow_canvas(
                channel_id=params.get("channel", context.get("channel_id")),
                workflow_name=params.get("title", "Workflow"),
                steps=params.get("content", [])
            )
            return {"canvas_url": canvas_manager.get_canvas_url(result)}
            
        else:
            # For other actions, use the assistant
            command = f"Execute {step.action} with parameters: {json.dumps(params)}"
            result = assistant.process_command(command, context)
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