let createError = require('http-errors');
let express = require('express');
let path = require('path');
let net = require('net');

let app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use(express.static(path.join(__dirname, 'public')));

let client = new net.Socket();
client.connect(9090, '127.0.0.1', () => {
  console.log('Connected');
});

app.use('/run', (req, res, next) => {
  console.log(req.query.instructions);
  client.write(req.query.instructions);
});

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
