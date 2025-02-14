const WebSocket = require('ws');
const fs = require('fs')
const net = require('net');

// g3obj.js
class G3WebSocket {
    // constructor(hostname = window.location.hostname, port = window.location.port) {
    constructor(hostname = '', port = '') {
        const urlParams = new URLSearchParams('');
        if (urlParams.get('address') != undefined)
            this.hostname = urlParams.get('address');
        else
            this.hostname = hostname;

        if (urlParams.get('port') != undefined)
            this.port = urlParams.get('port');
        else
            this.port = port;

        this.nextid = 0;
        this.queue = {};
        this.signals = {};
        this.statuswait = 0;
    }

    open(path = "", user = "") {
        if (this.popen != undefined)
            return this.popen;

        this.popen = new Promise((resolve, reject) => {
            this.ws = new WebSocket("ws://" + user + this.hostname + ":" +
                this.port + path + "/websocket", "g3api");
            console.log("ws://" + user + this.hostname + ":" + this.port + path + "/websocket")
            this.ws.onclose = (e) => this._close(e);
            this.ws.onerror = (e) => {
                reject();
            };
            this.ws.onopen = () => {
                this.ws.onmessage = (msg) => { this._msg(JSON.parse(msg.data)) };
                this.ws.onerror = (e) => {
                    this._error();
                };
                resolve(this);
            };
        });
        return this.popen;
    }

    _close(e) {
        if (e.wasClean == true)
            return;
        return
        var nocon = new G3PopUp(
            "Communication lost",
            "The connection to the Recording Unit was lost. Trying to reconnect.<p>"
        );
        if (!nocon)
            return;
        var timeout = setInterval(() => {
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = () => {
                if (xhttp.readyState == 4) {
                    if (xhttp.status == 200) {
                        location.reload();
                    }
                }
            }
            xhttp.open("GET", window.location.href);
            xhttp.send();
        }, 2000);
    }

    async _error() {
        var div = document.createElement("div");
        div.innerHTML = "TEST";
        document.getElementsByTagName("body")[0].append(div);
    }

    _msg(msg) {
        if ("signal" in msg) {
            if (msg.signal in this.signals)
                this.signals[msg.signal].func(msg.body);
            else
                console.log("Missing signal: " + msg.signal, msg);
            return;
        }
        if (msg.id in this.queue) {
            if ("error" in msg) {
                this.queue[msg.id][1](msg.message);
            } else {
                this.queue[msg.id][0](msg.body);
            }
            delete this.queue[msg.id];
        }
        if (this._statusdone !== undefined) {
            clearTimeout(this._statusdone);
            delete this._statusdone;
        }
        // if (Object.keys(this.queue).length == 0) {
        //     this._statusdone = setTimeout(() => {
        //         statusdiv.classList.remove("menucom");
        //     }, 100);
        // }
    }


    async close() {
        for (var sig in this.signals) {
            this.disconnect(sig);
        }
        await this.ws.close();
    }

    send(context) {
        return new Promise((resolve, reject) => {
            var obj = {
                path: context.path,
                id: this.nextid += 1,
            };
            if (context.body !== undefined) {
                obj.method = "POST";
                obj.body = context.body;
            } else {
                obj.method = "GET";
            }
            if (context.args !== undefined)
                obj.params = context.args;
            this.queue[obj.id] = [
                (body) => { resolve(body) },
                (msg) => { reject(msg) },
                context
            ];
            // statusdiv.classList.add("menucom");
            this.ws.send(JSON.stringify(obj));
        });
    }

    connect(path, func) {
        return this.send({ path: path, body: null })
            .then((body) => {
                this.signals[body] = {
                    path: path,
                    name: path.split(":").pop(),
                    func: func
                };
                return body;
            })
            .catch((msg) => {
                console.log("Signal error: " + path + " : " + msg);
            });
    }

    async disconnect(id) {
        if (id in this.signals) {
            await this.send({ path: this.signals[id].path, body: id })
            delete this.signals[id];
        } else {
            console.log("Id not in signals");
        }
    }
}


class G3Obj {
    constructor(ws = null, path = "/") {
        this.path = path;
        if (ws == null)
            ws = new G3WebSocket();
        this.ws = ws;
    }

    async open() {
        return await this.ws.open();
    }

    name() {
        return this.path.split("/").pop();
    }

    get(name) {
        return this.ws.send({
            path: this.path + "." + name
        });
    }

    set(name, val) {
        return this.ws.send({
            path: this.path + "." + name,
            body: val
        });
    }

    call(action, args = []) {
        return this.ws.send({
            path: this.path + "!" + action,
            body: args
        });
    }

    connect(signal, func) {
        console.log(this.path + ":" + signal)
        return this.ws.connect(this.path + ":" + signal, func);
    }

    async connect_children(addfunc, remfunc) {
        var lst = await this.children();
        for (var i in lst)
            addfunc(lst[i]);
        return [
            this.connect("child-added", (v) => addfunc(v[0])),
            this.connect("child-removed", (v) => remfunc(v[0]))
        ];
    }

    async disconnect_children(ret) {
        this.disconnect("child-added", ret[0]);
        this.disconnect("child-removed", ret[1]);
    }

    disconnect(id) {
        return this.ws.disconnect(id);
    }

    child(name) {
        return new G3Obj(this.ws, this.path + "/" + name);
    }

