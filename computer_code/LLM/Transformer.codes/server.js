// Run: npm run dev (local) || npm start (prod)

// 1. import dependencies
import { app, port, environment } from './app.js';

// 2. set max port
const maxPort = port + 15;

// 3. define function to locally start server on
// an available port in the range [port, maxPort]
function startServer(port) {
    const server = app.listen(port, () => {
        console.log(`Server started on port ${port}`);
    });

    server.on('error', (error) => {
        if (error.code === 'EADDRINUSE') {
            console.log(`Port ${port} is in use, trying the next one...`);
            if (port < maxPort) {
                startServer(++port);
            } else {
                console.error('No available ports in the specified range.');
            }
        } else {
            console.error(`Failed to start server: ${error.message}`);
        }
    });
}

// 4. listen
if (environment === 'development') {
    startServer(port);
} else {
    app.listen(port, () => {
        console.log(`Server started on port ${port}`);
    });
}
