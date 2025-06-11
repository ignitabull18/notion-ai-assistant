"""
Advanced UI Components for Notion AI Assistant with rich blocks and inputs
"""
from typing import List, Dict, Any, Optional


def create_notion_form_blocks() -> List[Dict[str, Any]]:
    """Create advanced form for Notion operations"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📝 Advanced Notion Form"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Create sophisticated Notion content with ",
                            "style": {"bold": True}
                        },
                        {
                            "type": "text",
                            "text": "advanced formatting",
                            "style": {"italic": True, "bold": True}
                        },
                        {
                            "type": "text",
                            "text": " and rich media support."
                        }
                    ]
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "input",
            "block_id": "notion_url",
            "element": {
                "type": "url_text_input",
                "action_id": "notion_url_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "https://notion.so/workspace/page-id"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "🔗 Notion Page URL"
            }
        },
        {
            "type": "input",
            "block_id": "embed_url",
            "element": {
                "type": "url_text_input",
                "action_id": "embed_url_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "https://youtube.com/watch?v=..."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "🎥 Media Embed URL"
            },
            "hint": {
                "type": "plain_text",
                "text": "YouTube, Vimeo, or other embeddable content"
            },
            "optional": True
        },
        {
            "type": "input",
            "block_id": "priority_score",
            "element": {
                "type": "number_input",
                "action_id": "priority_input",
                "is_decimal_allowed": False,
                "min_value": "1",
                "max_value": "10",
                "initial_value": "5"
            },
            "label": {
                "type": "plain_text",
                "text": "🎯 Priority Score (1-10)"
            }
        },
        {
            "type": "input",
            "block_id": "collaborator_email",
            "element": {
                "type": "email_text_input",
                "action_id": "collaborator_email_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "collaborator@company.com"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "👥 Add Collaborator by Email"
            },
            "optional": True
        }
    ]


def create_notion_database_schema_blocks() -> List[Dict[str, Any]]:
    """Create blocks for database schema visualization"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🗄️ Database Schema Designer"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Design your Notion database with "
                        },
                        {
                            "type": "text",
                            "text": "advanced property types",
                            "style": {"code": True}
                        },
                        {
                            "type": "text",
                            "text": " and "
                        },
                        {
                            "type": "text",
                            "text": "relations",
                            "style": {"italic": True}
                        }
                    ]
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Available Property Types:*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📝 Text"},
                    "action_id": "add_text_property",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔢 Number"},
                    "action_id": "add_number_property"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📅 Date"},
                    "action_id": "add_date_property"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✅ Checkbox"},
                    "action_id": "add_checkbox_property"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔗 Relation"},
                    "action_id": "add_relation_property",
                    "style": "danger"
                }
            ]
        }
    ]


def create_notion_template_gallery() -> List[Dict[str, Any]]:
    """Create a template gallery with rich formatting"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎨 Notion Template Gallery"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Project Management",
                                    "style": {"bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": " - Kanban boards, Gantt charts"
                                }
                            ]
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Knowledge Base",
                                    "style": {"bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": " - Wiki, documentation"
                                }
                            ]
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "CRM",
                                    "style": {"bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": " - Contact management, deals"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]


def create_notion_analytics_dashboard() -> List[Dict[str, Any]]:
    """Create an analytics dashboard for Notion workspace"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Notion Analytics Dashboard"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Your workspace has "
                        },
                        {
                            "type": "text",
                            "text": "157 pages",
                            "style": {"bold": True, "code": True}
                        },
                        {
                            "type": "text",
                            "text": " and "
                        },
                        {
                            "type": "text",
                            "text": "23 databases",
                            "style": {"bold": True, "code": True}
                        }
                    ]
                },
                {
                    "type": "rich_text_quote",
                    "elements": [
                        {
                            "type": "text",
                            "text": "📈 23% increase in content creation this month"
                        }
                    ]
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Active Users*\n`12`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Total Views*\n`1,234`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Avg. Page Size*\n`2.3 KB`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Templates*\n`8`"
                }
            ]
        }
    ]


def create_notion_video_tutorial_block() -> Dict[str, Any]:
    """Create a video tutorial block"""
    return {
        "type": "video",
        "title": {
            "type": "plain_text",
            "text": "Notion Advanced Features Tutorial"
        },
        "title_url": "https://www.notion.so/help/guides",
        "description": {
            "type": "plain_text",
            "text": "Learn how to use databases, relations, and formulas"
        },
        "video_url": "https://www.youtube.com/embed/notion-tutorial",
        "alt_text": "Notion tutorial video",
        "thumbnail_url": "https://www.notion.so/image/tutorial-thumb.jpg",
        "author_name": "Notion",
        "provider_name": "Notion.so"
    }
}