import { WebSocket, WebSocketServer } from 'ws';
import { createInterface } from 'readline';

if (process.platform == 'win32')
    createInterface({ input: process.stdin, output: process.stdout }).on(
        'SIGINT',
        function () {
            process.emit('SIGINT');
        }
    );

process.on('SIGINT', function () {
    console.log('Keyboard interrupt recieved, exiting.');
    wss.clients.forEach(function (ws) {
        ws.close()
    });
    wss.close();
});

const wss = new WebSocketServer({ port: 8032 });
wss.on('connection', function (ws) {
    console.log('client connected');
    ws.on('message', function (msg, isBinary) {
        // data from PhysioLab; relay to all connected clients; PhysioLab should ignore
        wss.clients.forEach(function (ws) {
            if (ws != wss && ws.readyState == WebSocket.OPEN) {
                ws.send(msg, { binary: isBinary });
            }
        });
    });
    ws.on('error', console.error);
    ws.on('close', function () {
        console.log('client disconnected');
    });
});
wss.on('listening', function () {
    console.log(`listening on port ${8032}`);
});

// function ask(answer) {
//     console.log('sending:',answer);
//     wss.clients.forEach(function (ws) {
//         ws.send(answer);
//     })
//     rl.question('send:',ask);
// }
// const rl = createInterface({ input: process.stdin, output: process.stdout });
// rl.question('send:',ask);
