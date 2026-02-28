const BACKEND_URL = 'https://trading-mini-app-production.up.railway.app';

fetch(BACKEND_URL + '/api/market/summary')
  .then(response => response.json())
  .then(data => {
    console.log('SUKSES:', data);
    document.body.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
  })
  .catch(error => {
    console.error('GAGAL:', error);
    document.body.innerHTML = 'Error: ' + error.message;
  });