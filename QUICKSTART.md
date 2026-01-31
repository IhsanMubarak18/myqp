# Quick Start Guide - Question Paper Generator Desktop App

## For Users

### Installation

**Ubuntu:**
```bash
# Download and run AppImage
chmod +x Question-Paper-Generator-*.AppImage
./Question-Paper-Generator-*.AppImage

# Or install .deb package
sudo dpkg -i question-paper-generator_*.deb
```

**Windows:**
- Download and run the `.exe` installer
- Follow the installation wizard

**macOS:**
- Download the `.dmg` file
- Drag app to Applications folder

### Usage

1. Launch "Question Paper Generator" from your applications
2. Wait for the loading screen (Django server starting)
3. Use the application normally - all features work as before!

---

## For Developers

### Testing in Development Mode

```bash
cd /home/user/Documents/question_paper_app/Question-_paper_new

# Quick test
./test-desktop.sh

# Or manually
npm install          # First time only
npm run dev         # Start in development mode
```

### Building Installers

```bash
# Install dependencies (first time only)
npm install

# Build for current platform
npm run build

# Build for specific platforms
npm run build:linux    # .AppImage + .deb
npm run build:win      # .exe installer
npm run build:mac      # .dmg installer

# Build for all platforms
npm run build:all
```

Installers will be in the `dist/` folder.

### Project Structure

```
Question-_paper_new/
├── main.js              # Electron main process (Django auto-start)
├── preload.js           # IPC bridge
├── loading.html         # Loading screen
├── server.py            # Django wrapper
├── package.json         # NPM config + build settings
├── build-resources/     # App icons
├── question_paper/      # Django app (unchanged)
└── db.sqlite3          # Database
```

### Key Files Created

- `package.json` - Electron project configuration
- `main.js` - Main process with Django integration
- `preload.js` - Secure IPC communication
- `loading.html` - Professional loading screen
- `server.py` - Django startup wrapper
- `build-resources/` - Platform-specific icons

### How It Works

1. User launches the Electron app
2. `main.js` starts Django server on available port (8000-8100)
3. Loading screen shows while Django initializes
4. BrowserWindow loads Django web interface
5. All Django features work normally
6. On quit, Django server stops gracefully

### Requirements

- **Development**: Node.js 16+, Python 3.8+, Django 5.2.5
- **Production**: Everything bundled in installer

See [BUILDING.md](file:///home/user/Documents/question_paper_app/Question-_paper_new/BUILDING.md) for detailed build instructions.
