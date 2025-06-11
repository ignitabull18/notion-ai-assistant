"""N8N custom tools for Agno"""
from .n8n_tools import N8N_TOOLS
from .n8n_extended_tools import N8N_EXTENDED_TOOLS
from .workflow_builder import WORKFLOW_BUILDER_TOOLS

# Combine all tools
ALL_N8N_TOOLS = N8N_TOOLS + N8N_EXTENDED_TOOLS + WORKFLOW_BUILDER_TOOLS

__all__ = ["N8N_TOOLS", "N8N_EXTENDED_TOOLS", "WORKFLOW_BUILDER_TOOLS", "ALL_N8N_TOOLS"]