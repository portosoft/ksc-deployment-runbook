"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const nats_1 = require("nats");
const nats_2 = require("../constants/nats");
const helpers_1 = require("../helpers");
const logger_1 = __importDefault(require("../helpers/logger"));
const NATS_ADDRESS = (0, helpers_1.parseEnvVariable)('NATS_ADDRESS');
const NATS_PORT = (0, helpers_1.parseEnvVariable)('NATS_PORT');
const NATS_SERVERS = (0, helpers_1.parseEnvVariable)('NATS_SERVERS');
const NATS_TLS_CAFILE = (0, helpers_1.parseEnvVariable)('NATS_TLS_CAFILE');
const NATS_TLS_CERTFILE = (0, helpers_1.parseEnvVariable)('NATS_TLS_CERTFILE');
const NATS_TLS_KEYFILE = (0, helpers_1.parseEnvVariable)('NATS_TLS_KEYFILE');
const COMPONENT_NAME = 'NATS_CONNECTION_CREATOR';
class ConnectionCreator {
    constructor(onDisconnect = () => {
        global.runtime.logger.error(`${COMPONENT_NAME}: Call "process.exit(1)`);
        process.exit(1);
    }) {
        this.onDisconnect = onDisconnect;
        this.logPrefix = COMPONENT_NAME;
        this.logger = new logger_1.default(this.logPrefix);
        this.connectionOptions = this.getConnectionOptions();
    }
    getServerAddress() {
        if (NATS_SERVERS) {
            return NATS_SERVERS.split(',');
        }
        else if (NATS_ADDRESS && NATS_PORT) {
            return `${NATS_ADDRESS}:${NATS_PORT}`;
        }
        throw new Error('NATS Configuration error: no server address specified');
    }

    getConnectionOptions() {
        let reconnectTimeout = nats_2.Reconnect.START;
        const opts = {
            servers: this.getServerAddress(),
            maxReconnectAttempts: -1,
            reconnect: true,
            reconnectDelayHandler: () => {
                reconnectTimeout = this.calculateReconnectTimeout(reconnectTimeout);
                return reconnectTimeout;
            },
            tls: this.getTlsOptions()
        };
        return opts;
    }
    getTlsOptions() {
        const tls = {};
        if (NATS_TLS_CAFILE === null || NATS_TLS_CAFILE === void 0 ? void 0 : NATS_TLS_CAFILE.length) {
            tls.caFile = NATS_TLS_CAFILE;
        }
        if (NATS_TLS_CERTFILE === null || NATS_TLS_CERTFILE === void 0 ? void 0 : NATS_TLS_CERTFILE.length) {
            tls.certFile = NATS_TLS_CERTFILE;
        }
        if (NATS_TLS_KEYFILE === null || NATS_TLS_KEYFILE === void 0 ? void 0 : NATS_TLS_KEYFILE.length) {
            tls.keyFile = NATS_TLS_KEYFILE;
        }
        if (Object.keys(tls).length) {
            return tls;
        }
        else {
            return undefined;
        }
    }

    calculateReconnectTimeout(reconnectTimeout) {
        return reconnectTimeout < nats_2.Reconnect.MIN ? reconnectTimeout * 2 : nats_2.Reconnect.MAX;
    }

    async connectToNats() {
        let reconnectCounter = 0;
        return new Promise((resolve, reject) => {
            this.logger.log('Start connecting to NATS server');
            let reconnectTimeout = nats_2.Reconnect.DEFAULT;
            const pollConnect = async () => {
                reconnectCounter += 1;
                this.logger.log(`Start create а new connection, (attempt #${reconnectCounter})`);
                try {
                    this.connection = await (0, nats_1.connect)(this.connectionOptions);
                    this.logger.log('NATS Connection created');
                    this.connection.closed().then(() => {
                        this.logger.log('NATS Connection closed');
                    }).catch(e => {
                        this.logger.error(` NATS Connection closing error: ${e}`);
                    }).finally(this.onDisconnect);
                    resolve();
                }
                catch (error) {
                    if (reconnectCounter > nats_2.Reconnect.RECONNECT_ATTEMPTS_LIMIT) {
                        this.logger.error('Reconnection attempts limit was exceed. Call "process.exit(1). Error:', error);
                        reject(error);
                        this.onDisconnect();
                    }
                    this.logger.error(`NATS Connection Error: ${error}`);
                    reconnectTimeout = this.calculateReconnectTimeout(reconnectTimeout);
                    setTimeout(pollConnect, reconnectTimeout);
                }
            };
            pollConnect();
        });
    }
    async getOrCreateConnection() {
        if (!this.connection) {
            await this.connectToNats();
        }
        return this.connection;
    }
}
exports.default = ConnectionCreator;
