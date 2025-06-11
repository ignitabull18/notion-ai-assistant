"""
N8N Canvas Manager - Create collaborative workflow documents
"""
import json
import logging
from typing import Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class N8NCanvasManager:
    """Manages canvas creation for N8N workflows"""
    
    def __init__(self, client: WebClient):
        """Initialize with Slack client"""
        self.client = client
    
    async def create_workflow_canvas(
        self,
        workflow: Dict[str, Any],
        channel_id: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a canvas with workflow JSON"""
        try:
            # Format workflow content
            content = self._format_workflow_content(workflow)
            
            # Create canvas
            response = self.client.files_upload_v2(
                channel=channel_id,
                thread_ts=thread_ts,
                title=f"{workflow.get('name', 'Workflow')} - Export",
                filename=f"{workflow.get('name', 'workflow').lower().replace(' ', '_')}_export.canvas",
                content=content,
                initial_comment=f"📋 Exported workflow: *{workflow.get('name', 'Workflow')}*"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Failed to create workflow canvas: {e}")
            raise
    
    async def create_documentation_canvas(
        self,
        documentation: str,
        workflow_name: str,
        channel_id: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a canvas with workflow documentation"""
        try:
            # Create canvas
            response = self.client.files_upload_v2(
                channel=channel_id,
                thread_ts=thread_ts,
                title=f"{workflow_name} - Documentation",
                filename=f"{workflow_name.lower().replace(' ', '_')}_docs.canvas",
                content=documentation,
                initial_comment=f"📚 Documentation for: *{workflow_name}*"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Failed to create documentation canvas: {e}")
            raise
    
    async def create_template_canvas(
        self,
        template_name: str,
        template_content: Dict[str, Any],
        channel_id: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a canvas with workflow template"""
        try:
            # Format template content
            content = self._format_template_content(template_name, template_content)
            
            # Create canvas
            response = self.client.files_upload_v2(
                channel=channel_id,
                thread_ts=thread_ts,
                title=f"Template: {template_name}",
                filename=f"template_{template_name.lower().replace(' ', '_')}.canvas",
                content=content,
                initial_comment=f"🎯 Workflow template: *{template_name}*"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Failed to create template canvas: {e}")
            raise
    
    async def create_analysis_canvas(
        self,
        analysis_title: str,
        analysis_content: str,
        workflow_data: Optional[Dict[str, Any]],
        channel_id: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a canvas with workflow analysis"""
        try:
            # Format analysis content
            content = self._format_analysis_content(
                analysis_title,
                analysis_content,
                workflow_data
            )
            
            # Create canvas
            response = self.client.files_upload_v2(
                channel=channel_id,
                thread_ts=thread_ts,
                title=f"Analysis: {analysis_title}",
                filename=f"analysis_{analysis_title.lower().replace(' ', '_')}.canvas",
                content=content,
                initial_comment=f"🔍 Workflow analysis: *{analysis_title}*"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Failed to create analysis canvas: {e}")
            raise
    
    def _format_workflow_content(self, workflow: Dict[str, Any]) -> str:
        """Format workflow for canvas"""
        content = f"# {workflow.get('name', 'Workflow')} - Export\n\n"
        
        # Add metadata
        content += "## Metadata\n\n"
        content += f"- **ID**: `{workflow.get('id', 'N/A')}`\n"
        content += f"- **Active**: {workflow.get('active', False)}\n"
        content += f"- **Created**: {workflow.get('createdAt', 'Unknown')}\n"
        content += f"- **Updated**: {workflow.get('updatedAt', 'Unknown')}\n\n"
        
        # Add description if available
        if workflow.get('description'):
            content += f"## Description\n\n{workflow['description']}\n\n"
        
        # Add nodes summary
        nodes = workflow.get('nodes', [])
        if nodes:
            content += f"## Nodes ({len(nodes)})\n\n"
            for node in nodes:
                content += f"### {node.get('name', 'Unnamed Node')}\n"
                content += f"- **Type**: `{node.get('type', 'Unknown')}`\n"
                content += f"- **Position**: ({node.get('position', {}).get('x', 0)}, {node.get('position', {}).get('y', 0)})\n"
                if node.get('parameters'):
                    content += f"- **Parameters**: {len(node['parameters'])} configured\n"
                content += "\n"
        
        # Add JSON export
        content += "## JSON Export\n\n```json\n"
        content += json.dumps(workflow, indent=2)
        content += "\n```\n\n"
        
        # Add import instructions
        content += "## Import Instructions\n\n"
        content += "1. Copy the JSON above\n"
        content += "2. In N8N, go to Workflows → Import from File\n"
        content += "3. Paste the JSON and click Import\n"
        content += "4. Review and activate the workflow\n"
        
        return content
    
    def _format_template_content(
        self,
        template_name: str,
        template_content: Dict[str, Any]
    ) -> str:
        """Format template for canvas"""
        content = f"# Template: {template_name}\n\n"
        
        # Add description
        if template_content.get('description'):
            content += f"## Description\n\n{template_content['description']}\n\n"
        
        # Add use cases
        if template_content.get('use_cases'):
            content += "## Use Cases\n\n"
            for use_case in template_content['use_cases']:
                content += f"- {use_case}\n"
            content += "\n"
        
        # Add requirements
        if template_content.get('requirements'):
            content += "## Requirements\n\n"
            for req in template_content['requirements']:
                content += f"- {req}\n"
            content += "\n"
        
        # Add workflow JSON
        if template_content.get('workflow'):
            content += "## Workflow Template\n\n```json\n"
            content += json.dumps(template_content['workflow'], indent=2)
            content += "\n```\n\n"
        
        # Add setup instructions
        if template_content.get('setup'):
            content += "## Setup Instructions\n\n"
            content += template_content['setup'] + "\n\n"
        
        # Add customization guide
        content += "## Customization Guide\n\n"
        content += "1. Import the template workflow\n"
        content += "2. Update credentials for each service\n"
        content += "3. Modify trigger conditions as needed\n"
        content += "4. Adjust node parameters for your use case\n"
        content += "5. Test with sample data before activating\n"
        
        return content
    
    def _format_analysis_content(
        self,
        analysis_title: str,
        analysis_content: str,
        workflow_data: Optional[Dict[str, Any]]
    ) -> str:
        """Format analysis for canvas"""
        content = f"# {analysis_title}\n\n"
        
        # Add analysis content
        content += analysis_content + "\n\n"
        
        # Add original workflow if provided
        if workflow_data:
            content += "## Original Workflow\n\n"
            content += f"**Name**: {workflow_data.get('name', 'Unknown')}\n"
            content += f"**Nodes**: {len(workflow_data.get('nodes', []))}\n\n"
            
            content += "### Workflow JSON\n\n```json\n"
            content += json.dumps(workflow_data, indent=2)
            content += "\n```\n"
        
        return content