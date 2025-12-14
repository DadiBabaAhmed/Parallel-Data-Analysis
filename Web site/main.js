
// Fonctions utilitaires
function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// Données de simulation
const performanceData = {
    mapreduce: { baseTime: 120, efficiency: 0.7, overhead: 0.15 },
    spark: { baseTime: 80, efficiency: 0.85, overhead: 0.08 },
    mpi: { baseTime: 60, efficiency: 0.9, overhead: 0.05 }
};

// Variables de simulation
let simulationRunning = false;
let simulationInterval = null;

// Initialisation des graphiques
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    updateSimulation();
    // Fetch cluster hosts and recent results for the UI
    fetchHosts();
    fetchResults();
    fetchInputFiles();
    fetchJobs();
});

// Base URL for the local API server
const API_BASE = 'http://localhost:5000';

async function fetchHosts() {
    try {
        const res = await fetch(`${API_BASE}/api/hosts`);
        const hosts = await res.json();
        const containerList = document.getElementById('hostsList');
        containerList.innerHTML = '';
        hosts.forEach(h => {
            const a = document.createElement('a');
            a.href = h.url;
            a.target = '_blank';
            a.rel = 'noreferrer noopener';
            a.className = 'block text-blue-600 hover:underline';
            a.textContent = `${h.name} — ${h.url}`;
            containerList.appendChild(a);
        });
    } catch (err) {
        const containerList = document.getElementById('hostsList');
        containerList.innerHTML = '<div class="text-red-600">Impossible de contacter l\'API (run `make run-api`)</div>';
        console.error('fetchHosts error', err);
    }
}

async function fetchResults() {
    const resultsArea = document.getElementById('resultsArea');
    resultsArea.innerHTML = '<div class="text-sm text-gray-500">Chargement...</div>';
    try {
        const res = await fetch(`${API_BASE}/api/results`);
        const data = await res.json();
        
        const wrapper = document.createElement('div');
        wrapper.className = 'space-y-6';

        // Graphs Section
        const graphsSection = document.createElement('div');
        const gTitle = document.createElement('h5');
        gTitle.className = 'font-semibold mb-3';
        gTitle.textContent = 'Graphiques';
        graphsSection.appendChild(gTitle);
        const grid = document.createElement('div');
        grid.className = 'grid md:grid-cols-3 gap-4';
        
        if (data.graphs && data.graphs.length) {
            data.graphs.slice().reverse().forEach(name => {
                const card = document.createElement('div');
                card.className = 'bg-gray-50 p-3 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors';
                card.onclick = () => showImage(name);
                const img = document.createElement('img');
                img.src = `${API_BASE}/api/graphs/${encodeURIComponent(name)}`;
                img.alt = name;
                img.className = 'w-full h-40 object-contain rounded';
                const caption = document.createElement('div');
                caption.className = 'text-sm text-gray-700 mt-2';
                caption.textContent = name;
                card.appendChild(img);
                card.appendChild(caption);
                grid.appendChild(card);
            });
        } else {
            grid.innerHTML = '<div class="text-sm text-gray-500">Aucun graphique trouvé.</div>';
        }
        graphsSection.appendChild(grid);
        wrapper.appendChild(graphsSection);

        // Statistics / JSON Section
        const statsSection = document.createElement('div');
        const sTitle = document.createElement('h5');
        sTitle.className = 'font-semibold mb-3';
        sTitle.textContent = 'Fichiers de Statistiques (JSON)';
        statsSection.appendChild(sTitle);
        const list = document.createElement('div');
        list.className = 'space-y-2';
        
        if (data.statistics && data.statistics.length) {
            data.statistics.slice().reverse().forEach(name => {
                const row = document.createElement('div');
                row.className = 'flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors';
                
                const left = document.createElement('div');
                left.className = 'text-sm text-gray-800';
                left.textContent = name;
                
                const right = document.createElement('div');
                right.className = 'flex gap-2';
                
                const viewBtn = document.createElement('button');
                viewBtn.className = 'text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors';
                viewBtn.textContent = 'Voir';
                viewBtn.onclick = async () => {
                    await showFile(name);
                };
                
                const dlBtn = document.createElement('a');
                dlBtn.className = 'text-sm text-gray-600 px-3 py-1 hover:text-gray-900 transition-colors';
                dlBtn.href = `${API_BASE}/api/download?category=statistics&name=${encodeURIComponent(name)}`;
                dlBtn.textContent = 'Télécharger';
                dlBtn.target = '_blank';
                
                right.appendChild(viewBtn);
                right.appendChild(dlBtn);
                row.appendChild(left);
                row.appendChild(right);
                list.appendChild(row);
            });
        } else {
            list.innerHTML = '<div class="text-sm text-gray-500">Aucun fichier de statistiques trouvé.</div>';
        }
        statsSection.appendChild(list);
        wrapper.appendChild(statsSection);

        // General Files Section (CSV, TXT, etc.)
        const genSection = document.createElement('div');
        const genTitle = document.createElement('h5');
        genTitle.className = 'font-semibold mb-3';
        genTitle.textContent = 'Autres Fichiers';
        genSection.appendChild(genTitle);
        const genList = document.createElement('div');
        genList.className = 'space-y-2';
        
        if (data.general && data.general.length) {
            data.general.slice().reverse().forEach(name => {
                const row = document.createElement('div');
                row.className = 'flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors';
                
                const left = document.createElement('div');
                left.className = 'text-sm text-gray-800 flex items-center gap-2';
                
                // Add file type badge
                const ext = name.split('.').pop().toLowerCase();
                const badge = document.createElement('span');
                badge.className = 'text-xs px-2 py-0.5 rounded font-medium';
                
                if (ext === 'csv') {
                    badge.className += ' bg-green-100 text-green-700';
                    badge.textContent = 'CSV';
                } else if (['txt', 'log', 'md'].includes(ext)) {
                    badge.className += ' bg-blue-100 text-blue-700';
                    badge.textContent = 'TXT';
                } else {
                    badge.className += ' bg-gray-200 text-gray-700';
                    badge.textContent = ext.toUpperCase();
                }
                
                const fileName = document.createElement('span');
                fileName.textContent = name;
                
                left.appendChild(badge);
                left.appendChild(fileName);
                
                const right = document.createElement('div');
                right.className = 'flex gap-2';
                
                // Add "View" button for viewable file types
                const viewableExtensions = ['csv', 'txt', 'log', 'md', 'json'];
                if (viewableExtensions.includes(ext)) {
                    const viewBtn = document.createElement('button');
                    viewBtn.className = 'text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors';
                    viewBtn.textContent = 'Voir';
                    viewBtn.onclick = async () => {
                        await showFile(name);
                    };
                    right.appendChild(viewBtn);
                }
                
                const dl = document.createElement('a');
                dl.className = 'text-sm text-gray-600 px-3 py-1 hover:text-gray-900 transition-colors';
                dl.href = `${API_BASE}/api/download?category=general&name=${encodeURIComponent(name)}`;
                dl.target = '_blank';
                dl.textContent = 'Télécharger';
                
                right.appendChild(dl);
                row.appendChild(left);
                row.appendChild(right);
                genList.appendChild(row);
            });
        } else {
            genList.innerHTML = '<div class="text-sm text-gray-500">Aucun fichier trouvé.</div>';
        }
        genSection.appendChild(genList);
        wrapper.appendChild(genSection);

        resultsArea.innerHTML = '';
        resultsArea.appendChild(wrapper);
    } catch (err) {
        resultsArea.innerHTML = '<div class="text-red-600 bg-red-50 border border-red-200 rounded p-4">Erreur lors de la récupération des résultats. Assurez-vous que l\'API est démarrée (`make run-api`).</div>';
        console.error('fetchResults error', err);
    }
}

