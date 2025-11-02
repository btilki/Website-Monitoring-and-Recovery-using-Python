// Simple Node.js HTTP server for demo purposes
const http = require('http');

const port = process.env.PORT || 3000;

const requestHandler = (req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello from Node.js!\\n');
};

const server = http.createServer(requestHandler);

server.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});