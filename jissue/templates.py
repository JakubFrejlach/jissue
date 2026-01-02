"""Template manager for Jira issue types."""

import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages issue type templates."""

    def __init__(self, custom_template_dir: Path | None = None):
        """Initialize template manager.

        Args:
            custom_template_dir: Optional custom template directory.
                               Defaults to ~/.jissue/templates/
        """
        # Default templates (built-in)
        self.default_templates = self._get_default_templates()

        # Custom template directory
        if custom_template_dir:
            self.custom_dir = custom_template_dir
        else:
            self.custom_dir = Path.home() / ".jissue" / "templates"

        # Load custom templates if directory exists
        self.custom_templates = {}
        if self.custom_dir.exists():
            self.custom_templates = self._load_custom_templates()

    def _get_default_templates(self) -> Dict[str, str]:
        """Get default built-in templates."""
        return {
            "story": """**As a** [user type]
**I want** [goal]
**So that** [benefit]

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

## Additional Notes
[Any additional context or notes]
""",
            "bug": """## Description
[Clear description of the bug]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- Browser/Device:
- Version:
- OS:

## Additional Context
[Screenshots, logs, or other relevant information]
""",
            "task": """## Objective
[What needs to be done]

## Details
[Detailed description of the task]

## Checklist
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

## Dependencies
[Any dependencies or blockers]
""",
            "spike": """## Research Question
[What do we need to investigate?]

## Context
[Why is this research needed?]

## Goals
- Goal 1
- Goal 2

## Expected Outcomes
[What deliverables/findings are expected?]

## Time Box
[Time limit for this spike]
""",
            "epic": """## Vision
[High-level description of what this epic aims to achieve]

## Goals
- Goal 1
- Goal 2

## User Stories
[List of user stories that will be part of this epic]

## Success Metrics
[How will we measure success?]

## Timeline
[Expected timeline or milestones]
"""
        }

    def _load_custom_templates(self) -> Dict[str, str]:
        """Load custom templates from the templates directory."""
        templates = {}

        try:
            for template_file in self.custom_dir.glob("*.md"):
                issue_type = template_file.stem
                with open(template_file, 'r') as f:
                    templates[issue_type] = f.read()
                logger.info(f"Loaded custom template: {issue_type}")
        except Exception as e:
            logger.error(f"Error loading custom templates: {e}")

        return templates

    def get_template(self, issue_type: str) -> str | None:
        """Get template for a specific issue type.

        Custom templates override default templates.

        Args:
            issue_type: Issue type (e.g., 'story', 'bug', 'task')

        Returns:
            Template string or None if not found
        """
        issue_type = issue_type.lower()

        # Check custom templates first
        if issue_type in self.custom_templates:
            return self.custom_templates[issue_type]

        # Fall back to default templates
        return self.default_templates.get(issue_type)

    def get_all_templates(self) -> Dict[str, str]:
        """Get all available templates (custom overrides default)."""
        all_templates = self.default_templates.copy()
        all_templates.update(self.custom_templates)
        return all_templates

    def list_templates(self) -> list[str]:
        """List all available template names."""
        return list(self.get_all_templates().keys())
