var Socket = module.exports = {
  io: null,
  init: function(port) {
    this.io = require('socket.io').listen(port);
    this.io.on('connection', (socket) => {
      console.log('a user connected');

      socket.on('disconnect', () => {
        console.log('user disconnected');
      });
    });
    return this.io;
  }
}
