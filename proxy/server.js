var rufus = require('rufus');
rufus.addHandler(new rufus.handlers.File('log/proxy.log'));
rufus.console();
rufus.handleExceptions(false);
const logger = rufus.getLogger('server');

const https = require('https'),
      ProxyChain = require('proxy-chain');

const config = require('./config');
var proxiesIPv4 = [];
var proxiesIPv6 = [];

function* proxyIPv4Ring() {
  let i = -1;
  while(true) {
    // To prevent RangeError if proxies has been changed
    let currentProxies = proxiesIPv4;
    yield currentProxies[i = (i + 1) % currentProxies.length];
  }
}

function* proxyIPv6Ring() {
  let i = -1;
  while(true) {
    // To prevent RangeError if proxies has been changed
    let currentProxies = proxiesIPv6;
    yield currentProxies[i = (i + 1) % currentProxies.length];
  }
}

function runServer(port, ring) {
  let server = new ProxyChain.Server({
    port: port,
    verbose: false,
    prepareRequestFunction: () => {
      return {
        requestAuthentication: false,
        upstreamProxyUrl: ring.next().value,
      };
    },
  });
  server.listen();
}

function updateProxies() {
  https.get(config.proxy6_api_url, (resp) => {
    let data = '';
    resp.on('data', (chunk) => {
      data += chunk;
    });

    resp.on('end', () => {
      let newProxiesIPv4 = [];
      let newProxiesIPv6 = [];
      for (let value of Object.values(JSON.parse(data).list)) {
        if (value.type === 'http') {
          let url = value.type + '://' + value.user + ':' + value.pass + '@' + value.host + ':' + value.port;
          if (value.ip.indexOf(':') > -1) {
            newProxiesIPv6.push(url);
          } else {
            newProxiesIPv4.push(url);
          }
        }
      }
      proxiesIPv4 = newProxiesIPv4;
      proxiesIPv6 = newProxiesIPv6;
    });
  });
}
//
updateProxies();
runServer(8080, proxyIPv4Ring());
logger.info('Server[8080]: Listening...');
runServer(5050, proxyIPv6Ring());
logger.info('Server[5050]: Listening...');
// Every 10 minutes
setInterval(updateProxies, 600000);
