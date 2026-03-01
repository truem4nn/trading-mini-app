const BACKEND_URL = 'http://trading-mini-app.railway-internal:8000';
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