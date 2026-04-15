// Real-time Dashboard Logic
const logStream = document.getElementById('log-stream');
const alertList = document.getElementById('alert-list');
const totalSeqEl = document.getElementById('total-seq');
const threatCountEl = document.getElementById('threat-count');
const confidenceValEl = document.getElementById('confidence-val');

let totalSequences = 0;
let threatCount = 0;

// Update time
setInterval(() => {
    document.getElementById('current-time').innerText = new Date().toLocaleTimeString();
}, 1000);

// Function to add a log entry
function addLog(content, status = 'none') {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const ts = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    entry.innerHTML = `
        <span class="log-ts">${ts}</span>
        <span class="log-content">${content}</span>
    `;
    
    logStream.prepend(entry);
    
    // Limits
    if (logStream.children.length > 100) {
        logStream.removeChild(logStream.lastChild);
    }
    
    totalSequences++;
    totalSeqEl.innerText = totalSequences.toLocaleString();
}

// Function to add an alert
function addAlert(lvl, reason, line) {
    const card = document.createElement('div');
    card.className = 'alert-card';
    const ts = new Date().toLocaleTimeString();
    
    card.innerHTML = `
        <div class="alert-header">
            <span>[${lvl}] DEFENSE TRIGGERED</span>
            <span>${ts}</span>
        </div>
        <div class="alert-body">${line}</div>
        <div class="alert-meta">Reason: ${reason}</div>
    `;
    
    alertList.prepend(card);
    
    if (alertList.children.length > 10) {
        alertList.removeChild(alertList.lastChild);
    }
    
    threatCount++;
    threatCountEl.innerText = threatCount;
}

// Simulated data loop (will be replaced by real data fetch)
function simulate() {
    const samples = [
        "sshd[2245]: Accepted password for root from 192.168.1.15",
        "sshd[2245]: pam_unix(sshd:session): session opened for user root",
        "systemd[1]: Started Session 12 of user root.",
        "CRON[3312]: (root) CMD (run-parts /etc/cron.hourly)",
        "kernel: [122.4] eth0: link up, 1000Mbps",
        "sshd[4567]: Invalid user admin from 45.33.1.22",
        "sshd[4567]: pam_unix(sshd:auth): authentication failure; UID=0",
        "sshd[8891]: Failed password for root from 211.4.5.122 port 54321"
    ];

    const randomLog = samples[Math.floor(Math.random() * samples.length)];
    addLog(randomLog);
    
    if (randomLog.includes("Invalid") || randomLog.includes("Failed")) {
        if (Math.random() > 0.5) {
            addAlert("HIGH", "Multiple Auth Failures", randomLog);
        }
    }
    
    setTimeout(simulate, 1000 + Math.random() * 2000);
}

// Polling for real data
async function pollData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) return;
        const data = await response.json();
        
        // If data has new alerts/logs, update UI
        if (data.new_log) addLog(data.new_log);
        if (data.new_alert) addAlert(data.new_alert.level, data.new_alert.reason, data.new_alert.line);
        
        confidenceValEl.innerText = (data.confidence || 94.2) + '%';
        
    } catch (e) {
        // Silently fail if data.json not yet available
    }
}

// Uncomment to enable real polling
// setInterval(pollData, 1000);

simulate();
