'use strict';

const express  = require('express');
const verifier = require('alexa-verifier');
const alexa = require('alexa-app');

const express_app = express();
const bodyParser = require('body-parser');
const alexa_app = new alexa.app('sonos');
const SpotifyApi = require('spotify-web-api-node');
const spotify_api = new SpotifyApi();

// Run server to listen on port 3000.
const server = express_app.listen(3000, function () {
  console.log('listening on port 3000');
});

const io = require('socket.io')(server);
express_app.use(bodyParser.urlencoded({ extended: false } ));
express_app.use(express.static('static'));

// the alexa API calls specify an HTTPS certificate that must be validated.
express_app.use(function(req, res, next) {
  if (!req.headers.signaturecertchainurl) {
    return next();
  }

  // mark the request body as already having been parsed so it's ignored by
  // other body parser middlewares
  req._body = true;
  req.rawBody = '';
  req.on('data', function(data) {
    return req.rawBody += data;
  });
  req.on('end', function() {
    var cert_url, er, error, requestBody, signature;
    try {
      req.body = JSON.parse(req.rawBody);
    } catch (error) {
      er = error;
      req.body = {};
    }
    cert_url = req.headers.signaturecertchainurl;
    signature = req.headers.signature;
    requestBody = req.rawBody;
    verifier(cert_url, signature, requestBody, function(er) {
      if (er) {
        console.error('error validating the alexa cert:', er);
        res.status(401).json({ status: 'failure', reason: er });
      } else {
        next();
      }
    });
  });
});

express_app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

express_app.get('/', function (req, res) {
  res.send('OK');
});

alexa_app.error = function(exception, request, response) {
  console.log(exception);
  response.say('Sorry, something bad happened');
};

alexa_app.intent('Play',
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
      response.say('which room would you like Sonos to play in?').reprompt('Where?');
      response.shouldEndSession(false);
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
          spotify_api.searchAlbums(query)
            .then(function(data) {
              var albums = data.body['albums']['items'];
              var album = albums[0];
              id = album.id;
              console.log('ID 1 = '+id);
            }, function(err) {
              console.error(err);
            });
        }else{
          spotify_api.searchTracks(query)
            .then(function(data) {
              console.log('Track search: '+query, data.body);
            }, function(err) {
              console.error(err);
            });
        }

      }else {
        //no query has been passed - just unpause the music

      }
      //send a socket message to the proxy client
      console.log('ID 2 = '+id);
      console.log('sending',type, id);
      io.emit('sonos:play', {'type':type, 'id': id});
      response.say('Playing in the '+room);
    }
  }
);

alexa_app.express(express_app, '/echo/', true);

// Set socket.io listeners.
io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('disconnect', () => {
    console.log('user disconnected');
  });
});
