const { app, BrowserWindow, ipcMain, Tray, Menu, globalShortcut } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const findFreePort = require('find-free-port');

let mainWindow;
let djangoProcess;
let serverPort;
let tray;

// Determine if running in development mode
const isDev = process.argv.includes('--dev');

// Get the correct paths for resources
function getResourcePath(relativePath) {
    if (isDev) {
        return path.join(__dirname, relativePath);
    }
    // In production, resources are in the app.asar or extraResources
    return path.join(process.resourcesPath, relativePath);
}

// Find Python executable
function getPythonCommand() {
    if (isDev) {
        // In development, use system Python or virtual environment
        return process.platform === 'win32' ? 'python' : 'python3';
    }

    // In production, use bundled Python
    const pythonRuntime = getResourcePath('python-runtime');
    if (process.platform === 'win32') {
        return path.join(pythonRuntime, 'python.exe');
    } else if (process.platform === 'darwin') {
        return path.join(pythonRuntime, 'bin', 'python3');
    } else {
        return path.join(pythonRuntime, 'bin', 'python3');
    }
}

// Start Django server
async function startDjangoServer() {
    return new Promise(async (resolve, reject) => {
        try {
            // Find a free port
            const [freePort] = await findFreePort(8000);
            serverPort = freePort;

            console.log(`Starting Django server on port ${serverPort}...`);

            const pythonCmd = getPythonCommand();
            const managePy = isDev
                ? path.join(__dirname, 'manage.py')
                : getResourcePath('manage.py');

            // Start Django development server
            djangoProcess = spawn(pythonCmd, [
                managePy,
                'runserver',
                `127.0.0.1:${serverPort}`,
                '--noreload'
            ], {
                cwd: isDev ? __dirname : getResourcePath(''),
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: '1',
                    DJANGO_SETTINGS_MODULE: 'question_paper_project.settings'
                }
            });

            djangoProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log(`Django: ${output}`);

                // Check if server is ready
                if (output.includes('Starting development server') ||
                    output.includes('Quit the server')) {
                    console.log('Django server is ready!');
                    resolve(`http://127.0.0.1:${serverPort}`);
                }
            });

            djangoProcess.stderr.on('data', (data) => {
                console.error(`Django Error: ${data}`);
            });

            djangoProcess.on('error', (error) => {
                console.error('Failed to start Django server:', error);
                reject(error);
            });

            djangoProcess.on('close', (code) => {
                console.log(`Django process exited with code ${code}`);
            });

            // Timeout after 30 seconds
            setTimeout(() => {
                resolve(`http://127.0.0.1:${serverPort}`);
            }, 30000);

        } catch (error) {
            reject(error);
        }
    });
}

// Create the main window
function createWindow(serverUrl) {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        icon: path.join(__dirname, 'build-resources', 'icon.png'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
        show: false, // Don't show until ready
    });

    // Show loading screen first
    mainWindow.loadFile(path.join(__dirname, 'loading.html'));
    mainWindow.show();

    // Wait a bit for Django to be fully ready, then load the app
    setTimeout(() => {
        mainWindow.loadURL(serverUrl);
    }, 2000);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Handle window close
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Add zoom controls
    const zoomIn = () => {
        const currentZoom = mainWindow.webContents.getZoomFactor();
        mainWindow.webContents.setZoomFactor(currentZoom + 0.1);
    };

    const zoomOut = () => {
        const currentZoom = mainWindow.webContents.getZoomFactor();
        mainWindow.webContents.setZoomFactor(Math.max(0.5, currentZoom - 0.1));
    };

    const resetZoom = () => {
        mainWindow.webContents.setZoomFactor(1.0);
    };

    // Register zoom shortcuts
    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.control || input.meta) {
            if (input.key === '=' || input.key === '+') {
                zoomIn();
            } else if (input.key === '-') {
                zoomOut();
            } else if (input.key === '0') {
                resetZoom();
            }
        }
    });

    // Create application menu with zoom controls
    const template = [
        {
            label: 'View',
            submenu: [
                {
                    label: 'Zoom In',
                    accelerator: 'CmdOrCtrl+=',
                    click: zoomIn
                },
                {
                    label: 'Zoom Out',
                    accelerator: 'CmdOrCtrl+-',
                    click: zoomOut
                },
                {
                    label: 'Reset Zoom',
                    accelerator: 'CmdOrCtrl+0',
                    click: resetZoom
                },
                { type: 'separator' },
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' }
            ]
        },
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'close' }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);

    // Open DevTools in development mode
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }
}

// Create system tray
function createTray() {
    const iconPath = path.join(__dirname, 'build-resources', 'icon.png');
    tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show App',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                }
            }
        },
        {
            label: 'Quit',
            click: () => {
                app.quit();
            }
        }
    ]);

    tray.setToolTip('Question Paper Generator');
    tray.setContextMenu(contextMenu);

    // Show window on tray click
    tray.on('click', () => {
        if (mainWindow) {
            mainWindow.show();
        }
    });
}

// App ready event
app.whenReady().then(async () => {
    try {
        console.log('Starting Question Paper Generator...');

        // Start Django server
        const serverUrl = await startDjangoServer();
        console.log(`Server URL: ${serverUrl}`);

        // Create main window
        createWindow(serverUrl);

        // Create system tray
        createTray();

    } catch (error) {
        console.error('Failed to start application:', error);
        app.quit();
    }
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Activate event (macOS)
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow(`http://127.0.0.1:${serverPort}`);
    }
});

// Clean up Django process on quit
app.on('before-quit', () => {
    if (djangoProcess) {
        console.log('Stopping Django server...');
        djangoProcess.kill();
    }
});

// Handle IPC messages
ipcMain.on('get-server-url', (event) => {
    event.reply('server-url', `http://127.0.0.1:${serverPort}`);
});
