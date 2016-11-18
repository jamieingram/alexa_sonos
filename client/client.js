const io = require('socket.io-client');
const http = require('http');

const socket = io.connect('http://localhost:3000', {reconnect: true});

// Add a connect listener
socket.on('connect', function (socket) {
    console.log('Connected!');
});

socket.on('sonos:play', function (data) {
  console.log(data);
  //we now have a room target
  var options = {
    host: 'arran',
    port: 5005,
    path: '/Living%20Room/play'
  };

  http.get(options, function(resp){
    resp.on('data', function(chunk){
      //do something with chunk
    });
  }).on("error", function(e){
    console.log("Got error: " + e.message);
  });
});

socket.on('sonos:stop', function (data) {

});
