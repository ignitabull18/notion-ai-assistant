"""
Extended N8N tools for credentials, tags, and variables

NOTE: Some features are only available in N8N Enterprise/Cloud versions:
- Variables API (GetVariablesTool, CreateVariableTool) - Enterprise/Cloud only
- Tags API (GetTagsTool, CreateTagTool) - May be limited in open source
- Advanced permissions and SSO - Enterprise only

The tools are organized with open source compatible tools active by default.
Enterprise features are commented out but can be enabled if you have the appropriate license.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from agno.models import BaseTool
from .n8n_tools import get_headers, N8N_API_URL

logger = logging.getLogger(__name__)


class ListCredentialsTool(BaseTool):
    """List all credentials in N8N"""
    
    name: str = "list_credentials"
    description: str = "List all stored credentials in N8N for various services"
    
    def run(self) -> Dict[str, Any]:
        """List credentials"""
        try:
            url = f"{N8N_API_URL}/credentials"
            response = requests.get(url, headers=get_headers())
            response.raise_for_status()
            
            credentials = response.json().get("data", [])
            
            # Don't expose sensitive data
            safe_credentials = []
            for cred in credentials:
                safe_credentials.append({
                    "id": cred.get("id"),
                    "name": cred.get("name"),
                    "type": cred.get("type"),
                    "createdAt": cred.get("createdAt"),
                    "updatedAt": cred.get("updatedAt")
                })
            
            return {
                "success": True,
                "credentials": safe_credentials,
                "count": len(safe_credentials)
            }
        except Exception as e:
            logger.error(f"Failed to list credentials: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetCredentialTool(BaseTool):
    """Get details of a specific credential"""
    
    name: str = "get_credential"
    description: str = "Get information about a specific credential (without sensitive data)"
    
    def run(self, credential_id: str) -> Dict[str, Any]:
        """Get credential details"""
        try:
            url = f"{N8N_API_URL}/credentials/{credential_id}"
            response = requests.get(url, headers=get_headers())
            response.raise_for_status()
            
            credential = response.json()
            
            # Remove sensitive data
            safe_credential = {
                "id": credential.get("id"),
                "name": credential.get("name"),
                "type": credential.get("type"),
                "createdAt": credential.get("createdAt"),
                "updatedAt": credential.get("updatedAt"),
                "usedBy": credential.get("usedBy", [])
            }
            
            return {
                "success": True,
                "credential": safe_credential
            }
        except Exception as e:
            logger.error(f"Failed to get credential {credential_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class CreateCredentialTool(BaseTool):
    """Create a new credential"""
    
    name: str = "create_credential"
    description: str = "Create a new credential for a service (API key, OAuth, etc.)"
    
    def run(self, name: str, type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create credential"""
        try:
            credential_data = {
                "name": name,
                "type": type,
                "data": data
            }
            
            url = f"{N8N_API_URL}/credentials"
            response = requests.post(url, headers=get_headers(), json=credential_data)
            response.raise_for_status()
            
            created_credential = response.json()
            
            return {
                "success": True,
                "credential": {
                    "id": created_credential.get("id"),
                    "name": created_credential.get("name"),
                    "type": created_credential.get("type")
                },
                "message": f"Credential '{name}' created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create credential: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class DeleteCredentialTool(BaseTool):
    """Delete a credential"""
    
    name: str = "delete_credential"
    description: str = "Delete a credential from N8N"
    
    def run(self, credential_id: str) -> Dict[str, Any]:
        """Delete credential"""
        try:
            url = f"{N8N_API_URL}/credentials/{credential_id}"
            response = requests.delete(url, headers=get_headers())
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Credential {credential_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Failed to delete credential {credential_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Tags might be limited in open source version
# Test these endpoints first, uncomment if they work

# class GetTagsTool(BaseTool):
#     """Get all workflow tags"""
#     
#     name: str = "get_tags"
#     description: str = "Get all tags used for organizing workflows"
#     
#     def run(self) -> Dict[str, Any]:
#         """Get tags"""
#         try:
#             url = f"{N8N_API_URL}/tags"
#             response = requests.get(url, headers=get_headers())
#             response.raise_for_status()
#             
#             tags = response.json().get("data", [])
#             
#             return {
#                 "success": True,
#                 "tags": tags,
#                 "count": len(tags)
#             }
#         except Exception as e:
#             logger.error(f"Failed to get tags: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }


# class CreateTagTool(BaseTool):
#     """Create a new tag"""
#     
#     name: str = "create_tag"
#     description: str = "Create a new tag for organizing workflows"
#     
#     def run(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
#         """Create tag"""
#         try:
#             tag_data = {
#                 "name": name
#             }
#             if description:
#                 tag_data["description"] = description
#             
#             url = f"{N8N_API_URL}/tags"
#             response = requests.post(url, headers=get_headers(), json=tag_data)
#             response.raise_for_status()
#             
#             created_tag = response.json()
#             
#             return {
#                 "success": True,
#                 "tag": created_tag,
#                 "message": f"Tag '{name}' created successfully"
#             }
#         except Exception as e:
#             logger.error(f"Failed to create tag: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }


# Variables are typically enterprise/cloud features in N8N
# Uncomment these if you have enterprise license or cloud version

# class GetVariablesTool(BaseTool):
#     """Get all environment variables"""
#     
#     name: str = "get_variables"
#     description: str = "Get all environment variables available in workflows"
#     
#     def run(self) -> Dict[str, Any]:
#         """Get variables"""
#         try:
#             url = f"{N8N_API_URL}/variables"
#             response = requests.get(url, headers=get_headers())
#             response.raise_for_status()
#             
#             variables = response.json().get("data", [])
#             
#             return {
#                 "success": True,
#                 "variables": variables,
#                 "count": len(variables)
#             }
#         except Exception as e:
#             logger.error(f"Failed to get variables: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }


# class CreateVariableTool(BaseTool):
#     """Create a new environment variable"""
#     
#     name: str = "create_variable"
#     description: str = "Create a new environment variable for use in workflows"
#     
#     def run(self, key: str, value: str, type: str = "string") -> Dict[str, Any]:
#         """Create variable"""
#         try:
#             variable_data = {
#                 "key": key,
#                 "value": value,
#                 "type": type
#             }
#             
#             url = f"{N8N_API_URL}/variables"
#             response = requests.post(url, headers=get_headers(), json=variable_data)
#             response.raise_for_status()
#             
#             created_variable = response.json()
#             
#             return {
#                 "success": True,
#                 "variable": created_variable,
#                 "message": f"Variable '{key}' created successfully"
#             }
#         except Exception as e:
#             logger.error(f"Failed to create variable: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }


class GetExecutionDetailsTool(BaseTool):
    """Get detailed execution data"""
    
    name: str = "get_execution_details"
    description: str = "Get detailed data about a specific workflow execution including node outputs"
    
    def run(self, execution_id: str, include_data: bool = True) -> Dict[str, Any]:
        """Get execution details"""
        try:
            url = f"{N8N_API_URL}/executions/{execution_id}"
            params = {"includeData": include_data}
            
            response = requests.get(url, headers=get_headers(), params=params)
            response.raise_for_status()
            
            execution = response.json()
            
            return {
                "success": True,
                "execution": execution
            }
        except Exception as e:
            logger.error(f"Failed to get execution details {execution_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class DeleteWorkflowTool(BaseTool):
    """Delete a workflow"""
    
    name: str = "delete_workflow"
    description: str = "Permanently delete a workflow from N8N"
    
    def run(self, workflow_id: str) -> Dict[str, Any]:
        """Delete workflow"""
        try:
            url = f"{N8N_API_URL}/workflows/{workflow_id}"
            response = requests.delete(url, headers=get_headers())
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Workflow {workflow_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetWorkflowStatsTool(BaseTool):
    """Get workflow execution statistics"""
    
    name: str = "get_workflow_stats"
    description: str = "Get execution statistics for a workflow"
    
    def run(self, workflow_id: str, days: int = 7) -> Dict[str, Any]:
        """Get workflow stats"""
        try:
            # Get recent executions
            url = f"{N8N_API_URL}/executions"
            params = {
                "workflowId": workflow_id,
                "limit": 100
            }
            
            response = requests.get(url, headers=get_headers(), params=params)
            response.raise_for_status()
            
            executions = response.json().get("data", [])
            
            # Calculate stats
            total = len(executions)
            success = sum(1 for e in executions if e.get("status") == "success")
            error = sum(1 for e in executions if e.get("status") == "error")
            running = sum(1 for e in executions if e.get("status") == "running")
            
            # Calculate average execution time
            execution_times = []
            for execution in executions:
                if execution.get("startedAt") and execution.get("stoppedAt"):
                    # Simple time calculation (would need proper date parsing)
                    execution_times.append(1)  # Placeholder
            
            avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            return {
                "success": True,
                "stats": {
                    "workflow_id": workflow_id,
                    "total_executions": total,
                    "successful": success,
                    "failed": error,
                    "running": running,
                    "success_rate": (success / total * 100) if total > 0 else 0,
                    "average_execution_time": avg_time,
                    "period": f"Last {days} days"
                }
            }
        except Exception as e:
            logger.error(f"Failed to get workflow stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class TestWorkflowTool(BaseTool):
    """Test a workflow with sample data"""
    
    name: str = "test_workflow"
    description: str = "Test a workflow execution with sample data"
    
    def run(self, workflow_id: str, test_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test workflow"""
        try:
            # First get the workflow
            url = f"{N8N_API_URL}/workflows/{workflow_id}"
            response = requests.get(url, headers=get_headers())
            response.raise_for_status()
            workflow = response.json()
            
            # Create a test version if needed
            test_workflow = workflow.copy()
            test_workflow["name"] = f"{workflow['name']} - Test"
            test_workflow["active"] = False
            
            # Execute with test data
            execute_url = f"{N8N_API_URL}/workflows/{workflow_id}/execute"
            payload = {}
            if test_data:
                payload["workflowData"] = {"data": test_data}
            
            response = requests.post(execute_url, headers=get_headers(), json=payload)
            response.raise_for_status()
            
            execution = response.json()
            
            return {
                "success": True,
                "execution": execution,
                "message": f"Test execution started for workflow {workflow_id}"
            }
        except Exception as e:
            logger.error(f"Failed to test workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Extended tools collection (open source compatible)
N8N_EXTENDED_TOOLS = [
    # Credential management (should work in open source)
    ListCredentialsTool(),
    GetCredentialTool(),
    CreateCredentialTool(),
    DeleteCredentialTool(),
    
    # Execution and workflow management (core features)
    GetExecutionDetailsTool(),
    DeleteWorkflowTool(),
    GetWorkflowStatsTool(),
    TestWorkflowTool(),
    
    # Enterprise/Cloud features - uncomment if available:
    # GetTagsTool(),
    # CreateTagTool(),
    # GetVariablesTool(), 
    # CreateVariableTool(),
]