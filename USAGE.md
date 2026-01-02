# Jissue Usage Guide

## ✅ Setup Complete!

Your Jissue MCP server is configured and ready to use with Claude Code.

## 🚀 Two Ways to Use Jissue

### Method 1: Using the `jissue` Command (Recommended)

The `jissue` CLI command launches Claude Code with your issue request pre-loaded:

```bash
cd jissue
source venv/bin/activate

# Create a bug with description
jissue --type bug "API endpoint /api/flaws returning 500 errors"

# Create a story
jissue -t story "User wants OAuth authentication in portal"

# Interactive mode (Claude asks for details)
jissue --type spike

# Use a different project
jissue -p MYPROJECT --type task "Update installation docs"
```

**What happens:**
1. `jissue` generates a prompt describing your issue
2. Launches Claude Code from the jissue directory (`.mcp.json` auto-detected)
3. Claude Code asks you to approve the Jissue MCP server (click **YES**)
4. Claude searches for duplicates, formats the issue, shows it to you
5. On approval, creates the issue in Jira

### Method 2: Direct Claude Code (Alternative)

Launch Claude Code and interact naturally:

```bash
cd jissue
claude
```

Then type your request:
```
You: Create a bug in PROJ: API endpoint returns 500 errors for CVE queries

Claude: Let me search for similar issues first...
[Uses search_jira_issues]
...
```

## 📝 Command Reference

```bash
jissue [OPTIONS] [DESCRIPTION]

Options:
  -t, --type TYPE       Issue type: story, bug, task, spike, epic
  -p, --project KEY     Project key (default: from config)
  --setup               Show setup instructions
  -h, --help            Show help

Examples:
  jissue
    Interactive mode

  jissue --type bug "Login fails with special characters"
    Create bug with description

  jissue -t story "User wants to export to PDF"
    Create story

  jissue -p MYPROJECT --type task "Update docs"
    Create in different project
```

## 🎯 Example Workflows

### Workflow 1: Quick Bug Creation

```bash
$ jissue --type bug "Login fails when using special characters in password"

🚀 Launching Claude Code with Jissue MCP server...

Initial prompt:
I need to create a Jira issue in project PROJ.
Issue type: bug
Details: Login fails when using special characters in password
Please:
1. Search for similar existing issues first to avoid duplicates
2. Use the appropriate template for this issue type
3. Show me the proposed summary and description
4. After I approve, create the issue in Jira

[Claude Code opens and starts working]

Claude: Let me search for existing issues about "login special characters password"...
I found 1 similar issue but it's about a different component. Here's the proposed bug:

**Summary:** Login fails when password contains special characters

**Description:**
## Description
Login functionality fails when users attempt to authenticate with passwords
containing special characters.

## Steps to Reproduce
1. Create account with special characters in password
2. Attempt to log in
3. Login fails

## Expected Behavior
Login should succeed regardless of password characters

## Actual Behavior
Login fails with special character passwords

Should I create this issue?

You: Yes

Claude: ✓ Created Jira issue: PROJ-4355
URL: https://your-domain.atlassian.net/browse/PROJ-4355
```

### Workflow 2: Interactive Story Creation

```bash
$ jissue -t story

[Claude Code launches]

Claude: I need to create a story in PROJ. What should this story be about?

You: Users want to export vulnerability data as PDF reports

Claude: Let me search for existing stories about exports or PDF...
I found stories about CSV export but nothing about PDF. Here's my proposal:

**Summary:** Export vulnerability data as PDF reports

**Description:**
**As a** security analyst
**I want** to export vulnerability data as PDF reports
**So that** I can share formatted reports with stakeholders

## Acceptance Criteria
- [ ] User can select vulnerabilities to include
- [ ] Report includes CVE details and severity
- [ ] PDF formatting is professional
- [ ] Export progress indicator shown

Would you like me to add or change anything?

You: Add that it should include the company logo

Claude: Updated! Here's the revised description:
[Shows updated version with logo requirement]

Should I create this issue?

You: Yes

Claude: ✓ Created: PROJ-4356
```

