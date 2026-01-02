#!/bin/bash
# Jissue setup helper script

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                      JISSUE SETUP WIZARD                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

CONFIG_DIR="$HOME/.jissue"
CONFIG_FILE="$CONFIG_DIR/config.json"
TEMPLATES_DIR="$CONFIG_DIR/templates"

# Create configuration directory
echo "📁 Creating configuration directory: $CONFIG_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$TEMPLATES_DIR"

# Check if config already exists
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Configuration file already exists: $CONFIG_FILE"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Ask for Jira type
echo ""
echo "Which Jira deployment are you using?"
echo "1) Jira Cloud (*.atlassian.net)"
echo "2) Jira Data Center (self-hosted)"
read -p "Enter choice (1 or 2): " jira_type

echo ""
echo "Enter your Jira configuration:"

# Get common fields
read -p "Jira URL (e.g., https://your-domain.atlassian.net): " jira_url
read -p "Default project key (e.g., PROJ): " default_project

# Ask about proxy
echo ""
read -p "Are you behind a corporate proxy? (y/N): " -n 1 -r
echo
use_proxy=false
if [[ $REPLY =~ ^[Yy]$ ]]; then
    use_proxy=true
    read -p "Proxy URL (e.g., http://proxy.company.com:8080): " proxy_url
fi

# Create config based on type
if [ "$jira_type" == "1" ]; then
    read -p "Email: " email
    read -p "API Token: " api_token

    if [ "$use_proxy" = true ]; then
        cat > "$CONFIG_FILE" << EOF
{
  "jira_url": "$jira_url",
  "email": "$email",
  "api_token": "$api_token",
  "default_project": "$default_project",
  "proxy": "$proxy_url"
}
EOF
    else
        cat > "$CONFIG_FILE" << EOF
{
  "jira_url": "$jira_url",
  "email": "$email",
  "api_token": "$api_token",
  "default_project": "$default_project"
}
EOF
    fi
else
    read -p "Username: " username
    read -p "Password/Token: " password

    if [ "$use_proxy" = true ]; then
        cat > "$CONFIG_FILE" << EOF
{
  "jira_url": "$jira_url",
  "username": "$username",
  "password": "$password",
  "default_project": "$default_project",
  "proxy": "$proxy_url"
}
EOF
    else
        cat > "$CONFIG_FILE" << EOF
{
  "jira_url": "$jira_url",
  "username": "$username",
  "password": "$password",
  "default_project": "$default_project"
}
EOF
    fi
fi

echo ""
echo "✅ Configuration saved to: $CONFIG_FILE"
echo ""

# Test connection
echo "🔌 Testing Jira connection..."
if python3 -c "
from jissue.jira_client import JiraClientWrapper
try:
    client = JiraClientWrapper()
    projects = client.get_projects()
    print(f'✅ Successfully connected! Found {len(projects)} projects.')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo ""
else
    echo "⚠️  Connection test failed. Please check your credentials."
    echo ""
fi

# MCP Configuration
echo "📝 Claude Code MCP Configuration"
echo "────────────────────────────────────────────────────────────────"
echo "Add this to your Claude Code MCP settings:"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "jissue": {
      "command": "python",
      "args": ["-m", "jissue.server"]
    }
  }
}
EOF
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Claude Code MCP settings (see above)"
echo "2. Run: jissue --setup (to see full setup instructions)"
echo "3. Run: jissue (to start creating issues!)"
echo ""
