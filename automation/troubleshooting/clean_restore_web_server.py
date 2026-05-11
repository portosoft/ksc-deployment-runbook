import paramiko
import os
import sys
import base64

def clean_restore_web_server(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        target_file = "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        
        # Cleaned version (No DEBUG logs)
        clean_content = """\"use strict\";
Object.defineProperty(exports, \"__esModule\", { value: true });
exports.WebServer = void 0;
const parse_env_variable_1 = require(\"../../utils/parse-env-variable\");
const config_1 = require(\"../iam-integration/config\");
const web_server_1 = require(\"../web-server\");
const routes_1 = require(\"../web-server/routes\");
const loginRequests_1 = require(\"./loginRequests\");
class WebServer extends web_server_1.WebServer {
    constructor() {
        super();
        this.serversCount = 0;
        super.useExpressStaticFiles();
        try {
            if (Array.isArray(global.config.openAPIServers.pools)) {
                for (const pool of global.config.openAPIServers.pools) {
                    if (Array.isArray(pool.servers)) {
                        this.serversCount += pool.servers.length;
                    }
                }
            }
        }
        catch (err) {
            runtime.logger.error('An error occurred while counting servers:', err);
        }
    }
    get publicRoutes() {
        const routes = [
            this.loginPath,
            routes_1.allRoutes.ssoLoginPath,
            routes_1.publicRoutes.formsScriptPath,
            routes_1.publicRoutes.getSecretPath,
            routes_1.publicRoutes.saveUserSecretPath,
            routes_1.publicRoutes.totpAuthorizationErrorPath,
            routes_1.publicRoutes.l10nRegExp,
            routes_1.publicRoutes.pluginBundleRegExp,
            ...routes_1.pluginPublicRoutes,
            '/servers-ids',
            '/service-authentication',
            '/service-logout',
            '/reactive-tests/',
            config_1.iamIntegrationConfig.nwc.redirectPath,
            config_1.iamIntegrationConfig.nwc.backchannelLogout,
        ];
        return routes;
    }
    attachBasicRoutes(app) {
        app
            .route(routes_1.allRoutes.ssoLoginPath)
            .get((req, res) => {
            if (this.getAuthCookie(req, res)) {
                res.redirect(routes_1.allRoutes.changeAccountPath);
                return;
            }
            this.createClientSsoSession({
                request: req,
                response: res
            });
        });
    }
    getSelectedServer(req) {
        const selectedServerId = req.query.selected_server;
        let selectedServer;
        if (this.serversCount === 1) {
            for (const pool of global.config.openAPIServers.pools) {
                if (pool.servers.length) {
                    selectedServer = pool.servers[0];
                    break;
                }
            }
        }
        else if (selectedServerId) {
            selectedServer = global.config.openAPIServers.pools
                .flatMap((pool) => pool.servers)
                .find((serverInfo) => serverInfo.id === selectedServerId);
        }
        return selectedServer;
    }
    showServerSelectionErrorPage(res) {
        res.render('private/error-iam', {
            error: {
                l10n: {
                    title: 'serverSelection.errorPage.title',
                    message: 'serverSelection.errorPage.description'
                },
                interceptorLink: {
                    product: 'ksc',
                    version: 16.0
                }
            }
        });
    }
    async handleLoginRequest(req, res) {
        var _a, _b;
        runtime.logger.log('Checking IDM is installed');
        if ((_b = (_a = global.config) === null || _a === void 0 ? void 0 : _a.idm) === null || _b === void 0 ? void 0 : _b.isInstalled) {
            await (0, loginRequests_1.idmAuth)({
                req,
                res,
                callback: () => {
                    if (!this.serversCount) {
                        this.showServerSelectionErrorPage(res);
                    }
                    else {
                        this.showLoginPage({
                            req,
                            res,
                            params: {
                                selectedServer: this.getSelectedServer(req)
                            }
                        });
                    }
                }
            });
        }
        else {
            runtime.logger.log('No IDM is installed. Checking XDR configuration');
            const selectedServer = this.getSelectedServer(req);
            const isIamServer = Boolean(selectedServer === null || selectedServer === void 0 ? void 0 : selectedServer.isIAM);
            const shouldUseIamAuth = isIamServer || ((0, parse_env_variable_1.parseEnvVariable)('IS_XDR') && (0, parse_env_variable_1.parseEnvVariable)('USE_IAM'));
            req.query.selected_server = selectedServer === null || selectedServer === void 0 ? void 0 : selectedServer.id;
            if (shouldUseIamAuth) {
                (0, loginRequests_1.xdrAuth)({
                    req,
                    res
                });
            }
            else {
                runtime.logger.log('IS_XDR or USE_IAM are not set. Redirect to default login page.');
                if (!this.serversCount) {
                    this.showServerSelectionErrorPage(res);
                }
                else {
                    this.showLoginPage({
                        req,
                        res,
                        params: {
                            selectedServer
                        }
                    });
                }
            }
        }
    }
    async createClientSsoSession({ request, response }) {
        const negotiationResult = await global.sessionManager.performSsoNegotiation({
            request,
            response
        });
        if (!negotiationResult.completed) {
            if (negotiationResult.isShowErrorPage) {
                const localizationService = await runtime.get(services.localization);
                const localizedTitle = localizationService.get(errors.session.DOMAIN_AUTH.title);
                const localizedMessage = localizationService.get(errors.session.DOMAIN_AUTH.message);
                const localizedLinkText = localizationService.get(errors.session.DOMAIN_AUTH.linkText);
                response.render('public/info', {
                    loginUrl: routes_1.publicRoutes.loginPath,
                    linkText: localizedLinkText,
                    isLoginByCredentialsVisible: true,
                    error: {
                        title: localizedTitle,
                        message: localizedMessage
                    }
                });
            }
            else {
                response.status(negotiationResult.status);
                response.end();
            }
        }
        else {
            response.redirect('/');
        }
    }
}
exports.WebServer = WebServer;
"""
        
        # Write back
        b64_content = base64.b64encode(clean_content.encode('utf-8')).decode('utf-8')
        print("--- Writing clean restored file ---")
        client.exec_command(f"echo '{b64_content}' > /tmp/web-server-clean.txt")
        client.exec_command(f"base64 -d /tmp/web-server-clean.txt > /tmp/web-server-fixed.js")
        stdin, stdout, stderr = client.exec_command(f"sudo -S cp /tmp/web-server-fixed.js {target_file}")
        stdin.write(password + '\n')
        stdin.flush()
        
        # Restart
        print("--- Restarting ---")
        client.exec_command("sudo -S killall -9 node")
        client.exec_command("sudo -S systemctl restart KSCWebConsole.service")
        stdin.write(password + '\n')
        stdin.flush()
        
        print("Done!")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    clean_restore_web_server(host, user, password)
