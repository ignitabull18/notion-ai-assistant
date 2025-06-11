"""
Workflow builder from screenshots and natural language
Uses OpenAI Vision API to analyze workflow screenshots
"""
import os
import base64
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from agno.models import BaseTool

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AnalyzeWorkflowScreenshotTool(BaseTool):
    """Analyze a workflow screenshot and extract structure"""
    
    name: str = "analyze_workflow_screenshot"
    description: str = "Analyze a screenshot of an N8N workflow and extract the nodes and connections"
    
    def run(self, image_path: str) -> Dict[str, Any]:
        """Analyze workflow screenshot"""
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Call OpenAI Vision API (note: o1 doesn't support vision, keep GPT-4V for screenshots)
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing N8N workflow screenshots. 
                        Extract the workflow structure including:
                        1. All nodes (type, position, configuration)
                        2. Connections between nodes
                        3. Node settings and parameters
                        4. Workflow logic and flow
                        
                        Return a structured JSON that can be used to recreate the workflow."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this N8N workflow and extract its structure:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            # Parse the response
            analysis = response.choices[0].message.content
            
            # Extract workflow structure
            workflow_structure = self._parse_workflow_analysis(analysis)
            
            return {
                "success": True,
                "analysis": analysis,
                "workflow_structure": workflow_structure
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze screenshot: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_workflow_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse the analysis to extract workflow structure"""
        try:
            # This would parse the GPT response to extract structured data
            # For now, return a basic structure
            return {
                "nodes": [],
                "connections": {},
                "description": analysis
            }
        except Exception as e:
            logger.error(f"Failed to parse analysis: {e}")
            return {}


class BuildWorkflowFromDescriptionTool(BaseTool):
    """Build a workflow from natural language description"""
    
    name: str = "build_workflow_from_description"
    description: str = "Create an N8N workflow from a natural language description"
    
    def run(self, description: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Build workflow from description"""
        try:
            # Use o3 to design the workflow
            response = client.chat.completions.create(
                model="o3",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an N8N workflow expert. Create workflow JSON from descriptions.
                        
                        For each workflow, determine:
                        1. Required nodes and their types
                        2. Node configurations
                        3. Connections between nodes
                        4. Trigger conditions
                        
                        Return valid N8N workflow JSON with nodes and connections."""
                    },
                    {
                        "role": "user",
                        "content": f"Create an N8N workflow for: {description}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            workflow_json = response.choices[0].message.content
            
            # Parse and validate
            import json
            workflow_data = json.loads(workflow_json)
            
            # Ensure workflow has a name
            if not name:
                name = workflow_data.get("name", "Generated Workflow")
            workflow_data["name"] = name
            
            return {
                "success": True,
                "workflow": workflow_data,
                "message": f"Workflow '{name}' designed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to build workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class SuggestWorkflowImprovementsTool(BaseTool):
    """Suggest improvements for an existing workflow"""
    
    name: str = "suggest_workflow_improvements"
    description: str = "Analyze a workflow and suggest optimizations or improvements"
    
    def run(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow improvements"""
        try:
            # Use o3 to analyze and suggest improvements
            response = client.chat.completions.create(
                model="o3",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an N8N workflow optimization expert.
                        Analyze workflows and suggest improvements for:
                        1. Performance optimization
                        2. Error handling
                        3. Simplification
                        4. Best practices
                        5. Additional useful nodes
                        
                        Provide specific, actionable suggestions."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this workflow and suggest improvements: {json.dumps(workflow_data, indent=2)}"
                    }
                ]
            )
            
            suggestions = response.choices[0].message.content
            
            return {
                "success": True,
                "suggestions": suggestions,
                "original_workflow": workflow_data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GenerateWorkflowDocumentationTool(BaseTool):
    """Generate documentation for a workflow"""
    
    name: str = "generate_workflow_documentation"
    description: str = "Generate comprehensive documentation for an N8N workflow"
    
    def run(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow documentation"""
        try:
            # Use o3 to generate documentation
            response = client.chat.completions.create(
                model="o3",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a technical documentation expert for N8N workflows.
                        Generate comprehensive documentation including:
                        1. Overview and purpose
                        2. Prerequisites and setup
                        3. Node-by-node explanation
                        4. Configuration details
                        5. Usage examples
                        6. Troubleshooting tips
                        
                        Format in clean Markdown."""
                    },
                    {
                        "role": "user",
                        "content": f"Generate documentation for this workflow: {json.dumps(workflow_data, indent=2)}"
                    }
                ]
            )
            
            documentation = response.choices[0].message.content
            
            return {
                "success": True,
                "documentation": documentation,
                "workflow_name": workflow_data.get("name", "Unnamed Workflow")
            }
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Workflow builder tools collection
WORKFLOW_BUILDER_TOOLS = [
    AnalyzeWorkflowScreenshotTool(),
    BuildWorkflowFromDescriptionTool(),
    SuggestWorkflowImprovementsTool(),
    GenerateWorkflowDocumentationTool(),
]