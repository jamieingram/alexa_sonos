var Socket = module.exports = {
  io: null,
  init: function(server) {
    this.io = require('socket.io')(server);
    this.io.on('connection', (socket) => {
      console.log('a user connected');

      socket.on('disconnect', () => {
        console.log('user disconnected');
      });
    });
    return this.io;
  }
}
