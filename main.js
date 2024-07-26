import { WebSocketServer } from "ws";
import { createInterface } from "readline";

const wss = new WebSocketServer({ port: 8032 });
wss.on('connection', function (ws) {
    console.log('client connected');
    // ws.on('message',function (msg) {
    //     console.log(msg)
    //     // data from PhysioLab; relay to all connected clients; PhysioLab should ignore
    //     wss.clients.forEach(function (ws) {
    //         ws.send(msg);
    //     })
    // })
    ws.on('error', console.error);
    ws.on('close', function () {
        console.log('client disconnected');
    })
})

function ask(answer) {
    console.log('sending:',answer);
    wss.clients.forEach(function (ws) {
        ws.send(answer);
    })
    rl.question('send:',ask);
}
const rl = createInterface({ input: process.stdin, output: process.stdout });
rl.question('send:',ask);
