var config = {};
config.proxy6_api_url = 'https://proxy6.net/api/<API_KEY>/getproxy/?state=active';

try {
  Object.assign(config, require('./config_prod'));
} catch (e) {}

module.exports = config;
