"""
Advanced UI Components showcasing all Slack Block Kit elements including:
- Rich Text Blocks
- Video Blocks
- Advanced Input Elements (email, url, number)
- All available Block Kit components
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


def create_advanced_input_demo_blocks() -> List[Dict[str, Any]]:
    """Create blocks showcasing all advanced input elements"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎨 Advanced Input Elements Demo"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "This showcases all available Slack input elements and blocks."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "input",
            "block_id": "email_input_block",
            "element": {
                "type": "email_text_input",
                "action_id": "email_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "user@example.com"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "📧 Email Input"
            },
            "hint": {
                "type": "plain_text",
                "text": "Enter a valid email address"
            }
        },
        {
            "type": "input",
            "block_id": "url_input_block",
            "element": {
                "type": "url_text_input",
                "action_id": "url_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "https://example.com"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "🔗 URL Input"
            },
            "hint": {
                "type": "plain_text",
                "text": "Enter a valid URL"
            }
        },
        {
            "type": "input",
            "block_id": "number_input_block",
            "element": {
                "type": "number_input",
                "action_id": "number_input",
                "is_decimal_allowed": True,
                "min_value": "0",
                "max_value": "1000",
                "initial_value": "10"
            },
            "label": {
                "type": "plain_text",
                "text": "🔢 Number Input"
            },
            "hint": {
                "type": "plain_text",
                "text": "Enter a number between 0 and 1000"
            }
        },
        {
            "type": "input",
            "block_id": "time_picker_block",
            "element": {
                "type": "timepicker",
                "action_id": "time_input",
                "initial_time": "13:30",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select time"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "⏰ Time Picker"
            }
        },
        {
            "type": "input",
            "block_id": "multi_select_block",
            "element": {
                "type": "multi_static_select",
                "action_id": "multi_select_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select multiple options"
                },
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Option A"},
                        "value": "option_a"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Option B"},
                        "value": "option_b"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Option C"},
                        "value": "option_c"
                    }
                ],
                "max_selected_items": 2
            },
            "label": {
                "type": "plain_text",
                "text": "🎯 Multi-Select"
            }
        },
        {
            "type": "input",
            "block_id": "overflow_menu_block",
            "element": {
                "type": "overflow",
                "action_id": "overflow_input",
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Edit"},
                        "value": "edit"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Delete"},
                        "value": "delete"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Archive"},
                        "value": "archive"
                    }
                ]
            },
            "label": {
                "type": "plain_text",
                "text": "⋯ Overflow Menu"
            }
        }
    ]


def create_rich_text_block_demo() -> Dict[str, Any]:
    """Create a rich text block with all formatting options"""
    return {
        "type": "rich_text",
        "elements": [
            {
                "type": "rich_text_section",
                "elements": [
                    {
                        "type": "text",
                        "text": "This is a ",
                    },
                    {
                        "type": "text",
                        "text": "rich text block",
                        "style": {"bold": True}
                    },
                    {
                        "type": "text",
                        "text": " with "
                    },
                    {
                        "type": "text",
                        "text": "various",
                        "style": {"italic": True}
                    },
                    {
                        "type": "text",
                        "text": " formatting options.\n"
                    }
                ]
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Bold text",
                                "style": {"bold": True}
                            }
                        ]
                    },
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Italic text",
                                "style": {"italic": True}
                            }
                        ]
                    },
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Strikethrough text",
                                "style": {"strike": True}
                            }
                        ]
                    },
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Code text",
                                "style": {"code": True}
                            }
                        ]
                    }
                ]
            },
            {
                "type": "rich_text_section",
                "elements": [
                    {
                        "type": "text",
                        "text": "\nYou can also include "
                    },
                    {
                        "type": "link",
                        "url": "https://slack.com",
                        "text": "links"
                    },
                    {
                        "type": "text",
                        "text": ", "
                    },
                    {
                        "type": "user",
                        "user_id": "U1234567890"
                    },
                    {
                        "type": "text",
                        "text": " mentions, and "
                    },
                    {
                        "type": "channel",
                        "channel_id": "C1234567890"
                    },
                    {
                        "type": "text",
                        "text": " channel references."
                    }
                ]
            },
            {
                "type": "rich_text_quote",
                "elements": [
                    {
                        "type": "text",
                        "text": "This is a quoted text block that stands out from the rest of the content."
                    }
                ]
            },
            {
                "type": "rich_text_preformatted",
                "elements": [
                    {
                        "type": "text",
                        "text": "{\n  \"type\": \"rich_text\",\n  \"elements\": [...]\n}"
                    }
                ]
            }
        ]
    }


