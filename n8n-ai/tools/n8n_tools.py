"""
Custom N8N tools for Agno agent
Implements workflow management, execution, and monitoring
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from agno.models import BaseTool

logger = logging.getLogger(__name__)

# N8N API configuration
N8N_API_URL = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
N8N_USERNAME = os.getenv("N8N_USERNAME", "")
N8N_PASSWORD = os.getenv("N8N_PASSWORD", "")

# Headers for N8N API requests
def get_headers():
    """Get headers for N8N API requests"""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    return headers


class ListWorkflowsTool(BaseTool):
    """List all workflows in the N8N instance"""
    
    name: str = "list_workflows"
    description: str = "List all workflows in the N8N instance with their status and details"
    
    def run(self, active_only: bool = False) -> Dict[str, Any]:
        """List workflows"""
        try:
            url = f"{N8N_API_URL}/workflows"
            params = {"active": "true"} if active_only else {}
            
            response = requests.get(url, headers=get_headers(), params=params)
            response.raise_for_status()
            
            workflows = response.json().get("data", [])
            
            return {
                "success": True,
                "workflows": workflows,
                "count": len(workflows)
            }
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetWorkflowTool(BaseTool):
    """Get details of a specific workflow"""
    
    name: str = "get_workflow"
    description: str = "Get detailed information about a specific workflow by ID"
    
    def run(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details"""
        try:
            url = f"{N8N_API_URL}/workflows/{workflow_id}"
            response = requests.get(url, headers=get_headers())
            response.raise_for_status()
            
            return {
                "success": True,
                "workflow": response.json()
            }
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class CreateWorkflowTool(BaseTool):
    """Create a new workflow from JSON"""
    
    name: str = "create_workflow"
    description: str = "Create a new workflow from a JSON definition"
    
    def run(self, name: str, nodes: List[Dict], connections: Dict, 
            settings: Optional[Dict] = None, active: bool = False) -> Dict[str, Any]:
        """Create a new workflow"""
        try:
            workflow_data = {
                "name": name,
                "nodes": nodes,
                "connections": connections,
                "active": active,
                "settings": settings or {}
            }
            
            url = f"{N8N_API_URL}/workflows"
            response = requests.post(url, headers=get_headers(), json=workflow_data)
            response.raise_for_status()
            
            created_workflow = response.json()
            
            return {
                "success": True,
                "workflow": created_workflow,
                "message": f"Workflow '{name}' created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class UpdateWorkflowTool(BaseTool):
    """Update an existing workflow"""
    
    name: str = "update_workflow"
    description: str = "Update an existing workflow's configuration"
    
    def run(self, workflow_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update workflow"""
        try:
            url = f"{N8N_API_URL}/workflows/{workflow_id}"
            response = requests.patch(url, headers=get_headers(), json=updates)
            response.raise_for_status()
            
            return {
                "success": True,
                "workflow": response.json(),
                "message": f"Workflow {workflow_id} updated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ExecuteWorkflowTool(BaseTool):
    """Execute a workflow"""
    
    name: str = "execute_workflow"
    description: str = "Execute a workflow by ID with optional input data"
    
    def run(self, workflow_id: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute workflow"""
        try:
            url = f"{N8N_API_URL}/workflows/{workflow_id}/execute"
            
            payload = {}
            if data:
                payload["workflowData"] = {"data": data}
            
            response = requests.post(url, headers=get_headers(), json=payload)
            response.raise_for_status()
            
            execution = response.json()
            
            return {
                "success": True,
                "execution": execution,
                "message": f"Workflow {workflow_id} executed successfully"
            }
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetExecutionsTool(BaseTool):
    """Get workflow executions"""
    
    name: str = "get_executions"
    description: str = "Get execution history for a workflow or all workflows"
    
    def run(self, workflow_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get executions"""
        try:
            url = f"{N8N_API_URL}/executions"
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id
            
            response = requests.get(url, headers=get_headers(), params=params)
            response.raise_for_status()
            
            executions = response.json().get("data", [])
            
            return {
                "success": True,
                "executions": executions,
                "count": len(executions)
            }
        except Exception as e:
            logger.error(f"Failed to get executions: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ActivateWorkflowTool(BaseTool):
    """Activate a workflow"""
    
    name: str = "activate_workflow"
    description: str = "Activate a workflow to enable automatic execution"
    
    def run(self, workflow_id: str) -> Dict[str, Any]:
        """Activate workflow"""
        try:
            url = f"{N8N_API_URL}/workflows/{workflow_id}/activate"
            response = requests.post(url, headers=get_headers())
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Workflow {workflow_id} activated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to activate workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class DeactivateWorkflowTool(BaseTool):
    """Deactivate a workflow"""
    
    name: str = "deactivate_workflow"
    description: str = "Deactivate a workflow to stop automatic execution"
    
    def run(self, workflow_id: str) -> Dict[str, Any]:
        """Deactivate workflow"""
        try:
            url = f"{N8N_API_URL}/workflows/{workflow_id}/deactivate"
            response = requests.post(url, headers=get_headers())
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Workflow {workflow_id} deactivated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to deactivate workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ImportWorkflowTool(BaseTool):
    """Import a workflow from JSON"""
    
    name: str = "import_workflow"
    description: str = "Import a workflow from a JSON string or file"
    
    def run(self, workflow_json: Union[str, Dict]) -> Dict[str, Any]:
        """Import workflow"""
        try:
            # Parse JSON if string
            if isinstance(workflow_json, str):
                workflow_data = json.loads(workflow_json)
            else:
                workflow_data = workflow_json
            
            # Ensure required fields
            if "name" not in workflow_data:
                workflow_data["name"] = "Imported Workflow"
            
            # Create the workflow
            create_tool = CreateWorkflowTool()
            result = create_tool.run(
                name=workflow_data.get("name"),
                nodes=workflow_data.get("nodes", []),
                connections=workflow_data.get("connections", {}),
                settings=workflow_data.get("settings"),
                active=workflow_data.get("active", False)
            )
            
            return result
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON: {e}"
            }
        except Exception as e:
            logger.error(f"Failed to import workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ExportWorkflowTool(BaseTool):
    """Export a workflow to JSON"""
    
    name: str = "export_workflow"
    description: str = "Export a workflow to JSON format"
    
    def run(self, workflow_id: str) -> Dict[str, Any]:
        """Export workflow"""
        try:
            # Get the workflow
            get_tool = GetWorkflowTool()
            result = get_tool.run(workflow_id)
            
            if not result["success"]:
                return result
            
            workflow = result["workflow"]
            
            # Clean up internal fields
            export_data = {
                "name": workflow.get("name"),
                "nodes": workflow.get("nodes", []),
                "connections": workflow.get("connections", {}),
                "settings": workflow.get("settings", {}),
                "active": workflow.get("active", False)
            }
            
            return {
                "success": True,
                "workflow_json": json.dumps(export_data, indent=2),
                "workflow_data": export_data
            }
        except Exception as e:
            logger.error(f"Failed to export workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetNodesTool(BaseTool):
    """Get available N8N nodes"""
    
    name: str = "get_nodes"
    description: str = "Get list of available N8N nodes and their types"
    
    def run(self, search: Optional[str] = None) -> Dict[str, Any]:
        """Get available nodes"""
        try:
            # This would typically call the N8N API to get node types
            # For now, return common node types
            nodes = [
                {"name": "Start", "type": "n8n-nodes-base.start", "category": "Core"},
                {"name": "Webhook", "type": "n8n-nodes-base.webhook", "category": "Core"},
                {"name": "HTTP Request", "type": "n8n-nodes-base.httpRequest", "category": "Core"},
                {"name": "Set", "type": "n8n-nodes-base.set", "category": "Core"},
                {"name": "IF", "type": "n8n-nodes-base.if", "category": "Core"},
                {"name": "Code", "type": "n8n-nodes-base.code", "category": "Core"},
                {"name": "Slack", "type": "n8n-nodes-base.slack", "category": "Communication"},
                {"name": "Gmail", "type": "n8n-nodes-base.gmail", "category": "Communication"},
                {"name": "Google Sheets", "type": "n8n-nodes-base.googleSheets", "category": "Data"},
                {"name": "Postgres", "type": "n8n-nodes-base.postgres", "category": "Database"},
                {"name": "MongoDB", "type": "n8n-nodes-base.mongoDb", "category": "Database"},
                {"name": "OpenAI", "type": "@n8n/n8n-nodes-langchain.openAi", "category": "AI"},
            ]
            
            # Filter by search term if provided
            if search:
                search_lower = search.lower()
                nodes = [n for n in nodes if search_lower in n["name"].lower() or 
                        search_lower in n["category"].lower()]
            
            return {
                "success": True,
                "nodes": nodes,
                "count": len(nodes)
            }
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Collect all tools for easy import
N8N_TOOLS = [
    ListWorkflowsTool(),
    GetWorkflowTool(),
    CreateWorkflowTool(),
    UpdateWorkflowTool(),
    ExecuteWorkflowTool(),
    GetExecutionsTool(),
    ActivateWorkflowTool(),
    DeactivateWorkflowTool(),
    ImportWorkflowTool(),
    ExportWorkflowTool(),
    GetNodesTool(),
]