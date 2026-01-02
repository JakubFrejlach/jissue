# Jissue

AI-powered Jira issue creator with Claude Code integration via MCP (Model Context Protocol).

## Overview

Jissue combines the power of Claude AI with your Jira workflow. Simply describe what you want to create in natural language, and Claude will:

1. **Search for duplicates** - Automatically check if similar issues already exist
2. **Format properly** - Use templates for different issue types (Story, Bug, Spike, etc.)
3. **Interactive refinement** - Iterate on the summary and description until it's perfect
4. **Create in Jira** - With one command, create the issue in your Jira project

## Features

- ✅ **Duplicate Detection** - Search existing issues before creating new ones
- ✅ **Smart Templates** - Built-in templates for Story, Bug, Task, Spike, and Epic
- ✅ **Custom Templates** - Override defaults with your own templates
- ✅ **Interactive Workflow** - Review and refine before creating
- ✅ **Jira Cloud & Data Center** - Works with both deployment types
- ✅ **MCP Integration** - Seamless Claude Code integration

## Installation

```bash
# Clone the repository
git clone https://github.com/JakubFrejlach/jissue
cd jissue

# Install the package
pip install -e .
```

## Setup

### Quick Setup (Recommended)

Use the interactive setup wizard:
```bash
./setup.sh
```

The wizard will:
- Prompt for your Jira URL and credentials
- Detect Jira Cloud vs Data Center
- Optionally configure proxy settings
- Test the connection
- Show MCP configuration instructions

### Manual Setup

Alternatively, create `~/.jissue/config.json` manually:

**For Jira Cloud:**
```json
{
  "jira_url": "https://your-domain.atlassian.net",
  "email": "your-email@example.com",
  "api_token": "your-api-token",
  "default_project": "PROJ"
}
```

To get your API token for Jira Cloud:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to your config

**For Jira Data Center:**
```json
{
  "jira_url": "https://jira.your-company.com",
  "username": "your-username",
  "password": "your-password-or-personal-access-token",
  "default_project": "PROJ"
}
```

**Optional: Proxy Configuration**

If you're behind a corporate proxy, add the `proxy` field:
```json
{
  "jira_url": "https://jira.your-company.com",
  "username": "your-username",
  "password": "your-password",
  "default_project": "PROJ",
  "proxy": "http://proxy.company.com:8080"
}
```

### 2. MCP Server Configuration (Automatic)

The Jissue MCP server is automatically detected when you run `jissue` from the jissue directory.

The `.mcp.json` file in the project root tells Claude Code about the Jissue MCP server.

**To use Jissue from other directories**, copy `.mcp.json` to your project:
```bash
cp /path/to/jissue/.mcp.json /path/to/your/project/
```

Or create a global `~/.mcp.json` (check if your Claude Code version supports it)

### 3. (Optional) Custom Templates

Create custom templates in `~/.jissue/templates/`:

```bash
# Example: Custom story template
cat > ~/.jissue/templates/story.md << 'EOF'
**As a** [user type]
**I want** [goal]
**So that** [benefit]

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Technical Notes
[Technical details]
EOF
```

## Usage

### Basic Usage

```bash
# Launch interactive mode (uses default project from config)
jissue

# Create a bug with initial description
jissue --type bug "Login button not working on mobile"

# Create a story
jissue -t story "As a user I want to export data to CSV"

# Create a spike
jissue --type spike "Research API rate limiting best practices"

# Create an issue in a specific project
jissue -p MYPROJECT --type task "Update documentation"
```

The `jissue` command:
1. Launches Claude Code from the jissue directory (so MCP server is detected)
2. Passes your initial prompt to Claude
3. Claude searches for duplicates, formats the issue, and creates it in Jira

### Example Workflow

```bash
$ jissue --type story "user authentication with OAuth"
🚀 Launching Claude Code with Jissue MCP server...

Claude:
I'll help you create a story for user authentication with OAuth. Let me first
search for any existing issues about authentication...

[Claude searches existing issues]

I found 2 related issues:
- PROJ-123: Implement login system
- PROJ-456: Add social login

Would you like to proceed with creating a new issue for OAuth specifically?

You: Yes

Claude:
Here's the proposed story:

**Summary:** Implement OAuth 2.0 authentication for user login

**Description:**
**As a** user
**I want** to log in using OAuth providers (Google, GitHub)
**So that** I don't need to create another password

## Acceptance Criteria
- [ ] Users can sign up/login with Google OAuth
- [ ] Users can sign up/login with GitHub OAuth
- [ ] Existing accounts can be linked to OAuth providers
- [ ] Security tokens are properly managed

Would you like me to create this issue?

You: Yes, create it

Claude:
✓ Created Jira issue: PROJ-789

URL: https://your-domain.atlassian.net/browse/PROJ-789
```

## How It Works

### Architecture

```
┌─────────┐         ┌──────────────┐         ┌──────────┐
│  CLI    │────────>│ Claude Code  │────────>│   Jira   │
│ (jissue)│         │  + MCP       │         │   API    │
└─────────┘         └──────────────┘         └──────────┘
                           │
                           │
                    ┌──────▼──────┐
                    │   Jissue    │
                    │ MCP Server  │
                    └─────────────┘
```

1. **CLI** launches Claude Code with your requirements
2. **Claude Code** uses MCP tools provided by Jissue server
3. **MCP Server** communicates with Jira API
4. **Templates** guide the formatting of issues

### Available MCP Tools

The Jissue MCP server provides these tools to Claude:

- `get_issue_templates` - Get formatting templates for issue types
- `search_jira_issues` - Search for existing issues (duplicate detection)
- `get_jira_issue` - Get details of a specific issue
- `get_jira_projects` - List available Jira projects
- `get_project_metadata` - Get available priorities and issue types for a project
- `create_jira_issue` - Create a new Jira issue

## Custom Templates

Templates are stored in:
1. Built-in templates (in `jissue/templates.py`)
2. Custom templates in `~/.jissue/templates/*.md`

Custom templates override built-in ones. Available template names:
- `story.md`
- `bug.md`
- `task.md`
- `spike.md`
- `epic.md`

Or create your own issue types!

## Troubleshooting

### "Configuration file not found"
Create `~/.jissue/config.json` with your Jira credentials (see Setup section).

### "Claude Code not found"
The claude command should be available in your PATH

### "Failed to connect to Jira"
- Check your `jira_url` is correct
- Verify your credentials (email + API token for Cloud, username + password for Data Center)
- Test credentials manually: `curl -u email:api_token https://your-domain.atlassian.net/rest/api/2/myself`

### MCP Server not working
- Ensure the server is configured in Claude Code MCP settings
- Test the server: `python -m jissue.server`
- Check Claude Code logs for MCP connection errors

## Development

```bash
# Install in development mode
pip install -e .

# Run the MCP server directly
python -m jissue.server

# Run tests (TODO)
pytest
```

## Future Improvements

Potential enhancements for future versions:
- Support for other MCP clients (not just Claude Code)
- More issue types and custom fields
- Issue updates/editing via MCP
- Tests and better error messages
- Release to PyPI for easier installation (`pip install jissue`)

This is a personal project shared with others. Contributions welcome but no guarantees on maintenance or support.

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
