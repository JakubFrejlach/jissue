# Jissue Quick Start Guide

## 1️⃣ Quick Setup

### Install Jissue

```bash
# Clone and install
git clone <your-repo-url>
cd jissue
pip install -e .
```

### Configure Jira Credentials

**Option A: Interactive Setup (Easiest)**

Run the setup wizard:
```bash
./setup.sh
```

It will guide you through configuration and test your connection.

**Option B: Manual Setup**

Create `~/.jissue/config.json`:

**For Jira Cloud:**
```json
{
  "jira_url": "https://your-domain.atlassian.net",
  "email": "your-email@example.com",
  "api_token": "your-api-token",
  "default_project": "PROJ"
}
```

Get your API token: https://id.atlassian.com/manage-profile/security/api-tokens

**For Jira Data Center:**
```json
{
  "jira_url": "https://jira.your-company.com",
  "username": "your-username",
  "password": "your-password-or-pat",
  "default_project": "PROJ"
}
```

**Optional:** If behind a proxy, add `"proxy": "http://proxy.company.com:8080"`

> **Note:** The MCP server is automatically detected when you run `jissue` from this directory.

## ✅ Setup Complete!

You're ready to create Jira issues with Claude.

## 🚀 The Simplest Way to Create Jira Issues

Just describe what you want in your own words. Claude will figure out everything else.

```bash
# Activate the virtual environment (if using one)
cd jissue
source venv/bin/activate

# Just describe what you want - Claude figures out it's a bug, picks priority, formats it
jissue "Login button not working on mobile Safari when password has special characters"

# Claude determines this is a story and formats it properly
jissue "Users want to export vulnerability data to PDF reports with company logo"

# Claude identifies this as a spike research task
jissue "Research best practices for API rate limiting in microservices"

# Interactive mode - Claude will ask you what you want
jissue

# Use a different project
jissue -p MYPROJECT "Installation docs are outdated for version 9.2"
```

## 💡 How It Works

**You provide the raw description**, Claude does the thinking:

1. **Gets project metadata** - Checks what priorities and issue types are valid in your project
2. **Analyzes your description** - Determines if it's a bug, story, task, spike, etc.
3. **Picks priority** - Based on severity/importance words in your description
4. **Searches for duplicates** - Checks if similar issues already exist
5. **Formats with templates** - Uses proper format (bug report, user story, etc.)
6. **Shows you the proposal** - Summary, description, type, priority
7. **Creates on approval** - You just say yes and it's created

## 📝 Examples

### Bug Report
```bash
$ jissue "API endpoint /api/flaws returns 500 errors when querying CVE-2024-1234"

🚀 Launching Claude Code with Jissue MCP server...

[Claude Code opens]

Claude: Let me analyze this and create an appropriate issue.

[Uses get_project_metadata to see project priorities]
[Determines this is a bug - server errors are bugs]
[Picks "High" priority - API errors are serious]
[Searches for similar issues about API 500 errors]

Found 2 similar issues but they're for different endpoints.

Here's the proposed bug:

**Type:** Bug
**Priority:** High
**Summary:** API endpoint /api/flaws returns 500 errors for specific CVE queries

**Description:**
## Description
The /api/flaws endpoint is returning HTTP 500 internal server errors
when querying for CVE-2024-1234.

## Steps to Reproduce
1. Query /api/flaws endpoint with CVE-2024-1234
2. Observe 500 error response

## Expected Behavior
API should return flaw data or 404 if not found

## Actual Behavior
Returns 500 internal server error

Should I create this issue?

You: Yes

Claude: ✓ Created: PROJ-4358
URL: https://your-domain.atlassian.net/browse/PROJ-4358
```

### Story
```bash
$ jissue "Security analysts need to filter vulnerabilities by CVSS score and export filtered results as PDF"

[Claude Code opens]

Claude: This looks like a user story. Let me format it properly.

[Analyzes: mentions "users need" = story, not critical = Medium priority]
[Searches for similar stories about filtering or PDF export]

Here's the proposed story:

**Type:** Story
**Priority:** Should Have
**Summary:** Filter vulnerabilities by CVSS score and export to PDF

**Description:**
**As a** security analyst
**I want** to filter vulnerabilities by CVSS score and export results as PDF
**So that** I can share customized vulnerability reports with stakeholders

## Acceptance Criteria
- [ ] User can filter by CVSS score range
- [ ] Filtered results can be exported as PDF
- [ ] PDF includes company branding
- [ ] Export shows applied filters in report

Should I create this?

You: Yes

Claude: ✓ Created: PROJ-4359
```

### Research Spike
```bash
$ jissue "Need to research how other security databases handle rate limiting for public APIs"

[Claude Code opens]

Claude: This is a research spike. Let me set it up properly.

[Identifies keywords "research", "how other" = spike]
[Picks "Normal" priority for research]

Here's the proposed spike:

**Type:** Spike
**Priority:** Normal
**Summary:** Research rate limiting approaches for security database APIs

**Description:**
## Research Question
How do other security databases implement rate limiting for public APIs?

## Context
We need to improve our API rate limiting strategy.

## Goals
- Review rate limiting in NVD, CVE.org, and other security databases
- Document best practices
- Identify improvements for our API

## Expected Outcomes
Technical document with recommendations and implementation options

## Time Box
1 week

Should I create this?

You: Yes

Claude: ✓ Created: PROJ-4360
```

## 🎯 What You CAN Do

✅ **Dump your thoughts** - No need to structure or categorize
✅ **Use natural language** - Write like you're talking to a colleague
✅ **Be vague** - Claude will ask clarifying questions if needed
✅ **Skip the details** - Claude will infer type, priority, format

## 🚫 What You DON'T Need

❌ Specify `--type bug` or `--type story` - Claude figures it out
❌ Pick a priority manually - Claude chooses based on severity
❌ Format with templates - Claude uses the right template
❌ Search for duplicates yourself - Claude does it automatically

## 🔧 Advanced Options

### Different Project
```bash
jissue -p MYPROJECT "Memory leak in systemd service after upgrade"
```

### Interactive Mode
```bash
jissue
# Claude: "What would you like to create?"
# You: [describe iteratively]
```

## 💡 Tips for Best Results

1. **Include severity indicators** for priority detection:
   - "critical", "urgent", "blocker" → High priority
   - "nice to have", "would be good" → Lower priority

2. **Use action words** to help type detection:
   - "broken", "fails", "error" → Bug
   - "users want", "need to be able" → Story
   - "research", "investigate" → Spike
   - "update", "refactor" → Task

3. **Add context** for better formatting:
   - "when using X..." gives better reproduction steps
   - "so that users can..." gives better user story benefit

## 🐛 Troubleshooting

### "Command not found: jissue"
```bash
# Make sure you're in the jissue directory and venv is activated
cd jissue
source venv/bin/activate
```

### Test the new approach
```bash
jissue "This is a test issue to verify everything works - please ignore"
```

## 🎉 That's It!

No more thinking about issue types, priorities, or formats.

Just tell Claude what you want and it handles the rest.

```bash
jissue "your thoughts here"
```
