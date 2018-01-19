const fs = require('fs');
const access = fs.createWriteStream('log/proxy.log', {flags: 'a+', mode: 0o666});
process.stdout.write = process.stderr.write = access.write.bind(access);
process.on('uncaughtException', function(err) {
  console.error((err && err.stack) ? err.stack : err);
});


const https = require('https'),
      ProxyChain = require('proxy-chain');

const config = require('./config');


function* makeRing(arr) {
  let i = 0;
  while(true) {
    yield arr[i];
    i = ++i % arr.length;
  }
}


function runServer(proxies) {
  let server = new ProxyChain.Server({
    port: 5050,
    verbose: true,
    prepareRequestFunction: () => {
      return {
        requestAuthentication: false,
        upstreamProxyUrl: proxies.next().value,
      };
    },
  });
  server.listen();
}


https.get(config.proxy6_api_url, (resp) => {
  let data = '';
  resp.on('data', (chunk) => {
    data += chunk;
  });

  resp.on('end', () => {
    let proxies = [];
    for (let [key, value] of Object.entries(JSON.parse(data).list)) {
      let url = value.type + '://' + value.user + ':' + value.pass + '@' + value.host + ':' + value.port;
      proxies.push(url);
    }
    let proxyRing = makeRing(proxies);
    runServer(proxyRing);
  });
});
