"""
Slack Canvas API integration for creating collaborative documents
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

from utils.logging import logger


class CanvasManager:
    """Manages Canvas creation and updates through Slack API"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_summary_canvas(
        self,
        channel_id: str,
        summary: str,
        timeframe: str,
        key_topics: List[str] = None,
        action_items: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with channel summary"""
        try:
            # Get channel info
            channel_info = self.client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
            
            # Create markdown content
            content = self._create_summary_markdown(
                channel_name, summary, timeframe, key_topics, action_items
            )
            
            # Create canvas
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"summary-{channel_name}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"📊 {channel_name} Summary - {timeframe}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating summary canvas: {e}")
            return None
    
    def create_meeting_canvas(
        self,
        channel_id: str,
        meeting_title: str,
        attendees: List[str] = None,
        agenda_items: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas for meeting notes"""
        try:
            content = self._create_meeting_markdown(meeting_title, attendees, agenda_items)
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"meeting-{datetime.now().strftime('%Y%m%d-%H%M')}.md",
                    "title": f"📝 {meeting_title}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating meeting canvas: {e}")
            return None
    
    def create_project_canvas(
        self,
        channel_id: str,
        project_name: str,
        objectives: List[str] = None,
        tasks: List[Dict[str, str]] = None,
        timeline: str = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas for project planning"""
        try:
            content = self._create_project_markdown(project_name, objectives, tasks, timeline)
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"project-{project_name.lower().replace(' ', '-')}.md",
                    "title": f"🚀 {project_name} - Project Plan"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating project canvas: {e}")
            return None
    
    def update_canvas(
        self,
        file_id: str,
        new_content: str,
        title: str = None
    ) -> Optional[Dict[str, Any]]:
        """Update existing canvas content"""
        try:
            # Note: This uses the files.edit method which may have limitations
            response = self.client.files_edit(
                file=file_id,
                content=new_content,
                title=title
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error updating canvas: {e}")
            return None
    
    def _create_summary_markdown(
        self,
        channel_name: str,
        summary: str,
        timeframe: str,
        key_topics: List[str] = None,
        action_items: List[str] = None
    ) -> str:
        """Create markdown content for summary canvas"""
        content = f"""# 📊 {channel_name} Summary

**Timeframe:** {timeframe}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
{summary}

"""
        
        if key_topics:
            content += "## 🏷️ Key Topics\n"
            for topic in key_topics:
                content += f"- {topic}\n"
            content += "\n"
        
        if action_items:
            content += "## ✅ Action Items\n"
            for item in action_items:
                content += f"- [ ] {item}\n"
            content += "\n"
        
        content += """## 📝 Notes
*Add your notes and follow-up items here*

---
*This summary was generated by Slack AI Assistant*"""
        
        return content
    
    def _create_meeting_markdown(
        self,
        meeting_title: str,
        attendees: List[str] = None,
        agenda_items: List[str] = None
    ) -> str:
        """Create markdown content for meeting canvas"""
        content = f"""# 📝 {meeting_title}

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Time:** {datetime.now().strftime('%H:%M')}

"""
        
        if attendees:
            content += "## 👥 Attendees\n"
            for attendee in attendees:
                content += f"- {attendee}\n"
            content += "\n"
        
        if agenda_items:
            content += "## 📋 Agenda\n"
            for i, item in enumerate(agenda_items, 1):
                content += f"{i}. {item}\n"
            content += "\n"
        
        content += """## 📝 Notes
*Meeting notes go here*

## ✅ Action Items
- [ ] *Add action items during the meeting*

## 🔄 Follow-up
*Next steps and follow-up items*

---
*Meeting canvas created by Slack AI Assistant*"""
        
        return content
    
    def _create_project_markdown(
        self,
        project_name: str,
        objectives: List[str] = None,
        tasks: List[Dict[str, str]] = None,
        timeline: str = None
    ) -> str:
        """Create markdown content for project canvas"""
        content = f"""# 🚀 {project_name}

**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** Planning

"""
        
        if timeline:
            content += f"**Timeline:** {timeline}\n\n"
        
        if objectives:
            content += "## 🎯 Objectives\n"
            for objective in objectives:
                content += f"- {objective}\n"
            content += "\n"
        
        content += "## 📋 Tasks\n"
        if tasks:
            for task in tasks:
                status = task.get('status', 'todo')
                checkbox = "- [x]" if status == 'done' else "- [ ]"
                assignee = f" (@{task.get('assignee')})" if task.get('assignee') else ""
                due_date = f" - Due: {task.get('due_date')}" if task.get('due_date') else ""
                content += f"{checkbox} {task.get('title', 'Untitled task')}{assignee}{due_date}\n"
        else:
            content += "- [ ] *Add project tasks here*\n"
        content += "\n"
        
        content += """## 🏗️ Project Plan
*Detailed project planning and milestones*

## 📊 Progress
*Track project progress and metrics*

## 🗒️ Notes
*Additional project notes and documentation*

---
*Project canvas created by Slack AI Assistant*"""
        
        return content
    
    def get_canvas_url(self, file_response: Dict[str, Any]) -> Optional[str]:
        """Extract canvas URL from file upload response"""
        try:
            if "files" in file_response and len(file_response["files"]) > 0:
                file_info = file_response["files"][0]
                return file_info.get("permalink", file_info.get("url_private"))
            return None
        except Exception as e:
            logger.error(f"Error extracting canvas URL: {e}")
            return None