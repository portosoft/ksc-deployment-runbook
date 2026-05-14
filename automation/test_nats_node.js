const { connect, JSONCodec } = require('nats');

async function test() {
    console.log('Testing NATS connection...');
    try {
        const nc = await connect({ servers: "127.0.0.1:4222" });
        console.log('Connected to NATS!');
        const jc = JSONCodec();
        console.log('Codec created.');
        await nc.flush();
        console.log('Flush done.');
        await nc.close();
        console.log('Closed.');
    } catch (err) {
        console.error('Error:', err);
    }
}

test();
