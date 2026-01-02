#!/usr/bin/env python3
"""Jissue CLI - Launch Claude Code with Jira MCP integration."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_config_path() -> Path:
    """Get the Jissue configuration directory path."""
    return Path.home() / ".jissue"


def ensure_config_exists():
    """Ensure configuration directory and files exist."""
    config_dir = get_config_path()
    config_dir.mkdir(exist_ok=True)

    # Create templates directory
    templates_dir = config_dir / "templates"
    templates_dir.mkdir(exist_ok=True)

    # Check if config.json exists
    config_file = config_dir / "config.json"
    if not config_file.exists():
        print(f"⚠️  Configuration file not found: {config_file}")
        print("\nPlease create ~/.jissue/config.json with the following structure:")
        print(json.dumps({
            "jira_url": "https://your-domain.atlassian.net",
            "email": "your-email@example.com",
            "api_token": "your-api-token",
            "default_project": "PROJ"
        }, indent=2))
        print("\nFor Jira Data Center, use:")
        print(json.dumps({
            "jira_url": "https://jira.your-company.com",
            "username": "your-username",
            "password": "your-password-or-token",
            "default_project": "PROJ"
        }, indent=2))
        sys.exit(1)


def build_initial_prompt(args) -> str:
    """Build the initial prompt for Claude Code."""
    # Load config to get default project
    import json
    config_path = Path.home() / ".jissue" / "config.json"
    default_project = "PROJ"  # fallback

    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            default_project = config.get("default_project", default_project)

    # Use project from args if specified, otherwise use default
    project = args.project if hasattr(args, 'project') and args.project else default_project

    parts = []

    parts.append(f"I need to create a Jira issue in project {project}.")

    if args.text:
        parts.append(f"\nHere's what I want to create:\n{args.text}")
    else:
        parts.append("\nPlease ask me what I want to create.")

    # Add instructions for Claude
    parts.append("\nPlease help me by:")
    parts.append("1. First, get the project metadata to see available priorities and issue types")
    parts.append("2. Analyze my description and determine the appropriate issue type (bug/story/task/spike/etc)")
    parts.append("3. Suggest an appropriate priority based on the severity/importance")
    parts.append("4. Search for similar existing issues to avoid duplicates:")
    parts.append("   - Extract key concepts and search terms from my description")
    parts.append("   - Search using different combinations of keywords")
    parts.append("   - Look for semantic similarity, not just exact phrase matches")
    parts.append("   - Tell me if you find potentially duplicate issues")
    parts.append("5. Use the appropriate template to format the issue")
    parts.append("6. Show me the proposed issue (summary, description, type, priority)")
    parts.append("7. After I approve, create the issue in Jira")

    return "\n".join(parts)


def launch_claude_code(initial_prompt: str):
    """Launch Claude Code with the initial prompt.

    The MCP server should be configured in Claude Code's settings.
    """
    # Check if claude is available
    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            check=True
        )
        claude_path = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("⚠️  Claude Code not found in PATH.")
        print("\nPlease install Claude Code first:")
        print("https://github.com/anthropics/claude-code")
        sys.exit(1)

    print("🚀 Launching Claude Code with Jissue MCP server...")
    print(f"\nInitial prompt:\n{initial_prompt}\n")
    print("-" * 60)
    print()

    # Change to jissue directory so MCP server is detected
    jissue_dir = Path(__file__).parent.parent
    original_dir = Path.cwd()

    try:
        # Launch Claude Code with the initial prompt as an argument
        # Pass the message directly to claude
        os.chdir(jissue_dir)
        subprocess.run(
            ["claude", initial_prompt],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    finally:
        os.chdir(original_dir)
        sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Jissue - AI-powered Jira issue creator. Just describe what you want and Claude will figure out the type, priority, and format it properly.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  jissue
    Interactive mode - Claude will ask what you want to create

  jissue "Login button not working on mobile Safari"
    Claude analyzes this and determines it's a bug, picks priority, formats it

  jissue "Users want to export vulnerability data to PDF reports"
    Claude determines this is a story, formats with acceptance criteria

  jissue "Research best practices for API rate limiting"
    Claude identifies this as a spike, uses spike template

  jissue -p MYPROJECT "Update installation documentation"
    Create an issue in a different project (MYPROJECT instead of default)

How it works:
  - You provide the description in your own words
  - Claude figures out if it's a bug, story, task, spike, etc.
  - Claude picks appropriate priority based on severity
  - Claude searches for duplicates
  - Claude formats it properly using templates
  - You approve, Claude creates it

Before using Jissue, make sure ~/.jissue/config.json is configured.
        """
    )

    parser.add_argument(
        "-p", "--project",
        dest="project",
        help="Jira project key (e.g., PROJ). Defaults to configured default_project"
    )

    parser.add_argument(
        "text",
        nargs="*",
        help="Description of what you want to create (in your own words, Claude will infer type and priority)"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Show setup instructions"
    )

    args = parser.parse_args()

    # Show setup instructions if requested
    if args.setup:
        show_setup_instructions()
        sys.exit(0)

    # Join text arguments if provided
    if args.text:
        args.text = " ".join(args.text)
    else:
        args.text = None

    # Ensure configuration exists
    ensure_config_exists()

    # Build initial prompt
    prompt = build_initial_prompt(args)

    # Launch Claude Code
    launch_claude_code(prompt)


def show_setup_instructions():
    """Show setup instructions for Jissue."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    JISSUE SETUP INSTRUCTIONS                     ║
╚══════════════════════════════════════════════════════════════════╝

Step 1: Create Jira Configuration
──────────────────────────────────
Create ~/.jissue/config.json with your Jira credentials:

For Jira Cloud:
{
  "jira_url": "https://your-domain.atlassian.net",
  "email": "your-email@example.com",
  "api_token": "your-api-token",
  "default_project": "PROJ"
}

For Jira Data Center:
{
  "jira_url": "https://jira.your-company.com",
  "username": "your-username",
  "password": "your-password-or-token",
  "default_project": "PROJ"
}

Step 2: Configure MCP Server in Claude Code
────────────────────────────────────────────
Add to your Claude Code MCP settings file:

{
  "mcpServers": {
    "jissue": {
      "command": "python",
      "args": ["-m", "jissue.server"]
    }
  }
}

Step 3: (Optional) Customize Templates
───────────────────────────────────────
Create custom templates in ~/.jissue/templates/

Example: ~/.jissue/templates/story.md
"""
)


if __name__ == "__main__":
    main()
