'use strict';

var alexa = require('alexa-app');
var app = new alexa.app('sonos');

var socket = require('./../../socket.js');

// Allow this module to be reloaded by hotswap when changed
module.change_code = 1;

var SpotifyApi = require('spotify-web-api-node');
var spotify_api = new SpotifyApi();

app.error = function(exception, request, response) {
  console.log(exception);
  response.say('Sorry, something bad happened');
};

app.launch(function(req,res) {
	res.say("Control your Sonos");
});

app.intent('Play',
  {
    'slots':{'room':'ROOM', 'artist':'ARTIST', 'track': 'TRACK'}
    ,'utterances':[
      'play some {artist} in the {room}',
      'play some {artist}',
      'play something by {artist} in the {room}',
      'play something by {artist}',
      'play {track} by {artist} in the {room}',
      'play {track} by {artist}'
    ]
  },
  function(request,response) {
    var room = request.slot('room'),
    artist = request.slot('artist'),
    track = request.slot('track');

    var id = '';
    var type = 'album';

    //check if anything has been passed for artist or track
    if (!room) {
      if (artist) response.session('artist',artist);
      if (track) response.session('track',track);
      var prompt = 'which room would you like music to play in?';
      response.say(prompt).reprompt(prompt).shouldEndSession(false);
    }else{
      //search the Spotify API for something appropriate
      var query = '';
      if (artist) query = 'artist:'+artist+' ';
      if (track) {
        query += 'track:'+track;
        type = 'track';
      }
      if (query != '') {
        if (type == 'album') {
          getSpotifyAlbum(query).then(function(album) {
            var artist = album.artists[0].name;
            sendSocketMessage('play', room, 'album', album.id);
            response.say('playing '+ album.name + ' by ' + artist).send();
          });
        }else{
          //search for a track
          getSpotifyTrack(query).then(function(track) {
            var artist = track.artists[0].name;
            sendSocketMessage('play', room,'track', track.id);
            response.say('playing '+ track.name + ' by ' + artist).send();
          });
        }
        return false;

      }else {
        //no query has been passed - just unpause the music
        sendSocketMessage('play', room);
        response.say('playing in the '+room).send();
      }
    }
    return false;
  }
);

app.intent('Pause',
  {
    'slots':{'room':'ROOM'}
    ,'utterances':[
      'pause in the {room}',
      'pause'
    ]
  },
  function(request,response) {
    var room = request.slot('room');
    sendSocketMessage('pause', room);
    response.say('pausing in the '+room).send();
  }
);

function getSpotifyAlbum(query) {
  console.log('get spotify album');
  return new Promise(function (resolve, reject) {
    spotify_api.searchAlbums(query, { limit: 10 }, function(err, data) {
      if (err) {
        reject(err);
        process.exit();
      }
      var albums = data.body.albums.items;
      var album = albums[0];
      var id = album.id;
      resolve(album);
    });
  });
}

function getSpotifyTrack(query) {
  return new Promise(function (resolve, reject) {
    spotify_api.searchTracks(query, { limit: 10 }, function(err, data) {
      if (err) {
        reject(err);
        process.exit();
      }
      var tracks = data.body.tracks.items;
      var track = tracks[0];
      resolve(track);
    });
  });
}

function sendSocketMessage(command, room, type, id) {
    //send a socket message to the proxy client
    if (command == 'play') {
      if (id) {
        console.log('sending play response',type, id);
        if (socket.io) socket.io.emit('sonos:play', {'type':type, 'id': id, 'room':room});
      }else {
        if (socket.io) socket.io.emit('sonos:unpause', {'room':room});
      }
    }

    if (command == 'pause') {
      if (socket.io) socket.io.emit('sonos:pause', {'room':room});
    }
}

module.exports = app;
