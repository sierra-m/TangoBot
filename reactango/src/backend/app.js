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

module.exports = app;