    children() {
        return this.object()
            .then((obj) => { return obj.children; });
    }

    properties() {
        return this.object()
            .then((obj) => { return obj.properties; });
    }

    object(help = false) {
        return this.ws.send({
            path: this.path,
            args: { "help": help }
        });
    }
}

// g3common.js

var menuitems = {
    "Home": "index.html",
    "Live": "live.html",
    "Recordings": "recorder.html",
    "Network": "network.html",
    "Calibrate": "calib.html",
    "Storage": "storage.html",
    "Rudimentary": "rudimentary.html",
    "API": "browse.html",
    "License": "license.html"
};

var ICON_EMPTY = "&nbsp;";
var ICON_WAIT = "&#10711;";
var ICON_COM = "&#9889;";
var ICON_PLAY = "&#9654;";
var ICON_STOP = "&#9632;";
var ICON_CALIBRATE = "&#9673;";
var ICON_CALIBRATE_NO_MARKER = "&#x1f441;";
var ICON_OK = "&#10004";
var ICON_CANCEL = "&#10008";
var ICON_RECORD = "&#9899";
var ICON_REFRESH = "&#8635;"

// var statusdiv = document.createElement("span")
// statusdiv.innerHTML = ICON_COM;
// statusdiv.classList.add("menu");
// statusdiv.classList.add("right");

/* Build menu */
function common_menu() {
    var page = window.location.pathname.split("/").slice(-1)[0];
    var menu = document.createElement("div");
    var icon = document.createElement('link');
    icon.type = "image/png";
    icon.rel = "shortcut icon";
    icon.href = "favicon.png";
    document.getElementsByTagName('head')[0].appendChild(icon);

    menu.y = 0;
    menu.classList.add("menu");
    const urlParams = new URLSearchParams(window.location.search).toString();
    for (var i in menuitems) {
        var a = document.createElement("a");
        a.classList.add("menu");
        if (menuitems[i] == page)
            a.classList.add("menuactive");

        a.innerHTML = i;
        var url = menuitems[i];
        if (urlParams != "")
            url = url + "?" + urlParams;

        a.href = url;
        menu.appendChild(a);
    }
    menu.appendChild(statusdiv);
    document.body.prepend(menu);
}

// common_menu();

function g3_dur_to_time(dur, dig = 0) {
    if (dur < 0)
        return "-:--:--";
    var h = Math.floor(dur / (60 * 60));
    var m = Math.floor((dur.toFixed(0) % (60 * 60)) / 60);
    if (m < 10)
        m = "0" + m;
    var s = Math.floor(dur) % 60;
    if (s < 10)
        s = "0" + s;
    d = (dig > 0) ? "." : "";

    return h + ":" + m + ":" + s;
}

var g3_checkbox_cnt = 0;

function g3_checkbox(title = "") {
    g3_checkbox_cnt++;
    var id = "checkbox" + g3_checkbox_cnt;
    var div = document.createElement("div");
    var box = document.createElement("input");
    box.type = "checkbox";
    box.id = id;
    div.append(box);
    var lbl = document.createElement("label");
    lbl.innerHTML = title;
    lbl.setAttribute("for", id);
    div.append(lbl);
    return [div, box];
}


class G3PopUp {
    constructor(headtext, label) {
        this.div = document.createElement("div");
        this.div.classList.add("popup");
        var box = document.createElement("div");
        box.classList.add("box");
        this.div.append(box);

        var head = document.createElement("h1");
        head.innerHTML = headtext;
        box.append(head);

        this.info = document.createElement("div");
        this.info.classList.add("info");
        this.info.innerHTML = label;
        box.append(this.info);
        document.getElementsByTagName("body")[0].append(this.div);
    }
}

function g3_v2s(vert, decimals = 3, leftpad = 0) {
    var s = [];
    vert.forEach((v) => {
        s.push(((v >= 0) ? " " + v.toFixed(decimals) : v.toFixed(decimals)).padStart(leftpad, " "))
    });
    return "(" + s.join(", ") + ")";
}


// Main worker
{
    let gazeJson, sceneBuffer;

    var root = new G3Obj();
    root.ws['hostname'] = 'tg03b-080201140731.local'
    console.log(root)
    console.log(root.ws)
    root.open()
        .then(() => {
            let rudi = root.child("rudimentary")
            console.log(rudi)

            let keepalive = () => {
                rudi.call("keepalive");
                console.log('Send keepalive request.')
            }

            setInterval(keepalive, 5000)

            const client = new net.Socket();
            client.connect(19931, '127.0.0.1', () => {
                console.log('Connected to eye-movement-loop.py');
            });

            async function fetchGaze() {
                await rudi.connect("gaze", (body) => {
                    console.log(body)
                    gazeJson = JSON.stringify(body)
                    const message = "gaze" + gazeJson;
                    const length = Buffer.byteLength(message);
                    client.write(Buffer.from(length.toString().padStart(8, '0') + message));
                })
            }

            async function fetchScene() {
                await rudi.connect("scene", (body) => {
                    console.log(body[0], body[1].slice(0, 100))
                    // body[1] is the image, send it through the socket
                    const message = "scene" + body[1];
                    const length = Buffer.byteLength(message);
                    client.write(Buffer.from(length.toString().padStart(8, '0') + message));
                });
            }

            fetchGaze()
            fetchScene()
        })
}
