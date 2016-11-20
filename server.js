var AlexaAppServer = require('alexa-app-server');

var config = require('config');

var server = new AlexaAppServer ({
    server_root:__dirname,        // Path to root
    public_html:"public_html",    // Static content
    app_dir:"apps",               // Where alexa-app modules are stored
    app_root:"/alexa/",           // Service root
    port:config.get('Server.port')// What port to use
}).start();

var socket = require('./socket.js');
var io = socket.init(server);
