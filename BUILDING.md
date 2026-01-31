# Building Question Paper Generator Desktop App

This guide explains how to build the desktop application installers for all platforms.

## Prerequisites

### Required Software

1. **Node.js** (v16 or later)
   ```bash
   # Ubuntu
   sudo apt install nodejs npm
   
   # macOS
   brew install node
   
   # Windows
   # Download from https://nodejs.org/
   ```

2. **Python 3** (3.8 or later)
   ```bash
   # Ubuntu
   sudo apt install python3 python3-pip python3-venv
   
   # macOS
   brew install python3
   
   # Windows
   # Download from https://python.org/
   ```

3. **Platform-specific build tools**
   
   **Ubuntu:**
   ```bash
   sudo apt install build-essential
   ```
   
   **Windows:**
   - Install Visual Studio Build Tools or Visual Studio Community
   
   **macOS:**
   ```bash
   xcode-select --install
   ```

## Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd /home/user/Documents/question_paper_app/Question-_paper_new
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   # Create virtual environment (optional but recommended for testing)
   python3 -m venv app_env
   source app_env/bin/activate  # On Windows: app_env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## Building

### Development Mode

To run the application in development mode (without building):

```bash
npm run dev
```

This will:
- Start Electron with your system Python
- Use the local Django project
- Enable DevTools for debugging

### Build for Current Platform

To build an installer for your current platform:

```bash
npm run build
```

This creates an installer in the `dist/` folder for your current OS.

### Build for Specific Platforms

**Linux only:**
```bash
npm run build:linux
```
Creates: `.AppImage` and `.deb` files

**Windows only:**
```bash
npm run build:win
```
Creates: `.exe` installer

**macOS only:**
```bash
npm run build:mac
```
Creates: `.dmg` file

### Build for All Platforms

To build installers for all platforms (requires appropriate OS or CI/CD):

```bash
npm run build:all
```

**Note:** Building for macOS requires a Mac. Building for Windows can be done on Linux/Mac with Wine, but native builds are recommended.

## Python Runtime Bundling

The desktop app needs to bundle Python runtime for distribution. This is currently handled by the build process, but you may need to:

1. **Create python-runtime folder** (for production builds)
   ```bash
   mkdir -p python-runtime
   ```

2. **Copy Python runtime** (platform-specific)
   
   This step is complex and varies by platform. For now, the app uses system Python in development mode.
   
   For production, consider using:
   - **PyInstaller** to create standalone Python executables
   - **python-build-standalone** for portable Python builds
   - Platform-specific Python installers bundled with the app

## Output

After building, you'll find installers in the `dist/` folder:

- **Ubuntu**: `Question-Paper-Generator-1.0.0.AppImage`, `question-paper-generator_1.0.0_amd64.deb`
- **Windows**: `Question Paper Generator Setup 1.0.0.exe`
- **macOS**: `Question Paper Generator-1.0.0.dmg`

## Testing Builds

### Ubuntu
```bash
# AppImage
chmod +x dist/Question-Paper-Generator-*.AppImage
./dist/Question-Paper-Generator-*.AppImage

# .deb
sudo dpkg -i dist/question-paper-generator_*.deb
question-paper-generator
```

### Windows
```cmd
# Run the installer
dist\Question Paper Generator Setup 1.0.0.exe
```

### macOS
```bash
# Open the DMG and drag to Applications
open dist/Question\ Paper\ Generator-1.0.0.dmg
```

## Troubleshooting

### Build fails with "electron-builder not found"
```bash
npm install --save-dev electron-builder
```

### Build fails with Python errors
- Ensure Python 3.8+ is installed
- Check that all requirements are installed: `pip install -r requirements.txt`

### Large bundle size
- The app includes Python runtime and all dependencies (~200-400MB)
- This is normal for Python-based desktop apps
- Consider using PyInstaller to optimize Python bundling

### Code signing (macOS/Windows)
For distribution, you should sign your applications:
- **macOS**: Requires Apple Developer account and certificate
- **Windows**: Requires code signing certificate

Add to `package.json` build config:
```json
"mac": {
  "identity": "Your Name (TEAM_ID)"
},
"win": {
  "certificateFile": "path/to/cert.pfx",
  "certificatePassword": "password"
}
```

## CI/CD

For automated builds, consider using:
- **GitHub Actions** with matrix builds for all platforms
- **CircleCI** or **Travis CI** with multiple OS support

Example GitHub Actions workflow:
```yaml
name: Build
on: [push]
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run build
```

## Advanced Configuration

Edit `package.json` under the `build` section to customize:
- Application name and ID
- File associations
- Auto-updater configuration
- Custom installer options

See [electron-builder documentation](https://www.electron.build/) for all options.
