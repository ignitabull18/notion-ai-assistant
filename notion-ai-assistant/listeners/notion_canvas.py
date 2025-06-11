"""
Notion Canvas Integration for collaborative workspace documentation
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

from utils.logging import logger


class NotionCanvasManager:
    """Manages Canvas creation for Notion workspace documentation"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_workspace_summary_canvas(
        self,
        channel_id: str,
        workspace_name: str,
        databases: List[Dict[str, Any]],
        pages: List[Dict[str, Any]],
        insights: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with Notion workspace summary"""
        try:
            content = self._create_workspace_summary_markdown(
                workspace_name, databases, pages, insights
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"notion-workspace-{workspace_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"📊 Notion Workspace Summary: {workspace_name}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating workspace summary canvas: {e}")
            return None
    
    def create_database_schema_canvas(
        self,
        channel_id: str,
        database_name: str,
        database_id: str,
        properties: List[Dict[str, Any]],
        sample_data: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas documenting database schema"""
        try:
            content = self._create_database_schema_markdown(
                database_name, database_id, properties, sample_data
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"notion-db-schema-{database_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"🗄️ Database Schema: {database_name}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating database schema canvas: {e}")
            return None
    
    def create_project_template_canvas(
        self,
        channel_id: str,
        project_name: str,
        template_type: str,
        structure: Dict[str, Any],
        tasks: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas with project template"""
        try:
            content = self._create_project_template_markdown(
                project_name, template_type, structure, tasks
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"notion-template-{template_type}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"📋 Project Template: {project_name}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating project template canvas: {e}")
            return None
    
    def create_workflow_documentation_canvas(
        self,
        channel_id: str,
        workflow_name: str,
        steps: List[Dict[str, Any]],
        automation_rules: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas documenting Notion workflows"""
        try:
            content = self._create_workflow_documentation_markdown(
                workflow_name, steps, automation_rules
            )
            
            response = self.client.files_upload_v2(
                channels=[channel_id],
                file_uploads=[{
                    "file": content.encode('utf-8'),
                    "filename": f"notion-workflow-{workflow_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md",
                    "title": f"🔄 Workflow Documentation: {workflow_name}"
                }],
                filetype="canvas"
            )
            
            return response
            
        except SlackApiError as e:
            logger.error(f"Error creating workflow documentation canvas: {e}")
            return None
    
    def _create_workspace_summary_markdown(
        self,
        workspace_name: str,
        databases: List[Dict[str, Any]],
        pages: List[Dict[str, Any]],
        insights: Dict[str, Any] = None
    ) -> str:
        """Create markdown content for workspace summary canvas"""
        content = f"""# 📊 Notion Workspace Summary: {workspace_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Total Databases:** {len(databases)}  
**Total Pages:** {len(pages)}

## 📈 Workspace Overview

"""
        
        if insights:
            content += f"""**Active Users:** {insights.get('active_users', 'Unknown')}  
**Last Activity:** {insights.get('last_activity', 'Unknown')}  
**Storage Used:** {insights.get('storage_used', 'Unknown')}  
**Workspace Age:** {insights.get('workspace_age', 'Unknown')}

"""
        
        content += "## 🗄️ Databases\n\n"
        
        for db in databases[:10]:
            content += f"""### {db.get('title', 'Untitled Database')}

**ID:** `{db.get('id', 'N/A')}`  
**URL:** https://notion.so/{db.get('id', '').replace('-', '')}  
**Properties:** {len(db.get('properties', []))}  
**Records:** {db.get('record_count', 'Unknown')}

**Key Properties:**
"""
            for prop in list(db.get('properties', {}).items())[:5]:
                content += f"- **{prop[0]}**: {prop[1].get('type', 'Unknown type')}\n"
            
            content += "\n---\n\n"
        
        content += "## 📄 Recent Pages\n\n"
        
        for page in pages[:10]:
            content += f"""### {page.get('title', 'Untitled Page')}

**ID:** `{page.get('id', 'N/A')}`  
**URL:** https://notion.so/{page.get('id', '').replace('-', '')}  
**Created:** {page.get('created_time', 'Unknown')}  
**Last Edited:** {page.get('last_edited_time', 'Unknown')}

---

"""
        
        content += """## 🎯 Optimization Opportunities

### Database Organization
- [ ] Review databases with similar properties for consolidation
- [ ] Add missing relations between connected databases
- [ ] Standardize property naming conventions
- [ ] Create database templates for common use cases

### Page Structure
- [ ] Organize pages into clear hierarchy
- [ ] Add tags or categories for better navigation
- [ ] Create page templates for recurring content
- [ ] Archive outdated pages

### Workflow Automation
- [ ] Set up recurring task templates
- [ ] Create automated status updates
- [ ] Implement notification rules
- [ ] Build integration workflows

## 📋 Next Steps

1. **Audit Content:** Review and categorize all pages and databases
2. **Define Standards:** Create naming and structure conventions
3. **Build Templates:** Develop reusable templates for common workflows
4. **Train Team:** Document best practices and train users
5. **Monitor Usage:** Track adoption and optimize based on usage patterns

## 🗒️ Notes

*Add team notes and workspace-specific insights here*

---
*Summary generated by Notion AI Assistant*"""
        
        return content
    
    def _create_database_schema_markdown(
        self,
        database_name: str,
        database_id: str,
        properties: List[Dict[str, Any]],
        sample_data: List[Dict[str, Any]] = None
    ) -> str:
        """Create markdown content for database schema canvas"""
        content = f"""# 🗄️ Database Schema: {database_name}

**Database ID:** `{database_id}`  
**Notion URL:** https://notion.so/{database_id.replace('-', '')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 Schema Overview

| Property | Type | Configuration | Description |
|----------|------|---------------|-------------|
"""
        
        for prop in properties:
            prop_type = prop.get('type', 'Unknown')
            config = prop.get('config', {})
            content += f"| **{prop.get('name', 'Unknown')}** | {prop_type} | "
            
            # Add configuration details based on type
            if prop_type == 'select':
                options = config.get('options', [])
                content += f"{len(options)} options"
            elif prop_type == 'relation':
                content += f"→ {config.get('database_name', 'Unknown DB')}"
            elif prop_type == 'formula':
                content += "Calculated"
            else:
                content += "Standard"
            
            content += f" | {prop.get('description', '-')} |\n"
        
        content += """

## 🔗 Relationships

"""
        
        relations = [p for p in properties if p.get('type') == 'relation']
        if relations:
            for rel in relations:
                content += f"- **{rel.get('name')}** → {rel.get('config', {}).get('database_name', 'Unknown Database')}\n"
        else:
            content += "*No relationships defined*\n"
        
        if sample_data:
            content += """

## 📝 Sample Data

| ID | Title | Key Properties |
|----|-------|----------------|
"""
            for item in sample_data[:5]:
                content += f"| {item.get('id', 'N/A')[:8]}... | {item.get('title', 'Untitled')} | "
                # Add key property values
                key_props = []
                for k, v in item.get('properties', {}).items()[:3]:
                    if isinstance(v, dict):
                        key_props.append(f"{k}: {v.get('value', 'N/A')}")
                    else:
                        key_props.append(f"{k}: {v}")
                content += ", ".join(key_props) + " |\n"
        
        content += """

## 🎯 Schema Best Practices

### Property Guidelines
- [ ] Use consistent naming conventions (camelCase or snake_case)
- [ ] Add descriptions to complex properties
- [ ] Group related properties together
- [ ] Use appropriate property types for data

### Performance Optimization
- [ ] Limit formula complexity
- [ ] Use filters instead of complex relations
- [ ] Archive old data regularly
- [ ] Index frequently searched properties

### Data Integrity
- [ ] Set required properties appropriately
- [ ] Use select/multi-select for controlled values
- [ ] Implement validation through formulas
- [ ] Regular data quality audits

## 🔧 Common Queries

```notion
// Find all items created this week
filter: created_time >= start_of_week()

// Find incomplete tasks
filter: status != "Done" AND status != "Archived"

// Find high-priority items
filter: priority = "High" OR priority = "Critical"
```

## 📋 Migration Checklist

- [ ] Export current data backup
- [ ] Document schema changes
- [ ] Test with sample data
- [ ] Migrate in batches
- [ ] Verify data integrity
- [ ] Update dependent views/filters

## 🗒️ Schema Notes

*Add implementation notes and considerations here*

---
*Schema documentation by Notion AI Assistant*"""
        
        return content
    
    def _create_project_template_markdown(
        self,
        project_name: str,
        template_type: str,
        structure: Dict[str, Any],
        tasks: List[Dict[str, Any]] = None
    ) -> str:
        """Create markdown content for project template canvas"""
        content = f"""# 📋 Project Template: {project_name}

**Template Type:** {template_type}  
**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Version:** 1.0

## 🎯 Template Overview

This template provides a structured approach for {template_type} projects in Notion.

## 📁 Project Structure

```
{project_name}/
├── 📊 Project Dashboard
├── 📋 Tasks Database
├── 📄 Documentation/
│   ├── Requirements
│   ├── Design Specs
│   └── Meeting Notes
├── 🎯 Goals & Milestones
├── 👥 Team Directory
└── 📈 Progress Reports
```

## 🗄️ Required Databases

### 1. Tasks Database
**Properties:**
- Title (Title)
- Status (Select: Not Started, In Progress, Review, Done)
- Priority (Select: Low, Medium, High, Critical)
- Assignee (Person)
- Due Date (Date)
- Sprint (Relation → Sprints DB)
- Labels (Multi-select)
- Effort (Number: Story points)

### 2. Sprints Database
**Properties:**
- Sprint Name (Title)
- Start Date (Date)
- End Date (Date)
- Goals (Text)
- Status (Select: Planning, Active, Completed)
- Velocity (Rollup: Sum of completed story points)

### 3. Team Database
**Properties:**
- Name (Title)
- Role (Select)
- Email (Email)
- Skills (Multi-select)
- Availability (Select)
- Current Tasks (Relation → Tasks DB)

## 📄 Page Templates

### Project Homepage
```markdown
# {Project Name}

## 🎯 Project Overview
[Brief description of the project]

## 📊 Key Metrics
- Start Date: {date}
- Target Completion: {date}
- Team Size: {number}
- Budget: ${amount}

## 🔗 Quick Links
- [[Tasks Database]]
- [[Project Timeline]]
- [[Team Directory]]
- [[Documentation]]

## 📈 Current Status
[Status summary and progress update]
```

### Sprint Planning Page
```markdown
# Sprint {number} Planning

## 🎯 Sprint Goals
1. Goal 1
2. Goal 2
3. Goal 3

## 📋 Committed Tasks
[Linked view of sprint tasks]

## 👥 Team Capacity
[Team availability matrix]

## 📝 Planning Notes
[Discussion points and decisions]
```

"""
        
        if tasks:
            content += "## ✅ Template Tasks\n\n"
            content += "| Task | Category | Duration | Dependencies |\n"
            content += "|------|----------|----------|-------------|\n"
            
            for task in tasks[:10]:
                content += f"| {task.get('name', 'Task')} | {task.get('category', 'General')} | {task.get('duration', 'TBD')} | {task.get('dependencies', 'None')} |\n"
        
        content += """

## 🔄 Workflow Automation

### Recurring Tasks
- Weekly team standup
- Sprint planning session
- Sprint retrospective
- Stakeholder updates

### Automation Rules
1. **Status Updates:** When task status changes to "Done", update sprint progress
2. **Notifications:** Alert assignee 2 days before due date
3. **Archival:** Move completed sprints to archive after 30 days
4. **Reports:** Generate weekly progress report every Friday

## 📊 Views and Filters

### Recommended Views
1. **Kanban Board:** Group by Status, filter by current sprint
2. **Calendar:** Show tasks by due date
3. **Team Workload:** Group by Assignee, show current sprint only
4. **Priority Matrix:** Group by Priority and Status
5. **Sprint Burndown:** Timeline view with effort rollup

## 🎨 Customization Guide

### For Different Project Types
- **Software Development:** Add Git integration, bug tracking
- **Marketing Campaign:** Add content calendar, channel tracking
- **Product Launch:** Add market research, competitor analysis
- **Research Project:** Add literature database, experiment tracking

### Scaling Considerations
- For teams > 10: Add sub-team structure
- For projects > 6 months: Add quarterly planning
- For multi-project: Add portfolio dashboard

## 🚀 Getting Started

1. **Duplicate Template:** Create a copy in your workspace
2. **Customize Properties:** Adjust database schemas for your needs
3. **Set Up Team:** Add team members and roles
4. **Create First Sprint:** Plan initial tasks and timeline
5. **Configure Automation:** Set up recurring tasks and notifications

## 📋 Checklist

- [ ] Rename project with actual name
- [ ] Add team members to Team database
- [ ] Set project start and end dates
- [ ] Create initial sprint
- [ ] Import or create initial tasks
- [ ] Set up automation rules
- [ ] Configure views and filters
- [ ] Schedule kickoff meeting

## 🗒️ Template Notes

*Customization notes and tips*

---
*Template created by Notion AI Assistant*"""
        
        return content
    
    def _create_workflow_documentation_markdown(
        self,
        workflow_name: str,
        steps: List[Dict[str, Any]],
        automation_rules: List[str] = None
    ) -> str:
        """Create markdown content for workflow documentation canvas"""
        content = f"""# 🔄 Workflow Documentation: {workflow_name}

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Status:** Active  
**Owner:** Workspace Admin

## 📋 Workflow Overview

This workflow automates {workflow_name} processes in your Notion workspace.

## 🔀 Process Flow

```mermaid
graph TD
    A[Start] --> B{Trigger Event}
"""
        
        for i, step in enumerate(steps):
            if i == 0:
                content += f"    B --> C{i}[{step.get('name', f'Step {i+1}')}]\n"
            elif i == len(steps) - 1:
                content += f"    C{i-1} --> D[{step.get('name', 'Complete')}]\n"
                content += "    D --> E[End]\n"
            else:
                content += f"    C{i-1} --> C{i}[{step.get('name', f'Step {i+1}')}]\n"
        
        content += "```\n\n## 📝 Detailed Steps\n\n"
        
        for i, step in enumerate(steps):
            content += f"""### Step {i+1}: {step.get('name', 'Unnamed Step')}

**Type:** {step.get('type', 'Manual')}  
**Trigger:** {step.get('trigger', 'Previous step completion')}  
**Action:** {step.get('action', 'Update record')}  
**Duration:** {step.get('duration', 'Instant')}

**Details:**
{step.get('description', 'No description provided')}

**Conditions:**
"""
            conditions = step.get('conditions', ['None'])
            for cond in conditions:
                content += f"- {cond}\n"
            
            content += "\n---\n\n"
        
        content += "## 🤖 Automation Rules\n\n"
        
        if automation_rules:
            for rule in automation_rules:
                content += f"- {rule}\n"
        else:
            content += """- When page status changes to "Complete", archive after 30 days
- Send notification when high-priority items are created
- Auto-assign tasks based on workload
- Generate weekly summary reports
- Sync with external calendar for deadlines
"""
        
        content += """

## ⚙️ Configuration

### Required Permissions
- Edit access to all affected databases
- Automation permissions enabled
- Integration access (if using external tools)

### Database Requirements
- Status property (Select type)
- Assignee property (Person type)
- Due Date property (Date type)
- Priority property (Select type)

### Integration Points
- Slack notifications
- Email alerts
- Calendar sync
- External API webhooks

## 📊 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Execution Time | < 5 seconds | 3.2 seconds |
| Success Rate | > 95% | 98.5% |
| Error Rate | < 5% | 1.5% |
| Daily Runs | Unlimited | ~500 |

## 🔧 Troubleshooting

### Common Issues

#### 1. Workflow Not Triggering
- Check trigger conditions
- Verify permissions
- Review automation limits

#### 2. Incomplete Execution
- Check step conditions
- Verify data requirements
- Review error logs

#### 3. Performance Issues
- Reduce complexity
- Batch operations
- Optimize formulas

## 📈 Optimization Tips

1. **Batch Processing:** Group similar operations
2. **Conditional Logic:** Use filters to reduce unnecessary steps
3. **Error Handling:** Add fallback options for failures
4. **Monitoring:** Set up alerts for failures
5. **Documentation:** Keep this doc updated

## 🚨 Error Handling

### Error Types
- **Data Validation:** Missing required fields
- **Permission Errors:** Insufficient access
- **Rate Limits:** Too many operations
- **Integration Failures:** External service issues

### Recovery Procedures
1. Log error details
2. Notify workflow owner
3. Attempt retry (max 3 times)
4. Fall back to manual process
5. Document in error log

## 📋 Maintenance Schedule

- **Daily:** Monitor execution logs
- **Weekly:** Review performance metrics
- **Monthly:** Optimize slow steps
- **Quarterly:** Full workflow audit

## 🗒️ Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| {datetime.now().strftime('%Y-%m-%d')} | 1.0 | Initial workflow | AI Assistant |

## 🔗 Related Resources

- [Notion Automation Guide](https://notion.so/help/automation)
- [Workflow Best Practices](internal-link)
- [Integration Documentation](internal-link)

---
*Workflow documented by Notion AI Assistant*"""
        
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