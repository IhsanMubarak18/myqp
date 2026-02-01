const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const findFreePort = require('find-free-port');

let mainWindow;
let djangoProcess;
let serverPort;
let tray;

const isDev = process.argv.includes('--dev');

function resourcePath(p) {
    return isDev ? path.join(__dirname, p) : path.join(process.resourcesPath, p);
}

function pythonCommand() {
    return process.platform === 'win32' ? 'python' : 'python3';
}

async function startDjangoServer() {
    const [port] = await findFreePort(8000);
    serverPort = port;

    const python = pythonCommand();
    const serverScript = resourcePath('server.py');

    djangoProcess = spawn(python, [serverScript, port], {
        cwd: isDev ? __dirname : process.resourcesPath,
        env: {
            ...process.env,
            PYTHONUNBUFFERED: '1'
        }
    });

    return new Promise((resolve, reject) => {
        let resolved = false;

        djangoProcess.stdout.on('data', (data) => {
            const msg = data.toString();
            console.log(msg);

            if (!resolved && msg.includes('Starting development server')) {
                resolved = true;
                resolve(`http://127.0.0.1:${serverPort}`);
            }
        });

        djangoProcess.stderr.on('data', (err) => {
            console.error(err.toString());
        });

        djangoProcess.on('error', reject);

        setTimeout(() => {
            if (!resolved) {
                resolve(`http://127.0.0.1:${serverPort}`);
            }
        }, 20000);
    });
}

function createWindow(url) {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        show: false,
        icon: resourcePath('build-resources/icon.png'),
        webPreferences: {
            preload: resourcePath('preload.js'),
            contextIsolation: true
        }
    });

    mainWindow.loadFile(resourcePath('loading.html'));
    mainWindow.once('ready-to-show', () => mainWindow.show());

    setTimeout(() => mainWindow.loadURL(url), 1500);
}

function createTray() {
    tray = new Tray(resourcePath('build-resources/icon.png'));
    tray.setContextMenu(Menu.buildFromTemplate([
        { label: 'Show', click: () => mainWindow.show() },
        { label: 'Quit', click: () => app.quit() }
    ]));
}

app.whenReady().then(async () => {
    const url = await startDjangoServer();
    createWindow(url);
    createTray();
});

ipcMain.handle('get-server-url', () => {
    return `http://127.0.0.1:${serverPort}`;
});

ipcMain.handle('go-back', () => {
    if (mainWindow && mainWindow.webContents.canGoBack()) {
        mainWindow.webContents.goBack();
        return true;
    }
    return false;
});

ipcMain.handle('can-go-back', () => {
    return mainWindow && mainWindow.webContents.canGoBack();
});


app.on('before-quit', () => {
    if (djangoProcess) djangoProcess.kill();
});
