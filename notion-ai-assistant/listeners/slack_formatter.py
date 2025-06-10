"""
Slack Block Kit formatter for beautiful agent responses
"""
import re
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SlackFormatter:
    """Format agent responses using Slack Block Kit for beautiful UI"""
    
    @staticmethod
    def format_notion_databases(databases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format a list of Notion databases into beautiful Slack blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Notion Databases",
                    "emoji": True
                }
            },
            {"type": "divider"}
        ]
        
        for db in databases:
            db_name = db.get('title', [{}])[0].get('plain_text', 'Untitled')
            db_id = db.get('id', '')
            created_time = db.get('created_time', '')[:10]  # Just date
            
            # Database block with info and button
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{db_name}*\n`{db_id}`\n_Created: {created_time}_"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Open in Notion",
                        "emoji": True
                    },
                    "url": f"https://notion.so/{db_id.replace('-', '')}",
                    "action_id": f"open_db_{db_id[:30]}"  # Truncate action_id to avoid length issues
                }
            })
        
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Found *{len(databases)}* databases in your workspace"[:150]  # Ensure context text isn't too long
                }
            ]
        })
        
        return blocks
    
    @staticmethod
    def format_agent_response(response_text: str) -> List[Dict[str, Any]]:
        """Convert agent markdown response to beautiful Slack blocks"""
        blocks = []
        
        # Special handling for database listings
        if "📊" in response_text and "URL:" in response_text:
            return SlackFormatter._format_database_listing(response_text)
        
        # Split response into paragraphs
        paragraphs = response_text.split('\n\n')
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            # Headers (marked with #)
            if para.startswith('#'):
                level = len(para) - len(para.lstrip('#'))
                header_text = para.lstrip('#').strip()
                
                if level == 1:
                    blocks.append({
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": header_text,
                            "emoji": True
                        }
                    })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{header_text}*"
                        }
                    })
                blocks.append({"type": "divider"})
                
            # Bullet lists
            elif para.strip().startswith(('- ', '• ', '* ', '1. ')):
                list_items = []
                for line in para.split('\n'):
                    if line.strip().startswith(('- ', '• ', '* ')):
                        list_items.append(line.strip()[2:])
                    elif re.match(r'^\d+\.\s', line.strip()):
                        list_items.append(re.sub(r'^\d+\.\s', '', line.strip()))
                
                if list_items:
                    formatted_list = '\n'.join([f"• {item}" for item in list_items])
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": formatted_list
                        }
                    })
                    
            # Code blocks
            elif para.startswith('```'):
                code_content = para.strip('`').strip()
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{code_content}```"
                    }
                })
                
            # Tables (enhanced support)
            elif '|' in para and para.count('|') > 2:
                # Parse markdown table
                lines = para.strip().split('\n')
                if len(lines) >= 2:
                    # Extract headers
                    header_line = lines[0]
                    headers = [h.strip() for h in header_line.split('|') if h.strip()]
                    
                    # Find data rows (skip separator line)
                    data_rows = []
                    for line in lines[2:] if len(lines) > 2 else lines[1:]:
                        if '|' in line:
                            row = [cell.strip() for cell in line.split('|') if cell.strip()]
                            if row:
                                data_rows.append(row)
                    
                    # Create a nice formatted table
                    if headers and data_rows:
                        # Add table header
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{' | '.join(headers)}*"
                            }
                        })
                        blocks.append({"type": "divider"})
                        
                        # For small tables (2-3 columns), use fields for compact view
                        if len(headers) <= 3:
                            for i in range(0, len(data_rows[:10]), 2):  # Process 2 rows at a time
                                fields = []
                                for j in range(2):  # Up to 2 rows per section
                                    if i + j < len(data_rows) and i + j < 10:
                                        row = data_rows[i + j]
                                        for k, (header, value) in enumerate(zip(headers, row)):
                                            fields.append({
                                                "type": "mrkdwn",
                                                "text": f"*{header}*\n{value}"
                                            })
                                
                                if fields:
                                    blocks.append({
                                        "type": "section",
                                        "fields": fields[:10]  # Slack limits to 10 fields per section
                                    })
                        else:
                            # For larger tables, use row-by-row format
                            for row in data_rows[:10]:
                                row_text = ""
                                for i, (header, value) in enumerate(zip(headers, row)):
                                    if i > 0:
                                        row_text += " • "
                                    row_text += f"*{header}:* {value}"
                                
                                blocks.append({
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": row_text
                                    }
                                })
                        
                        if len(data_rows) > 10:
                            blocks.append({
                                "type": "context",
                                "elements": [
                                    {
                                        "type": "mrkdwn",
                                        "text": f"_... and {len(data_rows) - 10} more rows_"
                                    }
                                ]
                            })
                    else:
                        # Fallback to code block
                        table_text = "```\n" + '\n'.join(lines) + "\n```"
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": table_text
                            }
                        })
                else:
                    # Single line, not a real table
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": para
                        }
                    })
                
            # Regular paragraphs
            else:
                # Convert Notion links to clickable buttons
                notion_link_pattern = r'https://(?:www\.)?notion\.so/([a-f0-9\-]+)'
                if re.search(notion_link_pattern, para):
                    # Extract the link and create a section with button
                    match = re.search(notion_link_pattern, para)
                    link_text = para[:match.start()].strip()
                    
                    # Truncate text if too long for Slack
                    if len(link_text) > 2000:
                        link_text = link_text[:1997] + "..."
                    
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": link_text if link_text else para[:2000]
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Open",  # Shorter text
                                "emoji": True
                            },
                            "url": match.group(0),
                            "action_id": f"open_{match.group(1)[:20]}"  # Shorter action ID
                        }
                    })
                else:
                    # Truncate long paragraphs
                    text = para if len(para) <= 2000 else para[:1997] + "..."
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": text
                        }
                    })
        
        # Add footer with Notion AI branding
        if blocks:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "✨ _Powered by Notion AI Assistant_"[:150]  # Ensure context text is under limit
                    }
                ]
            })
        
        # Slack has a limit of 50 blocks per message
        if len(blocks) > 50:
            # Truncate to 48 blocks and add a "truncated" message
            blocks = blocks[:48]
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Response truncated due to length. Ask for specific databases for more detail._"
                    }
                ]
            })
        
        return blocks
    
    @staticmethod
    def _format_database_listing(response_text: str) -> List[Dict[str, Any]]:
        """Special formatting for database listings with proper structure"""
        blocks = []
        
        # Add header
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Your Notion Databases",
                "emoji": True
            }
        })
        blocks.append({"type": "divider"})
        
        # Parse database entries
        lines = response_text.split('\n')
        current_db = {}
        db_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for database entry start (has emoji and bold text)
            if line.startswith('📊 **') or (line.startswith('**') and db_count > 0):
                # Save previous database if exists
                if current_db.get('name'):
                    db_block = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{current_db['name']}*\n`{current_db.get('id', 'No ID')}`"
                        }
                    }
                    
                    # Add button if URL exists
                    if current_db.get('url'):
                        db_block["accessory"] = {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Open",
                                "emoji": True
                            },
                            "url": current_db['url'],
                            "action_id": f"open_{db_count}"
                        }
                    
                    blocks.append(db_block)
                    db_count += 1
                
                # Start new database
                current_db = {'name': line.replace('📊', '').replace('**', '').strip()}
                
            elif line.startswith('ID:'):
                current_db['id'] = line.replace('ID:', '').strip()
                
            elif line.startswith('URL:'):
                current_db['url'] = line.replace('URL:', '').strip()
        
        # Add last database
        if current_db.get('name'):
            db_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{current_db['name']}*\n`{current_db.get('id', 'No ID')}`"
                }
            }
            
            if current_db.get('url'):
                db_block["accessory"] = {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Open",
                        "emoji": True
                    },
                    "url": current_db['url'],
                    "action_id": f"open_{db_count}"
                }
            
            blocks.append(db_block)
        
        # Add footer
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_Found {db_count + 1} databases in your workspace_"
                }
            ]
        })
        
        # Truncate if too many blocks
        if len(blocks) > 50:
            blocks = blocks[:48]
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Response truncated. Ask for specific databases for details._"
                    }
                ]
            })
        
        return blocks
    
    @staticmethod
    def format_error_message(error: str) -> List[Dict[str, Any]]:
        """Format error messages with helpful styling"""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Oops! Something went wrong*\n\n{error}"
                }
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Tip: Try rephrasing your request or check your Notion connection_"
                    }
                ]
            }
        ]
    
    @staticmethod
    def format_workspace_structure(structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format a workspace structure proposal with rich UI"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🏗️ Workspace Architecture Proposal",
                    "emoji": True
                }
            },
            {"type": "divider"}
        ]
        
        # Add interactive elements for each proposed component
        if 'databases' in structure:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Proposed Databases*"
                }
            })
            
            for db in structure['databases']:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{db['name']}*\n_{db.get('description', 'Database for tracking data')}_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Database",
                            "emoji": True
                        },
                        "style": "primary",
                        "action_id": f"create_db_{db['name'].lower().replace(' ', '_')}"
                    }
                })
        
        return blocks
    
    @staticmethod
    def format_status_update(action: str, status: str, details: Optional[str] = None) -> List[Dict[str, Any]]:
        """Format status updates with progress indicators"""
        status_emoji = {
            "starting": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌"
        }
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji.get(status, '📍')} *{action}*"
                }
            }
        ]
        
        if details:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": details
                    }
                ]
            })
        
        return blocks