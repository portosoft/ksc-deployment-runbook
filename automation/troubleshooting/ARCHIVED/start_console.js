const { spawn } = require('child_process');
const path = require('path');

// Environment variables
process.env.FEATURE_MESSAGE_BROKER_TYPE = 'nats';
process.env.NATS_ADDRESS = '127.0.0.1';
process.env.NATS_PORT = '8222';
process.env.NSQ_HOST = '127.0.0.1';
process.env.NSQ_PORT = '8222';

// Working directory
const workingDir = '/var/opt/kaspersky/ksc-web-console';
process.chdir(workingDir);

// Command: ./node pm.js ./pm.config.js
const cmd = './node';
const args = ['pm.js', './pm.config.js'];

console.log(`Starting KSC Web Console from ${workingDir}...`);
console.log(`Command: ${cmd} ${args.join(' ')}`);

const child = spawn(cmd, args, {
  cwd: workingDir,
  env: process.env,
  stdio: 'inherit'
});

child.on('close', (code) => {
  console.log(`KSC Web Console exited with code ${code}`);
  process.exit(code);
});

child.on('error', (err) => {
  console.error('Failed to start child process.', err);
  process.exit(1);
});