### Workflow 3: Using Direct Claude Code

```bash
$ cd jissue
$ claude

[Approve Jissue MCP server when prompted]

You: Search for issues about rate limiting

Claude: [Uses search_jira_issues]
Found 3 issues about rate limiting in PROJ:
- PROJ-1234: Implement API rate limiting
- PROJ-2345: Rate limit not working for authenticated users
- PROJ-3456: Increase rate limits for premium tier

Would you like details on any of these, or create a new related issue?

You: Create a new spike to research best practices

Claude: [Creates formatted spike using template]
Here's the proposed spike:

**Summary:** Research rate limiting best practices

**Description:**
## Research Question
What are the industry best practices for API rate limiting?

## Context
We have existing rate limiting but need to evaluate if we're following best practices.

## Goals
- Review current implementation
- Research industry standards
- Identify improvements

## Expected Outcomes
Technical document with recommendations

## Time Box
1 week

Should I create this?

You: Yes

Claude: ✓ Created: PROJ-4357
```

## 🛠️ Available MCP Tools

When Claude Code connects to Jissue, it gets these tools:

1. **get_issue_templates** - Get formatting templates for different issue types
2. **search_jira_issues** - Search for existing issues (duplicate detection!)
3. **get_jira_issue** - Get detailed information about a specific issue
4. **get_jira_projects** - List available Jira projects
5. **get_project_metadata** - Get available priorities and issue types for a project
6. **create_jira_issue** - Create a new Jira issue

Claude uses these automatically based on context.

## 🔧 Configuration

Your config: `~/.jissue/config.json`

```json
{
  "jira_url": "https://your-domain.atlassian.net",
  "token": "YOUR_TOKEN",
  "default_project": "PROJ"
}
```

Change `default_project` to use a different default project.

## 📚 Templates

Templates control how issues are formatted:

**Built-in templates** (`jissue/templates.py`):
- Story - User story format with acceptance criteria
- Bug - Bug report with steps to reproduce
- Task - Simple task checklist
- Spike - Research spike with time box
- Epic - High-level epic structure

**Custom templates** (`~/.jissue/templates/*.md`):

Create your own to override built-in ones:

```bash
cat > ~/.jissue/templates/story.md << 'EOF'
**As a** [user type]
**I want** [goal]
**So that** [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
[Team-specific requirements]
EOF
```

## 🐛 Troubleshooting

### "Command not found: jissue"

Activate the virtual environment:
```bash
cd jissue
source venv/bin/activate
```

### "MCP Server Not Detected"

The `jissue` command automatically handles this by launching from the jissue directory.

If using Claude Code directly:
1. Make sure you're in a directory with `.mcp.json`
2. Restart Claude Code
3. Copy `.mcp.json` to your project if needed

### "Connection to Jira failed"

Test the connection:
```bash
cd jissue
source venv/bin/activate
python3 -c "from jissue.jira_client import JiraClientWrapper; JiraClientWrapper(); print('✅ Connected')"
```

Common issues:
- Not on company VPN (if required for your Jira instance)
- Token expired
- Network connectivity issues

## 💡 Tips

1. **Use the CLI for speed** - `jissue --type bug "description"` is fastest
2. **Be descriptive** - More context = better formatted issues
3. **Let Claude search** - It will find duplicates automatically
4. **Review before creating** - Claude always shows proposals first
5. **Iterate freely** - Ask Claude to modify the issue before creating
6. **Use natural language** - No special syntax needed
7. **Try interactive mode** - `jissue --type story` for guided creation

## 🎉 Happy Issue Creating!

Jissue + Claude Code makes creating well-formatted, duplicate-free Jira issues easy and conversational.

Use `jissue --help` for command reference anytime!
