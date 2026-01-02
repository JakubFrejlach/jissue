"""Jira client wrapper for creating and managing issues."""

import logging
import os
from pathlib import Path
from typing import Any

from jira import JIRA

logger = logging.getLogger(__name__)


class JiraClientWrapper:
    """Wrapper for Jira API client."""

    def __init__(self):
        """Initialize Jira client with credentials from config."""
        self.config = self._load_config()
        self.jira = self._connect()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from ~/.jissue/config.json."""
        import json

        config_path = Path.home() / ".jissue" / "config.json"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n\n"
                "Please create ~/.jissue/config.json with the following structure:\n"
                "{\n"
                '  "jira_url": "https://your-domain.atlassian.net",\n'
                '  "email": "your-email@example.com",\n'
                '  "api_token": "your-api-token",\n'
                '  "default_project": "PROJ"\n'
                "}"
            )

        with open(config_path) as f:
            return json.load(f)

    def _connect(self) -> JIRA:
        """Connect to Jira."""
        try:
            # Configure options
            options = {
                "server": self.config["jira_url"],
                "check_update": False,
            }

            # Configure proxy if provided
            proxies = None
            if "proxy" in self.config:
                proxies = {
                    "http": self.config["proxy"],
                    "https": self.config["proxy"]
                }
                logger.info(f"Using proxy: {self.config['proxy']}")

            # Determine authentication method
            # Priority: token_auth > basic_auth (email+api_token) > basic_auth (username+password)
            if "token" in self.config:
                # Token authentication (Jira Data Center token auth)
                jira = JIRA(
                    options=options,
                    token_auth=self.config["token"],
                    get_server_info=False,
                    proxies=proxies
                )
                logger.info("Using token authentication")
            elif "email" in self.config and "api_token" in self.config:
                # Cloud authentication
                jira = JIRA(
                    options=options,
                    basic_auth=(self.config["email"], self.config["api_token"]),
                    proxies=proxies
                )
                logger.info("Using email + API token authentication (Jira Cloud)")
            elif "username" in self.config and "password" in self.config:
                # Data Center basic auth
                jira = JIRA(
                    options=options,
                    basic_auth=(self.config["username"], self.config["password"]),
                    proxies=proxies
                )
                logger.info("Using username + password authentication (Jira Data Center)")
            else:
                raise ValueError(
                    "Invalid config: must have either 'token' for token auth, "
                    "(email, api_token) for Cloud, or (username, password) for Data Center"
                )

            logger.info(f"Connected to Jira: {self.config['jira_url']}")
            return jira
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            raise

    def create_issue(
        self,
        project: str,
        issue_type: str,
        summary: str,
        description: str,
        priority: str | None = None,
        assignee: str | None = None
    ) -> str:
        """Create a Jira issue and return the issue key."""
        # Map common issue type names to Jira names
        issue_type_map = {
            "story": "Story",
            "bug": "Bug",
            "task": "Task",
            "spike": "Spike",
            "epic": "Epic",
            "subtask": "Sub-task"
        }

        jira_issue_type = issue_type_map.get(issue_type.lower(), issue_type.capitalize())

        issue_dict = {
            "project": {"key": project},
            "summary": summary,
            "description": description,
            "issuetype": {"name": jira_issue_type},
        }

        if priority:
            issue_dict["priority"] = {"name": priority}

        if assignee:
            issue_dict["assignee"] = {"name": assignee}

        try:
            issue = self.jira.create_issue(fields=issue_dict)
            logger.info(f"Created issue: {issue.key}")
            return issue.key
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            raise Exception(f"Failed to create Jira issue: {str(e)}")

    def get_issue_url(self, issue_key: str) -> str:
        """Get the URL for a Jira issue."""
        return f"{self.config['jira_url']}/browse/{issue_key}"

    def get_projects(self) -> list[dict[str, str]]:
        """Get list of available projects."""
        try:
            projects = self.jira.projects()
            return [
                {"key": p.key, "name": p.name}
                for p in projects
            ]
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            raise Exception(f"Failed to get Jira projects: {str(e)}")

    def search_issues(
        self,
        query: str,
        project: str | None = None,
        max_results: int = 10
    ) -> list[dict[str, Any]]:
        """Search for issues matching the query.

        Args:
            query: Text to search in summary and description
            project: Optional project key to limit search
            max_results: Maximum number of results to return

        Returns:
            List of issue dictionaries with key, summary, type, status, etc.
        """
        try:
            # Build JQL query
            jql_parts = []

            # Add text search only if query is not empty
            if query and query.strip():
                jql_parts.append(f'(summary ~ "{query}" OR description ~ "{query}")')

            # Add project filter if specified
            if project:
                jql_parts.append(f'project = {project}')

            # If no query parts, search for all issues (order by updated)
            if not jql_parts:
                jql = "ORDER BY updated DESC"
            else:
                jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"

            # Search with fields we need
            issues = self.jira.search_issues(
                jql,
                maxResults=max_results,
                fields='summary,issuetype,status,priority,description,assignee'
            )

            # Convert to simple dict format
            result = []
            for issue in issues:
                result.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'type': issue.fields.issuetype.name,
                    'status': issue.fields.status.name,
                    'priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else None,
                    'description': issue.fields.description or '',
                    'assignee': issue.fields.assignee.displayName if hasattr(issue.fields, 'assignee') and issue.fields.assignee else None,
                    'url': self.get_issue_url(issue.key)
                })

            return result

        except Exception as e:
            logger.error(f"Failed to search issues: {e}")
            raise Exception(f"Failed to search Jira issues: {str(e)}")

    def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Get detailed information about a specific issue.

        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')

        Returns:
            Issue dictionary with detailed information
        """
        try:
            issue = self.jira.issue(issue_key)

            return {
                'key': issue.key,
                'summary': issue.fields.summary,
                'type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else None,
                'description': issue.fields.description or '',
                'assignee': issue.fields.assignee.displayName if hasattr(issue.fields, 'assignee') and issue.fields.assignee else None,
                'url': self.get_issue_url(issue.key)
            }

        except Exception as e:
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise Exception(f"Failed to get Jira issue {issue_key}: {str(e)}")

    def get_project_metadata(self, project_key: str) -> dict[str, Any]:
        """Get metadata about a project including available priorities and issue types.

        Args:
            project_key: Jira project key (e.g., 'PROJ')

        Returns:
            Dictionary with priorities and issue types available for the project
        """
        try:
            # Get project to validate it exists
            project = self.jira.project(project_key)

            # Get all priorities (global in Jira)
            priorities = self.jira.priorities()
            priority_list = [p.name for p in priorities]

            # Get issue types for this project
            issue_types = self.jira.issue_types()
            issue_type_list = [it.name for it in issue_types]

            return {
                'project': {
                    'key': project.key,
                    'name': project.name
                },
                'priorities': priority_list,
                'issue_types': issue_type_list
            }

        except Exception as e:
            logger.error(f"Failed to get project metadata for {project_key}: {e}")
            raise Exception(f"Failed to get project metadata: {str(e)}")
