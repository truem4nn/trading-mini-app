// Inisialisasi Telegram WebApp
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Konstanta
const BACKEND_URL = 'https://trading-mini-app-production.up.railway.app'; 
const userId = tg.initDataUnsafe?.user?.id || 0;

// State
let currentView = 'dashboard';
let chatHistory = [];

// Fungsi utilitas untuk fetch API
async function apiGet(endpoint) {
    const res = await fetch(`${BACKEND_URL}/api${endpoint}`);
    return res.json();
}

async function apiPost(endpoint, body) {
    const res = await fetch(`${BACKEND_URL}/api${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return res.json();
}

// Render view
function showView(view) {
    currentView = view;
    const content = document.getElementById('content');
    content.innerHTML = '<div class="loader">Memuat...</div>';
    
    if (view === 'dashboard') renderDashboard();
    else if (view === 'prices') renderPrices();
    else if (view === 'orderbook') renderOrderBookForm();
    else if (view === 'chat') renderChat();
    else if (view === 'account') renderAccount();
}

// DASHBOARD
async function renderDashboard() {
    const content = document.getElementById('content');
    content.innerHTML = '<div class="loader">Mengambil data pasar...</div>';
    
    const data = await apiGet('/market/summary');
    let html = '<h2>📈 Ringkasan Pasar</h2>';
    
    for (const [pair, ticker] of Object.entries(data)) {
        const change = parseFloat(ticker.change_percentage);
        const changeClass = change >= 0 ? 'price-up' : 'price-down';
        const pairDisplay = pair.replace('_', '/');
        html += `
            <div class="card">
                <strong>${pairDisplay}</strong><br>
                Harga: $${ticker.last} 
                <span class="${changeClass}">(${change > 0 ? '+' : ''}${change}%)</span>
            </div>
        `;
    }
    content.innerHTML = html;
}

// HARGA LENGKAP
async function renderPrices() {
    const content = document.getElementById('content');
    content.innerHTML = '<div class="loader">Memuat harga...</div>';
    
    const pairs = ['BTC_USDT', 'ETH_USDT', 'BNB_USDT', 'SOL_USDT', 'XRP_USDT', 'ADA_USDT', 'DOGE_USDT'];
    let html = '<h2>💰 Harga Spot</h2>';
    
    for (const pair of pairs) {
        const data = await apiGet(`/ticker/${pair}`);
        if (data && data[0]) {
            const t = data[0];
            const change = parseFloat(t.change_percentage);
            const changeClass = change >= 0 ? 'price-up' : 'price-down';
            const pairDisplay = pair.replace('_', '/');
            html += `
                <div class="card">
                    <strong>${pairDisplay}</strong><br>
                    Harga: $${t.last}<br>
                    Perubahan 24j: <span class="${changeClass}">${change > 0 ? '+' : ''}${change}%</span>
                </div>
            `;
        }
    }
    content.innerHTML = html;
}

// ORDER BOOK
function renderOrderBookForm() {
    const html = `
        <h2>📚 Order Book</h2>
        <div class="card">
            <select id="pairSelect">
                <option value="BTC_USDT">BTC/USDT</option>
                <option value="ETH_USDT">ETH/USDT</option>
                <option value="BNB_USDT">BNB/USDT</option>
                <option value="SOL_USDT">SOL/USDT</option>
            </select>
            <button onclick="loadOrderBook()">Lihat</button>
        </div>
        <div id="obResult"></div>
    `;
    document.getElementById('content').innerHTML = html;
}

window.loadOrderBook = async function() {
    const pair = document.getElementById('pairSelect').value;
    const data = await apiGet(`/orderbook/${pair}?limit=5`);
    const pairDisplay = pair.replace('_', '/');
    let html = `<div class="card"><h3>${pairDisplay}</h3>`;
    html += '<h4>🔵 Bids (Beli)</h4><ul>';
    data.bids?.forEach(b => html += `<li>${b[0]} — ${b[1]}</li>`);
    html += '</ul><h4>🔴 Asks (Jual)</h4><ul>';
    data.asks?.forEach(a => html += `<li>${a[0]} — ${a[1]}</li>`);
    html += '</ul></div>';
    document.getElementById('obResult').innerHTML = html;
};

// CHAT AI
function renderChat() {
    chatHistory = [];
    const html = `
        <h2>💬 Tanya AI</h2>
        <div class="card">
            <div id="chatMessages" class="chat-box"></div>
            <input type="text" id="chatInput" placeholder="Ketik pertanyaan..." />
            <button onclick="sendChatMessage()">Kirim</button>
        </div>
    `;
    document.getElementById('content').innerHTML = html;
}

window.sendChatMessage = async function() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    
    const chatDiv = document.getElementById('chatMessages');
    chatDiv.innerHTML += `<div class="chat-message-user"><b>Anda:</b> ${msg}</div>`;
    input.value = '';
    
    const res = await apiPost('/chat', {
        message: msg,
        user_id: userId,
        history: chatHistory
    });
    
    chatDiv.innerHTML += `<div class="chat-message-ai"><b>AI:</b> ${res.response}</div>`;
    chatHistory.push({ role: 'user', content: msg });
    chatHistory.push({ role: 'assistant', content: res.response });
    chatDiv.scrollTop = chatDiv.scrollHeight;
};

// AKUN (hanya info, karena API Key tidak disimpan di frontend)
function renderAccount() {
    const html = `
        <h2>🔐 Akun Gate.io</h2>
        <div class="card">
            <p>Fitur ini memerlukan API Key yang disimpan di backend. Hubungi admin untuk mengaktifkan.</p>
            <p>Atau gunakan bot chat untuk cek saldo via perintah.</p>
        </div>
    `;
    document.getElementById('content').innerHTML = html;
}

// Muat dashboard saat pertama kali
showView('dashboard');