#!/usr/bin/env node
const http = require('http');

async function testHealth() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 8001,
      path: '/health',
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => {
        body += chunk;
      });
      res.on('end', () => {
        try {
          const response = {
            status: res.statusCode,
            body: JSON.parse(body)
          };
          resolve(response);
        } catch (e) {
          resolve({
            status: res.statusCode,
            body: body
          });
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });
    req.end();
  });
}

async function main() {
  console.log('Testing health endpoint...');
  try {
    const response = await testHealth();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(response.body, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
