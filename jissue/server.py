#!/usr/bin/env python3
"""Jissue MCP Server - Provides Jira issue creation tools to Claude Code."""

import json
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

from jissue.jira_client import JiraClientWrapper
from jissue.templates import TemplateManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jissue-server")


class IssueInput(BaseModel):
    """Input for creating a Jira issue."""
    project: str = Field(description="Jira project key (e.g., 'PROJ')")
    issue_type: str = Field(description="Issue type: story, bug, spike, task, etc.")
    summary: str = Field(description="Issue summary/title")
    description: str = Field(description="Issue description in Jira markdown format")
    priority: str | None = Field(default=None, description="Priority name (use get_project_metadata to see valid priorities)")
    assignee: str | None = Field(default=None, description="Assignee username")


class JissueServer:
    """MCP Server for Jissue - AI-powered Jira issue creation."""

    def __init__(self):
        self.server = Server("jissue")
        self.template_manager = TemplateManager()
        self.jira_client: JiraClientWrapper | None = None

        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="get_issue_templates",
                description="Get available Jira issue type templates (story, bug, spike, task, etc.) with formatting guidelines",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_type": {
                            "type": "string",
                            "description": "Optional: specific issue type to get template for"
                        }
                    }
                }
            ),
            Tool(
                name="create_jira_issue",
                description="Create a new Jira issue with the provided details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Jira project key (e.g., 'PROJ')"
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Issue type: story, bug, spike, task, etc."
                        },
                        "summary": {
                            "type": "string",
                            "description": "Issue summary/title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Issue description in Jira markdown format"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority name (use get_project_metadata to get valid priorities for the project)"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Assignee username (optional)"
                        }
                    },
                    "required": ["project", "issue_type", "summary", "description"]
                }
            ),
            Tool(
                name="get_jira_projects",
                description="Get list of available Jira projects",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="search_jira_issues",
                description="Search for existing Jira issues using text search. Useful for finding similar/duplicate issues before creating new ones. TIP: For better duplicate detection, try multiple searches with different keyword combinations extracted from the user's description (e.g., core concepts, synonyms, related terms) rather than searching the full phrase once.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text to search in summary and description. Use key concepts/keywords rather than full phrases for better results."
                        },
                        "project": {
                            "type": "string",
                            "description": "Optional: limit search to specific project key"
                        },
                        "max_results": {
                            "type": "number",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_jira_issue",
                description="Get detailed information about a specific Jira issue by its key (e.g., PROJ-123)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "Jira issue key (e.g., 'PROJ-123')"
                        }
                    },
                    "required": ["issue_key"]
                }
            ),
            Tool(
                name="get_project_metadata",
                description="Get project metadata including available priorities and issue types. Use this before creating issues to know what priorities and types are valid.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_key": {
                            "type": "string",
                            "description": "Jira project key (e.g., 'PROJ')"
                        }
                    },
                    "required": ["project_key"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        # Map tool names to handler methods
        handlers = {
            "get_issue_templates": self._get_issue_templates,
            "create_jira_issue": self._create_jira_issue,
            "get_jira_projects": self._get_jira_projects,
            "search_jira_issues": self._search_jira_issues,
            "get_jira_issue": self._get_jira_issue,
            "get_project_metadata": self._get_project_metadata,
        }

        try:
            handler = handlers.get(name)
            if not handler:
                raise ValueError(f"Unknown tool: {name}")

            return await handler(arguments)
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _get_issue_templates(self, args: dict[str, Any]) -> list[TextContent]:
        """Get issue templates."""
        issue_type = args.get("issue_type")

        if issue_type:
            template = self.template_manager.get_template(issue_type)
            if template:
                result = f"# {issue_type.upper()} Template\n\n{template}"
            else:
                result = f"No template found for issue type: {issue_type}\n\nAvailable types: {', '.join(self.template_manager.list_templates())}"
        else:
            templates = self.template_manager.get_all_templates()
            result = "# Available Issue Templates\n\n"
            for itype, template in templates.items():
                result += f"## {itype.upper()}\n\n{template}\n\n---\n\n"

        return [TextContent(type="text", text=result)]

    async def _create_jira_issue(self, args: dict[str, Any]) -> list[TextContent]:
        """Create a Jira issue."""
        # Validate input
        issue_input = IssueInput(**args)

        # Initialize Jira client if not already done
        if self.jira_client is None:
            self.jira_client = JiraClientWrapper()

        # Create the issue
        issue_key = self.jira_client.create_issue(
            project=issue_input.project,
            issue_type=issue_input.issue_type,
            summary=issue_input.summary,
            description=issue_input.description,
            priority=issue_input.priority,
            assignee=issue_input.assignee
        )

        issue_url = self.jira_client.get_issue_url(issue_key)

        result = f"✓ Created Jira issue: {issue_key}\n\nURL: {issue_url}\n\nSummary: {issue_input.summary}"
        return [TextContent(type="text", text=result)]

    async def _get_jira_projects(self, args: dict[str, Any] | None = None) -> list[TextContent]:
        """Get list of Jira projects."""
        if self.jira_client is None:
            self.jira_client = JiraClientWrapper()

        projects = self.jira_client.get_projects()

        result = "# Available Jira Projects\n\n"
        for project in projects:
            result += f"- **{project['key']}**: {project['name']}\n"

        return [TextContent(type="text", text=result)]

    async def _search_jira_issues(self, args: dict[str, Any]) -> list[TextContent]:
        """Search for Jira issues."""
        if self.jira_client is None:
            self.jira_client = JiraClientWrapper()

        query = args["query"]
        project = args.get("project")
        max_results = args.get("max_results", 10)

        issues = self.jira_client.search_issues(
            query=query,
            project=project,
            max_results=int(max_results)
        )

        if not issues:
            result = f"No issues found matching: {query}"
        else:
            result = f"# Found {len(issues)} issue(s)\n\n"
            for issue in issues:
                result += f"## {issue['key']}: {issue['summary']}\n"
                result += f"**Type:** {issue['type']} | **Status:** {issue['status']} | **Priority:** {issue.get('priority', 'N/A')}\n"
                result += f"**URL:** {issue['url']}\n"
                if issue.get('description'):
                    # Truncate long descriptions
                    desc = issue['description'][:200]
                    if len(issue['description']) > 200:
                        desc += "..."
                    result += f"**Description:** {desc}\n"
                result += "\n---\n\n"

        return [TextContent(type="text", text=result)]

    async def _get_jira_issue(self, args: dict[str, Any]) -> list[TextContent]:
        """Get detailed information about a specific Jira issue."""
        if self.jira_client is None:
            self.jira_client = JiraClientWrapper()

        issue_key = args["issue_key"]
        issue = self.jira_client.get_issue(issue_key)

        result = f"# {issue['key']}: {issue['summary']}\n\n"
        result += f"**Type:** {issue['type']}\n"
        result += f"**Status:** {issue['status']}\n"
        result += f"**Priority:** {issue.get('priority', 'N/A')}\n"
        result += f"**Assignee:** {issue.get('assignee', 'Unassigned')}\n"
        result += f"**URL:** {issue['url']}\n\n"
        result += f"## Description\n\n{issue.get('description', 'No description')}\n"

        return [TextContent(type="text", text=result)]

    async def _get_project_metadata(self, args: dict[str, Any]) -> list[TextContent]:
        """Get project metadata including priorities and issue types."""
        if self.jira_client is None:
            self.jira_client = JiraClientWrapper()

        project_key = args["project_key"]
        metadata = self.jira_client.get_project_metadata(project_key)

        result = f"# {metadata['project']['key']} - {metadata['project']['name']}\n\n"

        result += "## Available Priorities\n"
        for priority in metadata['priorities']:
            result += f"- {priority}\n"

        result += "\n## Available Issue Types\n"
        for issue_type in metadata['issue_types']:
            result += f"- {issue_type}\n"

        return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server."""
    logger.info("Starting Jissue MCP Server...")
    server = JissueServer()

    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