def create_video_block_demo() -> Dict[str, Any]:
    """Create a video block"""
    return {
        "type": "video",
        "title": {
            "type": "plain_text",
            "text": "Demo Video"
        },
        "title_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "description": {
            "type": "plain_text",
            "text": "This is a video block that can embed video content"
        },
        "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "alt_text": "Demo video",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "author_name": "Slack Demo",
        "provider_name": "YouTube",
        "provider_icon_url": "https://www.youtube.com/favicon.ico"
    }


def create_file_block_demo() -> Dict[str, Any]:
    """Create a file block"""
    return {
        "type": "file",
        "external_id": "ABCD1",
        "source": "remote"
    }


def create_complete_ui_showcase() -> List[Dict[str, Any]]:
    """Create a complete showcase of all UI elements"""
    blocks = []
    
    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🚀 Complete Slack UI Components Showcase"
        }
    })
    
    # Rich Text Demo
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Rich Text Blocks*"
        }
    })
    blocks.append(create_rich_text_block_demo())
    
    blocks.append({"type": "divider"})
    
    # Video Block Demo
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Video Blocks*"
        }
    })
    blocks.append(create_video_block_demo())
    
    blocks.append({"type": "divider"})
    
    # Advanced Inputs
    blocks.extend(create_advanced_input_demo_blocks())
    
    blocks.append({"type": "divider"})
    
    # Context blocks
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "image",
                "image_url": "https://api.slack.com/img/blocks/bkb_template_images/placeholder.png",
                "alt_text": "placeholder"
            },
            {
                "type": "mrkdwn",
                "text": "This is a context block with image and text"
            }
        ]
    })
    
    # Actions block with all button styles
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Primary"},
                "style": "primary",
                "action_id": "primary_button"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Danger"},
                "style": "danger",
                "action_id": "danger_button"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Default"},
                "action_id": "default_button"
            }
        ]
    })
    
    return blocks


def create_form_with_validation_modal() -> Dict[str, Any]:
    """Create a modal with form validation example"""
    return {
        "type": "modal",
        "callback_id": "advanced_form_modal",
        "title": {
            "type": "plain_text",
            "text": "Advanced Form"
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This form demonstrates all input types with validation"
                }
            },
            {
                "type": "input",
                "block_id": "email_block",
                "element": {
                    "type": "email_text_input",
                    "action_id": "email_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "john.doe@example.com"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Email Address"
                }
            },
            {
                "type": "input",
                "block_id": "website_block",
                "element": {
                    "type": "url_text_input",
                    "action_id": "url_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "https://example.com"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Website URL"
                }
            },
            {
                "type": "input",
                "block_id": "age_block",
                "element": {
                    "type": "number_input",
                    "action_id": "age_input",
                    "is_decimal_allowed": False,
                    "min_value": "18",
                    "max_value": "120"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Age"
                }
            },
            {
                "type": "input",
                "block_id": "phone_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "phone_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "+1 (555) 123-4567"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Phone Number"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "Include country code"
                }
            },
            {
                "type": "input",
                "block_id": "preferences_block",
                "element": {
                    "type": "checkboxes",
                    "action_id": "preferences_input",
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Email notifications"},
                            "value": "email_notif"
                        },
                        {
                            "text": {"type": "plain_text", "text": "SMS alerts"},
                            "value": "sms_alerts"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Weekly digest"},
                            "value": "weekly_digest"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Notification Preferences"
                },
                "optional": True
            }
        ]
    }


def create_interactive_home_tab() -> Dict[str, Any]:
    """Create an interactive home tab with all components"""
    return {
        "type": "home",
        "blocks": create_complete_ui_showcase()
    }