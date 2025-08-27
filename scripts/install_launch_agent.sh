#!/bin/bash
# Install Termina LaunchAgent with dynamic path resolution
# This script creates and installs the LaunchAgent plist with correct paths

set -e

echo "🚀 Installing Termina LaunchAgent..."

# Resolve paths dynamically
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.termina.plist"

# Detect uv binary location
UV_PATH=""
if command -v uv >/dev/null 2>&1; then
    UV_PATH="$(which uv)"
else
    # Try common locations
    for path in "/usr/local/bin/uv" "/opt/homebrew/bin/uv" "$HOME/.local/bin/uv"; do
        if [ -x "$path" ]; then
            UV_PATH="$path"
            break
        fi
    done
fi

if [ -z "$UV_PATH" ]; then
    echo "❌ Error: uv not found. Please install uv first."
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

echo "📝 Creating LaunchAgent plist at: $PLIST_FILE"
echo "   Project directory: $PROJECT_DIR"
echo "   UV path: $UV_PATH"

# Create the plist file with dynamic paths
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.termina</string>
    <key>ProgramArguments</key>
    <array>
        <string>$UV_PATH</string>
        <string>run</string>
        <string>python</string>
        <string>termina.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/termina.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/termina.out</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ LaunchAgent plist created successfully"

# Unload existing agent if running
if launchctl list | grep -q "com.termina"; then
    echo "⏹️  Unloading existing LaunchAgent..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# Load the new agent
echo "🔄 Loading LaunchAgent..."
launchctl load "$PLIST_FILE"

# Verify it's loaded
if launchctl list | grep -q "com.termina"; then
    echo "✅ Termina LaunchAgent installed and loaded successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   • Termina will now start automatically when you log in"
    echo "   • Check System Preferences → Security & Privacy for required permissions"
    echo "   • View logs: tail -f /tmp/termina.out /tmp/termina.err"
    echo ""
    echo "📝 Management commands:"
    echo "   • Stop:    launchctl unload $PLIST_FILE"
    echo "   • Start:   launchctl load $PLIST_FILE"
    echo "   • Status:  launchctl list | grep com.termina"
else
    echo "❌ Failed to load LaunchAgent. Check the logs:"
    echo "   tail -f /tmp/termina.err"
    exit 1
fi