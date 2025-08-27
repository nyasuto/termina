#!/bin/bash
# Create macOS app bundle for Termina

APP_NAME="Termina"
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# Create directory structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>termina</string>
    <key>CFBundleIdentifier</key>
    <string>com.termina.app</string>
    <key>CFBundleName</key>
    <string>Termina</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSBackgroundOnly</key>
    <false/>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create executable script
cat > "${MACOS_DIR}/termina" << EOF
#!/bin/bash
cd "\$(dirname "\$0")/../../../"
uv run python termina.py
EOF

chmod +x "${MACOS_DIR}/termina"

echo "✅ App bundle created: ${APP_DIR}"
echo "📝 Next steps:"
echo "1. Move ${APP_DIR} to Applications folder"
echo "2. Add to Login Items in System Preferences"