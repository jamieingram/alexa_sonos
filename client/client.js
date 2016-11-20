const io = require('socket.io-client');
const http = require('http');

const socket = io.connect('http://localhost:8080', {reconnect: true});

// Add a connect listener
socket.on('connect', function (socket) {
    console.log('Connected!');
});

socket.on('sonos:play', function (data) {
  console.log(data);
  //we now have a room target
  var path = '/'+escape(data.room)+'/spotify/now/spotify:album:'+data.id;
  sendHTTPCommand(path);
});

socket.on('sonos:pause', function (data) {
  var path = '/'+escape(data.room)+'/pause';
  sendHTTPCommand(path);
});

socket.on('sonos:unpause', function (data) {
  var path = '/'+escape(data.room)+'/play';
  sendHTTPCommand(path);
});

function sendHTTPCommand(path) {
  var options = {
    host: 'arran',
    port: 5005,
    path: path
  };

  http.get(options, function(resp){
    resp.on('data', function(chunk){
      //do something with chunk
    });
  }).on("error", function(e){
    console.log("Got error: " + e.message);
  });
}
