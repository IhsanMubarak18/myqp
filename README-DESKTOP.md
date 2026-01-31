# Question Paper Generator - Desktop Application

A cross-platform desktop application for generating question papers with PDF export functionality.

## Features

- Create and manage question papers with three parts (A, B, C)
- Support for images in questions with configurable positioning
- PDF generation for question papers, answer sheets, and blueprints
- Admin dashboard for managing exam configurations
- SQLite database for data persistence
- Cross-platform support (Ubuntu, Windows, macOS)

## Installation

### Ubuntu

1. Download the `.AppImage` or `.deb` file from the releases page
2. For AppImage:
   ```bash
   chmod +x Question-Paper-Generator-*.AppImage
   ./Question-Paper-Generator-*.AppImage
   ```
3. For .deb:
   ```bash
   sudo dpkg -i question-paper-generator_*.deb
   ```

### Windows

1. Download the `.exe` installer from the releases page
2. Run the installer and follow the installation wizard
3. Launch "Question Paper Generator" from the Start Menu

### macOS

1. Download the `.dmg` file from the releases page
2. Open the DMG and drag the app to Applications folder
3. Launch from Applications (you may need to allow the app in Security & Privacy settings)

## Usage

1. Launch the application
2. The Django server will start automatically (you'll see a loading screen)
3. Once loaded, you can:
   - Create new question papers from the main page
   - Manage exam configurations from the admin dashboard
   - Generate PDFs of your question papers
   - Edit and delete existing question papers

## Data Storage

All your data is stored locally in an SQLite database located at:
- **Ubuntu/Linux**: `~/.config/question-paper-generator/`
- **Windows**: `%APPDATA%\question-paper-generator\`
- **macOS**: `~/Library/Application Support/question-paper-generator/`

## System Requirements

- **Ubuntu**: 18.04 or later
- **Windows**: Windows 10 or later
- **macOS**: macOS 10.13 or later
- **RAM**: 2GB minimum
- **Disk Space**: 500MB free space

## Troubleshooting

### Application won't start
- Make sure you have sufficient permissions
- Check if port 8000-8100 is available
- Try restarting your computer

### Database errors
- The application will automatically run migrations on first start
- If issues persist, delete the database file and restart (you'll lose data)

### PDF generation issues
- Ensure you have write permissions in the media folder
- Check that images are in supported formats (PNG, JPG)

## Development

See [BUILDING.md](BUILDING.md) for instructions on building from source.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please visit the GitHub repository.