async function showFile(name) {
    const modalId = 'jsonModal';
    
    // Create or reuse modal
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        const inner = document.createElement('div');
        inner.className = 'bg-white w-11/12 md:w-3/4 p-6 rounded-lg overflow-auto max-h-[80vh]';
        inner.id = modalId + '-inner';
        modal.appendChild(inner);
        document.body.appendChild(modal);
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    }

    const inner = document.getElementById(modalId + '-inner');
    inner.innerHTML = '<div class="text-sm text-gray-600">Chargement...</div>';

    try {
        const ext = (name || '').split('.').pop().toLowerCase();
        const url = `${API_BASE}/api/download?category=statistics&name=${encodeURIComponent(name)}`;
        const res = await fetch(url);
        
        if (!res.ok) {
            throw new Error(`Erreur HTTP ${res.status}: ${res.statusText}`);
        }
        
        const contentType = (res.headers.get('content-type') || '').toLowerCase();

        // Helper to render modal header with title and close button
        function renderHeader() {
            inner.innerHTML = '';
            const header = document.createElement('div');
            header.className = 'flex justify-between items-center mb-4 pb-2 border-b';
            
            const title = document.createElement('h4');
            title.className = 'font-semibold text-lg';
            title.textContent = name;
            
            const close = document.createElement('button');
            close.className = 'text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded hover:bg-gray-100';
            close.textContent = '✕ Fermer';
            close.onclick = () => modal.remove();
            
            header.appendChild(title);
            header.appendChild(close);
            inner.appendChild(header);
        }

        // Helper to parse CSV properly (handles quoted fields)
        function parseCSV(text) {
            const rows = [];
            let currentRow = [];
            let currentField = '';
            let inQuotes = false;
            
            for (let i = 0; i < text.length; i++) {
                const char = text[i];
                const nextChar = text[i + 1];
                
                if (char === '"') {
                    if (inQuotes && nextChar === '"') {
                        currentField += '"';
                        i++; // Skip next quote
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (char === ',' && !inQuotes) {
                    currentRow.push(currentField);
                    currentField = '';
                } else if ((char === '\n' || char === '\r') && !inQuotes) {
                    if (char === '\r' && nextChar === '\n') {
                        i++; // Skip \n in \r\n
                    }
                    if (currentField || currentRow.length > 0) {
                        currentRow.push(currentField);
                        rows.push(currentRow);
                        currentRow = [];
                        currentField = '';
                    }
                } else {
                    currentField += char;
                }
            }
            
            // Add last field and row if any
            if (currentField || currentRow.length > 0) {
                currentRow.push(currentField);
                rows.push(currentRow);
            }
            
            return rows.filter(row => row.length > 0 && row.some(cell => cell.trim()));
        }

        // JSON Handler
        if (ext === 'json' || contentType.includes('application/json')) {
            const data = await res.json();
            renderHeader();
            
            const pre = document.createElement('pre');
            pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[60vh]';
            pre.textContent = JSON.stringify(data, null, 2);
            inner.appendChild(pre);
            return;
        }

        // CSV Handler
        if (ext === 'csv' || contentType.includes('text/csv') || contentType.includes('application/csv')) {
            const text = await res.text();
            
            if (!text.trim()) {
                renderHeader();
                inner.innerHTML += '<div class="text-gray-600 text-sm">Le fichier CSV est vide.</div>';
                return;
            }
            
            renderHeader();
            
            try {
                const rows = parseCSV(text);
                
                if (rows.length === 0) {
                    inner.innerHTML += '<div class="text-gray-600 text-sm">Aucune donnée trouvée dans le fichier CSV.</div>';
                    return;
                }
                
                // Render as table for reasonable sizes
                if (rows.length <= 500) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'overflow-auto max-h-[60vh] border rounded';
                    
                    const table = document.createElement('table');
                    table.className = 'min-w-full text-sm border-collapse';
                    
                    // Header row
                    const thead = document.createElement('thead');
                    thead.className = 'bg-gray-50 sticky top-0';
                    const headerRow = document.createElement('tr');
                    rows[0].forEach((header, idx) => {
                        const th = document.createElement('th');
                        th.className = 'px-3 py-2 text-left font-semibold text-gray-700 border-b border-r';
                        th.textContent = header || `Colonne ${idx + 1}`;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);
                    table.appendChild(thead);
                    
                    // Data rows
                    const tbody = document.createElement('tbody');
                    rows.slice(1).forEach((row, rowIdx) => {
                        const tr = document.createElement('tr');
                        tr.className = rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50';
                        
                        row.forEach(cell => {
                            const td = document.createElement('td');
                            td.className = 'px-3 py-2 border-b border-r text-gray-800';
                            td.textContent = cell;
                            tr.appendChild(td);
                        });
                        tbody.appendChild(tr);
                    });
                    table.appendChild(tbody);
                    
                    wrapper.appendChild(table);
                    inner.appendChild(wrapper);
                    
                    // Add row count info
                    const info = document.createElement('div');
                    info.className = 'text-xs text-gray-600 mt-2';
                    info.textContent = `${rows.length - 1} ligne(s) de données`;
                    inner.appendChild(info);
                } else {
                    // Too large, show as text with warning
                    const warning = document.createElement('div');
                    warning.className = 'bg-yellow-50 border border-yellow-200 rounded p-3 mb-3 text-sm';
                    warning.textContent = `Fichier volumineux (${rows.length} lignes). Affichage en mode texte.`;
                    inner.appendChild(warning);
                    
                    const pre = document.createElement('pre');
                    pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[55vh]';
                    pre.textContent = text;
                    inner.appendChild(pre);
                }
            } catch (parseError) {
                console.error('CSV parsing error:', parseError);
                // Fallback to plain text
                const pre = document.createElement('pre');
                pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[60vh]';
                pre.textContent = text;
                inner.appendChild(pre);
            }
            return;
        }

        // Plain Text Handler
        if (contentType.startsWith('text/') || ['txt', 'log', 'md'].includes(ext)) {
            const text = await res.text();
            
            if (!text.trim()) {
                renderHeader();
                inner.innerHTML += '<div class="text-gray-600 text-sm">Le fichier texte est vide.</div>';
                return;
            }
            
            renderHeader();
            
            const pre = document.createElement('pre');
            pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[60vh] whitespace-pre-wrap';
            pre.textContent = text;
            inner.appendChild(pre);
            return;
        }

        // Image Handler
        if (contentType.startsWith('image/') || ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(ext)) {
            const blob = await res.blob();
            const imgURL = URL.createObjectURL(blob);
            
            renderHeader();
            
            const container = document.createElement('div');
            container.className = 'flex items-center justify-center bg-gray-50 rounded p-4';
            container.style.maxHeight = '65vh';
            
            const img = document.createElement('img');
            img.src = imgURL;
            img.alt = name;
            img.className = 'max-w-full max-h-full h-auto rounded shadow-lg';
            img.onload = () => URL.revokeObjectURL(imgURL); // Clean up
            
            container.appendChild(img);
            inner.appendChild(container);
            return;
        }

        // Fallback for unsupported file types
        renderHeader();
        const fallback = document.createElement('div');
        fallback.className = 'bg-gray-50 border border-gray-200 rounded p-4 text-sm';
        fallback.innerHTML = `
            <p class="mb-2">Type de fichier non affichable : <strong>${contentType || ext}</strong></p>
            <a class="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" 
               href="${url}" 
               download="${name}">
                Télécharger le fichier
            </a>
        `;
        inner.appendChild(fallback);

    } catch (err) {
        inner.innerHTML = `
            <div class="text-red-600 bg-red-50 border border-red-200 rounded p-4">
                <strong>Erreur:</strong> ${err.message || 'Impossible de charger le fichier.'}
            </div>
        `;
        console.error('showFile error:', err);
    }
}

async function fetchInputFiles() {
    try {
        const res = await fetch(`${API_BASE}/api/input-files`);
        const data = await res.json();
        const sel = document.getElementById('inputFileSelect');
        sel.innerHTML = '';
        if (data.files && data.files.length) {
            data.files.forEach(f => {
                const opt = document.createElement('option');
                opt.value = f;
                opt.textContent = f;
                sel.appendChild(opt);
            });
        } else {
            const opt = document.createElement('option');
            opt.textContent = 'Aucun fichier trouvé';
            sel.appendChild(opt);
        }
    } catch (err) {
        console.error('fetchInputFiles error', err);
        const sel = document.getElementById('inputFileSelect');
        sel.innerHTML = '<option>Erreur</option>';
    }
}

async function fetchJobs() {
    try {
        const res = await fetch(`${API_BASE}/api/jobs`);
        const data = await res.json();
        const jobsArea = document.getElementById('jobsListArea');
        if (!jobsArea) return; // Element may not exist in all pages
        
        jobsArea.innerHTML = '';
        if (data.jobs && data.jobs.length > 0) {
            const wrapper = document.createElement('div');
            wrapper.className = 'space-y-2';
            
            // Sort jobs by created_at descending
            const sortedJobs = data.jobs.sort((a, b) => {
                return new Date(b.created_at) - new Date(a.created_at);
            });
            
            sortedJobs.forEach(job => {
                const jobCard = document.createElement('div');
                jobCard.className = 'p-3 bg-gray-50 rounded border border-gray-200';
                
                const header = document.createElement('div');
                header.className = 'flex justify-between items-start mb-2';
                
                const jobInfo = document.createElement('div');
                jobInfo.className = 'text-sm';
                jobInfo.innerHTML = `
                    <div class="font-semibold">${job.id}</div>
                    <div class="text-gray-600">File: ${job.filename}</div>
                    <div class="text-gray-600">Analysis: ${job.analysis}</div>
                `;
                
                const statusBadge = document.createElement('span');
                statusBadge.className = `px-2 py-1 text-xs rounded ${getStatusClass(job.status)}`;
                statusBadge.textContent = job.status;
                
                header.appendChild(jobInfo);
                header.appendChild(statusBadge);
                
                const actions = document.createElement('div');
                actions.className = 'flex gap-2 mt-2';
                
                const viewLogsBtn = document.createElement('button');
                viewLogsBtn.className = 'text-xs bg-gray-600 text-white px-2 py-1 rounded';
                viewLogsBtn.textContent = 'Voir Logs';
                viewLogsBtn.onclick = () => showJobLogs(job.id);
                
                const refreshBtn = document.createElement('button');
                refreshBtn.className = 'text-xs bg-blue-600 text-white px-2 py-1 rounded';
                refreshBtn.textContent = 'Rafraîchir';
                refreshBtn.onclick = () => refreshJobStatus(job.id);
                
                actions.appendChild(viewLogsBtn);
                actions.appendChild(refreshBtn);
                
                jobCard.appendChild(header);
                jobCard.appendChild(actions);
                wrapper.appendChild(jobCard);
            });
            
            jobsArea.appendChild(wrapper);
        } else {
            jobsArea.innerHTML = '<div class="text-sm text-gray-500">Aucun job en cours</div>';
        }
    } catch (err) {
        console.error('fetchJobs error', err);
    }
}

function getStatusClass(status) {
    switch (status) {
        case 'finished':
            return 'bg-green-100 text-green-800';
        case 'running':
            return 'bg-blue-100 text-blue-800';
        case 'failed':
            return 'bg-red-100 text-red-800';
        case 'queued':
            return 'bg-yellow-100 text-yellow-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

async function refreshJobStatus(job_id) {
    try {
        const res = await fetch(`${API_BASE}/api/job/${encodeURIComponent(job_id)}`);
        const job = await res.json();
        if (job.error) {
            alert(`Erreur: ${job.error}`);
        } else {
            await fetchJobs(); // Refresh the entire jobs list
        }
    } catch (err) {
        console.error('refreshJobStatus error', err);
        alert('Erreur lors de la récupération du statut du job');
    }
}

async function showJobLogs(job_id) {
    const modalId = 'logsModal';
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        const inner = document.createElement('div');
        inner.className = 'bg-white w-11/12 md:w-3/4 p-6 rounded-lg overflow-auto max-h-[80vh]';
        inner.id = modalId + '-inner';
        modal.appendChild(inner);
        document.body.appendChild(modal);
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    }
    
    const inner = document.getElementById(modalId + '-inner');
    inner.innerHTML = '<div class="text-sm text-gray-600">Chargement des logs...</div>';
    
    try {
        const res = await fetch(`${API_BASE}/api/job/${encodeURIComponent(job_id)}/logs`);
        const data = await res.json();
        
        if (data.error) {
            inner.innerHTML = `<div class="text-red-600">Erreur: ${data.error}</div>`;
            return;
        }
        
        const title = document.createElement('div');
        title.className = 'flex justify-between items-center mb-3';
        
        const t = document.createElement('h4');
        t.className = 'font-semibold';
        t.textContent = `Logs: ${job_id}`;
        
        const close = document.createElement('button');
        close.className = 'text-sm text-gray-600';
        close.textContent = 'Fermer';
        close.onclick = () => modal.remove();
        
        title.appendChild(t);
        title.appendChild(close);
        
        const pre = document.createElement('pre');
        pre.className = 'text-xs bg-gray-900 text-green-400 p-4 rounded overflow-auto code-font';
        pre.style.maxHeight = '60vh';
        pre.textContent = data.log || 'Aucun log disponible';
        
        inner.innerHTML = '';
        inner.appendChild(title);
        inner.appendChild(pre);
    } catch (err) {
        inner.innerHTML = '<div class="text-red-600">Impossible de charger les logs.</div>';
        console.error('showJobLogs error', err);
    }
}

async function triggerAnalysis() {
    const sel = document.getElementById('inputFileSelect');
    const file = sel.value;
    const analysis = document.getElementById('analysisType').value;
    const masterInput = document.getElementById('sparkMaster');
    const containerInput = document.getElementById('sparkContainer');
    const statusDiv = document.getElementById('jobStatus');
    
    if (!file || file === 'Aucun fichier trouvé' || file === 'Chargement...') {
        statusDiv.textContent = 'Veuillez sélectionner un fichier d\'entrée valide.';
        return;
    }
    
    statusDiv.textContent = 'Démarrage du job...';
    
    const payload = {
        filename: file,
        analysis: analysis
    };
    
    // Add optional parameters if they exist and have values
    if (masterInput && masterInput.value) {
        payload.master = masterInput.value;
    }
    if (containerInput && containerInput.value) {
        payload.container = containerInput.value;
    }
    
    try {
        const res = await fetch(`${API_BASE}/api/trigger`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.job_id) {
            statusDiv.innerHTML = `Job démarré: <strong>${data.job_id}</strong>`;
            // Start polling
            pollJobStatus(data.job_id);
            // Also refresh the jobs list
            fetchJobs();
        } else {
            statusDiv.textContent = `Erreur: ${data.error || data.detail || 'unknown'}`;
        }
    } catch (err) {
        console.error('triggerAnalysis error', err);
        statusDiv.textContent = 'Erreur lors du démarrage du job. Vérifiez que l\'API est démarrée.';
    }
}

async function pollJobStatus(job_id) {
    const statusDiv = document.getElementById('jobStatus');
    const logsDivId = `jobLogs-${job_id}`;
    // create logs container
    let logsDiv = document.getElementById(logsDivId);
    if (!logsDiv) {
        logsDiv = document.createElement('pre');
        logsDiv.id = logsDivId;
        logsDiv.className = 'mt-3 text-xs bg-gray-900 text-green-400 p-3 rounded code-font max-h-48 overflow-auto';
        statusDiv.parentNode.appendChild(logsDiv);
    }

    let finished = false;
    const poll = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/job/${encodeURIComponent(job_id)}`);
            const info = await res.json();
            if (info.error) {
                statusDiv.textContent = `Erreur: ${info.error}`;
                clearInterval(poll);
                return;
            }
            
            // Update status with badge
            const statusBadge = `<span class="px-2 py-1 text-xs rounded ${getStatusClass(info.status)}">${info.status}</span>`;
            statusDiv.innerHTML = `Job <strong>${job_id}</strong>: ${statusBadge}`;

            // Fetch logs
            const lres = await fetch(`${API_BASE}/api/job/${encodeURIComponent(job_id)}/logs`);
            const logs = await lres.json();
            if (logs.log) {
                logsDiv.textContent = logs.log;
                logsDiv.scrollTop = logsDiv.scrollHeight;
            }

            if (info.status === 'finished' || info.status === 'failed') {
                finished = true;
                clearInterval(poll);
                // Refresh results list when finished
                fetchResults();
                fetchJobs();
                const exitCodeMsg = info.exit_code !== undefined ? ` (exit code: ${info.exit_code})` : '';
                statusDiv.innerHTML += ` — terminé${exitCodeMsg}`;
            }
        } catch (err) {
            console.error('pollJobStatus error', err);
            statusDiv.textContent = 'Erreur lors de la récupération du statut du job.';
            clearInterval(poll);
        }
    }, 2000);
}

async function showFile(name) {
    const modalId = 'jsonModal';
    
    // Create or reuse modal
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        const inner = document.createElement('div');
        inner.className = 'bg-white w-11/12 md:w-3/4 p-6 rounded-lg overflow-auto max-h-[80vh]';
        inner.id = modalId + '-inner';
        modal.appendChild(inner);
        document.body.appendChild(modal);
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    }

    const inner = document.getElementById(modalId + '-inner');
    inner.innerHTML = '<div class="text-sm text-gray-600">Chargement...</div>';

    try {
        const ext = (name || '').split('.').pop().toLowerCase();
        const url = `${API_BASE}/api/download?category=statistics&name=${encodeURIComponent(name)}`;
        const res = await fetch(url);
        
        if (!res.ok) {
            throw new Error(`Erreur HTTP ${res.status}: ${res.statusText}`);
        }
        
        const contentType = (res.headers.get('content-type') || '').toLowerCase();

        // Helper to render modal header with title and close button
        function renderHeader() {
            inner.innerHTML = '';
            const header = document.createElement('div');
            header.className = 'flex justify-between items-center mb-4 pb-2 border-b';
            
            const title = document.createElement('h4');
            title.className = 'font-semibold text-lg';
            title.textContent = name;
            
            const close = document.createElement('button');
            close.className = 'text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded hover:bg-gray-100';
            close.textContent = '✕ Fermer';
            close.onclick = () => modal.remove();
            
            header.appendChild(title);
            header.appendChild(close);
            inner.appendChild(header);
        }

        // Helper to parse CSV properly (handles quoted fields)
        function parseCSV(text) {
            const rows = [];
            let currentRow = [];
            let currentField = '';
            let inQuotes = false;
            
            for (let i = 0; i < text.length; i++) {
                const char = text[i];
                const nextChar = text[i + 1];
                
                if (char === '"') {
                    if (inQuotes && nextChar === '"') {
                        currentField += '"';
                        i++; // Skip next quote
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (char === ',' && !inQuotes) {
                    currentRow.push(currentField);
                    currentField = '';
                } else if ((char === '\n' || char === '\r') && !inQuotes) {
                    if (char === '\r' && nextChar === '\n') {
                        i++; // Skip \n in \r\n
                    }
                    if (currentField || currentRow.length > 0) {
                        currentRow.push(currentField);
                        rows.push(currentRow);
                        currentRow = [];
                        currentField = '';
                    }
                } else {
                    currentField += char;
                }
            }
            
            // Add last field and row if any
            if (currentField || currentRow.length > 0) {
                currentRow.push(currentField);
                rows.push(currentRow);
            }
            
            return rows.filter(row => row.length > 0 && row.some(cell => cell.trim()));
        }

        // JSON Handler
        if (ext === 'json' || contentType.includes('application/json')) {
            const data = await res.json();
            renderHeader();
            
            const pre = document.createElement('pre');
            pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[60vh]';
            pre.textContent = JSON.stringify(data, null, 2);
            inner.appendChild(pre);
            return;
        }

        // CSV Handler
        if (ext === 'csv' || contentType.includes('text/csv') || contentType.includes('application/csv')) {
            const text = await res.text();
            
            if (!text.trim()) {
                renderHeader();
                inner.innerHTML += '<div class="text-gray-600 text-sm">Le fichier CSV est vide.</div>';
                return;
            }
            
            renderHeader();
            
            try {
                const rows = parseCSV(text);
                
                if (rows.length === 0) {
                    inner.innerHTML += '<div class="text-gray-600 text-sm">Aucune donnée trouvée dans le fichier CSV.</div>';
                    return;
                }
                
                // Render as table for reasonable sizes
                if (rows.length <= 500) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'overflow-auto max-h-[60vh] border rounded';
                    
                    const table = document.createElement('table');
                    table.className = 'min-w-full text-sm border-collapse';
                    
                    // Header row
                    const thead = document.createElement('thead');
                    thead.className = 'bg-gray-50 sticky top-0';
                    const headerRow = document.createElement('tr');
                    rows[0].forEach((header, idx) => {
                        const th = document.createElement('th');
                        th.className = 'px-3 py-2 text-left font-semibold text-gray-700 border-b border-r';
                        th.textContent = header || `Colonne ${idx + 1}`;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);
                    table.appendChild(thead);
                    
                    // Data rows
                    const tbody = document.createElement('tbody');
                    rows.slice(1).forEach((row, rowIdx) => {
                        const tr = document.createElement('tr');
                        tr.className = rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50';
                        
                        row.forEach(cell => {
                            const td = document.createElement('td');
                            td.className = 'px-3 py-2 border-b border-r text-gray-800';
                            td.textContent = cell;
                            tr.appendChild(td);
                        });
                        tbody.appendChild(tr);
                    });
                    table.appendChild(tbody);
                    
                    wrapper.appendChild(table);
                    inner.appendChild(wrapper);
                    
                    // Add row count info
                    const info = document.createElement('div');
                    info.className = 'text-xs text-gray-600 mt-2';
                    info.textContent = `${rows.length - 1} ligne(s) de données`;
                    inner.appendChild(info);
                } else {
                    // Too large, show as text with warning
                    const warning = document.createElement('div');
                    warning.className = 'bg-yellow-50 border border-yellow-200 rounded p-3 mb-3 text-sm';
                    warning.textContent = `Fichier volumineux (${rows.length} lignes). Affichage en mode texte.`;
                    inner.appendChild(warning);
                    
                    const pre = document.createElement('pre');
                    pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[55vh]';
                    pre.textContent = text;
                    inner.appendChild(pre);
                }
            } catch (parseError) {
                console.error('CSV parsing error:', parseError);
                // Fallback to plain text
                const pre = document.createElement('pre');
                pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[60vh]';
                pre.textContent = text;
                inner.appendChild(pre);
            }
            return;
        }

        // Plain Text Handler
        if (contentType.startsWith('text/') || ['txt', 'log', 'md'].includes(ext)) {
            const text = await res.text();
            
            if (!text.trim()) {
                renderHeader();
                inner.innerHTML += '<div class="text-gray-600 text-sm">Le fichier texte est vide.</div>';
                return;
            }
            
            renderHeader();
            
            const pre = document.createElement('pre');
            pre.className = 'text-xs bg-gray-100 p-4 rounded overflow-auto code-font max-h-[60vh] whitespace-pre-wrap';
            pre.textContent = text;
            inner.appendChild(pre);
            return;
        }

        // Image Handler
        if (contentType.startsWith('image/') || ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(ext)) {
            const blob = await res.blob();
            const imgURL = URL.createObjectURL(blob);
            
            renderHeader();
            
            const container = document.createElement('div');
            container.className = 'flex items-center justify-center bg-gray-50 rounded p-4';
            container.style.maxHeight = '65vh';
            
            const img = document.createElement('img');
            img.src = imgURL;
            img.alt = name;
            img.className = 'max-w-full max-h-full h-auto rounded shadow-lg';
            img.onload = () => URL.revokeObjectURL(imgURL); // Clean up
            
            container.appendChild(img);
            inner.appendChild(container);
            return;
        }

        // Fallback for unsupported file types
        renderHeader();
        const fallback = document.createElement('div');
        fallback.className = 'bg-gray-50 border border-gray-200 rounded p-4 text-sm';
        fallback.innerHTML = `
            <p class="mb-2">Type de fichier non affichable : <strong>${contentType || ext}</strong></p>
            <a class="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" 
               href="${url}" 
               download="${name}">
                Télécharger le fichier
            </a>
        `;
        inner.appendChild(fallback);

    } catch (err) {
        inner.innerHTML = `
            <div class="text-red-600 bg-red-50 border border-red-200 rounded p-4">
                <strong>Erreur:</strong> ${err.message || 'Impossible de charger le fichier.'}
            </div>
        `;
        console.error('showFile error:', err);
    }
}

function showImage(name) {
    const modalId = 'imageModal';
    // Create a modal to display the full-size image
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4';
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
        document.body.appendChild(modal);
    }
    
    modal.innerHTML = '';
    
    const container = document.createElement('div');
    container.className = 'bg-white rounded-lg overflow-hidden max-w-[95vw] max-h-[95vh] flex flex-col';
    
    const header = document.createElement('div');
    header.className = 'flex justify-between items-center p-4 border-b border-gray-200';
    
    const title = document.createElement('h4');
    title.className = 'font-semibold text-gray-900';
    title.textContent = name;
    
    const actions = document.createElement('div');
    actions.className = 'flex gap-2';
    
    const downloadBtn = document.createElement('a');
    downloadBtn.href = `${API_BASE}/api/download?category=graphs&name=${encodeURIComponent(name)}`;
    downloadBtn.target = '_blank';
    downloadBtn.className = 'text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700';
    downloadBtn.textContent = 'Télécharger';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'text-sm text-gray-600 hover:text-gray-900 ml-2';
    closeBtn.textContent = '✕ Fermer';
    closeBtn.onclick = () => modal.remove();
    
    actions.appendChild(downloadBtn);
    actions.appendChild(closeBtn);
    header.appendChild(title);
    header.appendChild(actions);
    
    const imgContainer = document.createElement('div');
    imgContainer.className = 'p-4 overflow-auto flex items-center justify-center bg-gray-50';
    imgContainer.style.maxHeight = '85vh';
    
    const img = document.createElement('img');
    img.src = `${API_BASE}/api/graphs/${encodeURIComponent(name)}`;
    img.alt = name;
    img.className = 'max-w-full h-auto rounded shadow-lg';
    
    imgContainer.appendChild(img);
    container.appendChild(header);
    container.appendChild(imgContainer);
    modal.appendChild(container);
}

function initializeCharts() {
    // Graphique de comparaison des frameworks
    const ctx1 = document.getElementById('frameworkChart');
    if (ctx1) {
        drawFrameworkChart(ctx1.getContext('2d'));
    }
    
    // Graphique de scalabilité
    const ctx2 = document.getElementById('scalabilityChart');
    if (ctx2) {
        drawScalabilityChart(ctx2.getContext('2d'));
    }
}

function drawFrameworkChart(ctx) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    
    // Données de performance
    const frameworks = ['Hadoop', 'Spark', 'MPI', 'Flink'];
    const performance = [100, 65, 45, 55]; // Temps d'exécution relatif
    const colors = ['#ef4444', '#f97316', '#3b82f6', '#8b5cf6'];
    
    // Effacer le canvas
    ctx.clearRect(0, 0, width, height);
    
    // Dessiner les barres
    const barWidth = width / (frameworks.length * 2);
    const maxValue = Math.max(...performance);
    
    frameworks.forEach((framework, index) => {
        const barHeight = (performance[index] / maxValue) * (height - 60);
        const x = (index * 2 + 0.5) * barWidth;
        const y = height - 40 - barHeight;
        
        // Barre
        ctx.fillStyle = colors[index];
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Label
        ctx.fillStyle = '#374151';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(framework, x + barWidth/2, height - 20);
        ctx.fillText(performance[index] + 's', x + barWidth/2, y - 5);
    });
    
    // Titre
    ctx.fillStyle = '#111827';
    ctx.font = 'bold 14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Temps d\'exécution par framework', width/2, 20);
}

function drawScalabilityChart(ctx) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    
    // Données de scalabilité
    const nodes = [1, 2, 4, 8, 12, 16, 20];
    const speedup = [1, 1.8, 3.2, 5.5, 7.2, 8.5, 9.1];
    
    // Effacer le canvas
    ctx.clearRect(0, 0, width, height);
    
    // Dessiner les axes
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(40, height - 40);
    ctx.lineTo(width - 20, height - 40);
    ctx.moveTo(40, height - 40);
    ctx.lineTo(40, 20);
    ctx.stroke();
    
    // Dessiner la ligne de scalabilité
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    nodes.forEach((node, index) => {
        const x = 40 + (node / 20) * (width - 60);
        const y = height - 40 - (speedup[index] / 10) * (height - 60);
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        // Points
        ctx.fillStyle = '#3b82f6';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
        
        // Labels
        if (index % 2 === 0) {
            ctx.fillStyle = '#374151';
            ctx.font = '10px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(node.toString(), x, height - 25);
        }
    });
    ctx.stroke();
    
    // Titre
    ctx.fillStyle = '#111827';
    ctx.font = 'bold 14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Scalabilité linéaire', width/2, 20);
    
    // Axe Y
    ctx.fillStyle = '#374151';
    ctx.font = '12px Inter';
    ctx.textAlign = 'right';
    ctx.fillText('Speedup', 35, 15);
}

function updateSimulation() {
    const dataSize = document.getElementById('dataSize');
    const nodes = document.getElementById('nodes');
    const algorithm = document.getElementById('algorithm');
    
    if (!dataSize || !nodes || !algorithm) return;
    
    const dataSizeValue = document.getElementById('dataSizeValue');
    const nodesValue = document.getElementById('nodesValue');
    
    if (dataSizeValue) dataSizeValue.textContent = dataSize.value + ' GB';
    if (nodesValue) nodesValue.textContent = nodes.value + ' nœuds';
    
    // Calculer les performances estimées
    const config = performanceData[algorithm.value];
    const baseTime = config.baseTime * (dataSize.value / 10);
    const parallelTime = baseTime / Math.min(nodes.value, 12) * (1 + config.overhead);
    const efficiency = Math.min(config.efficiency * Math.min(nodes.value, 8) / nodes.value, 1);
    
    // Mettre à jour l'affichage
    const executionTime = document.getElementById('executionTime');
    const processedData = document.getElementById('processedData');
    const processingRate = document.getElementById('processingRate');
    const parallelEfficiency = document.getElementById('parallelEfficiency');
    const cpuLoad = document.getElementById('cpuLoad');
    
    if (executionTime) executionTime.textContent = Math.round(parallelTime) + ' secondes';
    if (processedData) processedData.textContent = dataSize.value + ' GB';
    if (processingRate) processingRate.textContent = Math.round(dataSize.value / parallelTime * 100) / 100 + ' GB/s';
    if (parallelEfficiency) parallelEfficiency.textContent = Math.round(efficiency * 100) + '%';
    if (cpuLoad) cpuLoad.textContent = Math.round(75 + Math.random() * 20) + '%';
}

function runSimulation() {
    if (simulationRunning) {
        stopSimulation();
        return;
    }
    
    simulationRunning = true;
    const button = event.target;
    button.textContent = 'Arrêter la Simulation';
    button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
    button.classList.add('bg-red-600', 'hover:bg-red-700');
    
    let mapProgress = 0;
    let reduceProgress = 0;
    
    simulationInterval = setInterval(() => {
        // Simuler la progression
        if (mapProgress < 100) {
            mapProgress += Math.random() * 15;
            if (mapProgress > 100) mapProgress = 100;
        } else if (reduceProgress < 100) {
            reduceProgress += Math.random() * 10;
            if (reduceProgress > 100) reduceProgress = 100;
        } else {
            stopSimulation();
            return;
        }
        
        // Mettre à jour l'interface
        const mapProgressEl = document.getElementById('mapProgress');
        const mapBarEl = document.getElementById('mapBar');
        const reduceProgressEl = document.getElementById('reduceProgress');
        const reduceBarEl = document.getElementById('reduceBar');
        
        if (mapProgressEl) mapProgressEl.textContent = Math.round(mapProgress) + '%';
        if (mapBarEl) mapBarEl.style.width = mapProgress + '%';
        if (reduceProgressEl) reduceProgressEl.textContent = Math.round(reduceProgress) + '%';
        if (reduceBarEl) reduceBarEl.style.width = reduceProgress + '%';
        
        // Mettre à jour les statistiques dynamiques
        if (mapProgress > 0) {
            const dataSizeEl = document.getElementById('dataSize');
            const processingRateEl = document.getElementById('processingRate');
            const cpuLoadEl = document.getElementById('cpuLoad');
            
            if (dataSizeEl && processingRateEl) {
                const dataSize = parseInt(dataSizeEl.value);
                const elapsed = (mapProgress / 100) * 60; // Temps simulé
                processingRateEl.textContent = Math.round(dataSize / (elapsed || 1) * 100) / 100 + ' GB/s';
            }
            if (cpuLoadEl) {
                cpuLoadEl.textContent = Math.round(70 + Math.random() * 25) + '%';
            }
        }
    }, 200);
}

function stopSimulation() {
    simulationRunning = false;
    if (simulationInterval) {
        clearInterval(simulationInterval);
        simulationInterval = null;
    }
    
    const button = document.querySelector('button[onclick="runSimulation()"]');
    if (button) {
        button.textContent = 'Lancer la Simulation';
        button.classList.remove('bg-red-600', 'hover:bg-red-700');
        button.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }
    
    // Réinitialiser la progression
    setTimeout(() => {
        const mapProgressEl = document.getElementById('mapProgress');
        const mapBarEl = document.getElementById('mapBar');
        const reduceProgressEl = document.getElementById('reduceProgress');
        const reduceBarEl = document.getElementById('reduceBar');
        
        if (mapProgressEl) mapProgressEl.textContent = '0%';
        if (mapBarEl) mapBarEl.style.width = '0%';
        if (reduceProgressEl) reduceProgressEl.textContent = '0%';
        if (reduceBarEl) reduceBarEl.style.width = '0%';
    }, 1000);
}

// Animation de défilement fluide
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
        });
    });
});

// Effet de parallaxe pour la section hero
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero-bg');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Gestion du menu mobile
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Initialisation des animations au défilement
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observer les éléments avec animation
document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll('.card-hover');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});