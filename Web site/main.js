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
        // Build UI: show graphs thumbnails and JSON files list
        const wrapper = document.createElement('div');
        wrapper.className = 'space-y-6';

        // Graphs
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
                card.className = 'bg-gray-50 p-3 rounded-lg';
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

        // Statistics / JSON
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
                row.className = 'flex items-center justify-between p-2 bg-gray-50 rounded';
                const left = document.createElement('div');
                left.className = 'text-sm text-gray-800';
                left.textContent = name;
                const right = document.createElement('div');
                const viewBtn = document.createElement('button');
                viewBtn.className = 'text-sm bg-blue-600 text-white px-3 py-1 rounded';
                viewBtn.textContent = 'Voir JSON';
                viewBtn.onclick = async () => {
                    await showJson(name);
                };
                const dlBtn = document.createElement('a');
                dlBtn.className = 'ml-2 text-sm text-gray-600';
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

        // General files (CSV etc.)
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
                row.className = 'flex items-center justify-between p-2 bg-gray-50 rounded';
                const left = document.createElement('div');
                left.className = 'text-sm text-gray-800';
                left.textContent = name;
                const right = document.createElement('div');
                const dl = document.createElement('a');
                dl.className = 'text-sm text-gray-600';
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
        resultsArea.innerHTML = '<div class="text-red-600">Erreur lors de la récupération des résultats. Assurez-vous que l\'API est démarrée (`make run-api`).</div>';
        console.error('fetchResults error', err);
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


async function triggerAnalysis() {
    const sel = document.getElementById('inputFileSelect');
    const file = sel.value;
    const analysis = document.getElementById('analysisType').value;
    const statusDiv = document.getElementById('jobStatus');
    if (!file || file === 'Aucun fichier trouvé' || file === 'Chargement...') {
        statusDiv.textContent = 'Veuillez sélectionner un fichier d\'entrée valide.';
        return;
    }
    statusDiv.textContent = 'Démarrage du job...';
    try {
        const res = await fetch(`${API_BASE}/api/trigger`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: file, analysis: analysis})
        });
        const data = await res.json();
        if (res.ok && data.job_id) {
            statusDiv.innerHTML = `Job démarré: <strong>${data.job_id}</strong>`;
            // Start polling
            pollJobStatus(data.job_id);
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
        logsDiv.className = 'mt-3 text-xs bg-gray-100 p-3 rounded code-font max-h-48 overflow-auto';
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
            statusDiv.innerHTML = `Job <strong>${job_id}</strong>: ${info.status}`;

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
                statusDiv.innerHTML += ' — terminé';
            }
        } catch (err) {
            console.error('pollJobStatus error', err);
            statusDiv.textContent = 'Erreur lors de la récupération du statut du job.';
            clearInterval(poll);
        }
    }, 2000);
}

async function showJson(name) {
    const modalId = 'jsonModal';
    // Create a simple modal to display JSON
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
        const res = await fetch(`${API_BASE}/api/results/file?category=statistics&name=${encodeURIComponent(name)}`);
        const data = await res.json();
        const pre = document.createElement('pre');
        pre.className = 'text-xs bg-gray-100 p-3 rounded overflow-auto code-font';
        pre.textContent = JSON.stringify(data, null, 2);
        inner.innerHTML = '';
        const title = document.createElement('div');
        title.className = 'flex justify-between items-center mb-3';
        const t = document.createElement('h4');
        t.className = 'font-semibold';
        t.textContent = name;
        const close = document.createElement('button');
        close.className = 'text-sm text-gray-600';
        close.textContent = 'Fermer';
        close.onclick = () => modal.remove();
        title.appendChild(t);
        title.appendChild(close);
        inner.appendChild(title);
        inner.appendChild(pre);
    } catch (err) {
        inner.innerHTML = '<div class="text-red-600">Impossible de charger le fichier JSON.</div>';
        console.error('showJson error', err);
    }
}

function initializeCharts() {
    // Graphique de comparaison des frameworks
    const ctx1 = document.getElementById('frameworkChart').getContext('2d');
    drawFrameworkChart(ctx1);
    
    // Graphique de scalabilité
    const ctx2 = document.getElementById('scalabilityChart').getContext('2d');
    drawScalabilityChart(ctx2);
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
    const dataSize = document.getElementById('dataSize').value;
    const nodes = document.getElementById('nodes').value;
    const algorithm = document.getElementById('algorithm').value;
    
    document.getElementById('dataSizeValue').textContent = dataSize + ' GB';
    document.getElementById('nodesValue').textContent = nodes + ' nœuds';
    
    // Calculer les performances estimées
    const config = performanceData[algorithm];
    const baseTime = config.baseTime * (dataSize / 10);
    const parallelTime = baseTime / Math.min(nodes, 12) * (1 + config.overhead);
    const efficiency = Math.min(config.efficiency * Math.min(nodes, 8) / nodes, 1);
    
    // Mettre à jour l'affichage
    document.getElementById('executionTime').textContent = Math.round(parallelTime) + ' secondes';
    document.getElementById('processedData').textContent = dataSize + ' GB';
    document.getElementById('processingRate').textContent = Math.round(dataSize / parallelTime * 100) / 100 + ' GB/s';
    document.getElementById('parallelEfficiency').textContent = Math.round(efficiency * 100) + '%';
    document.getElementById('cpuLoad').textContent = Math.round(75 + Math.random() * 20) + '%';
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
        document.getElementById('mapProgress').textContent = Math.round(mapProgress) + '%';
        document.getElementById('mapBar').style.width = mapProgress + '%';
        document.getElementById('reduceProgress').textContent = Math.round(reduceProgress) + '%';
        document.getElementById('reduceBar').style.width = reduceProgress + '%';
        
        // Mettre à jour les statistiques dynamiques
        if (mapProgress > 0) {
            const dataSize = parseInt(document.getElementById('dataSize').value);
            const elapsed = (mapProgress / 100) * 60; // Temps simulé
            document.getElementById('processingRate').textContent = Math.round(dataSize / (elapsed || 1) * 100) / 100 + ' GB/s';
            document.getElementById('cpuLoad').textContent = Math.round(70 + Math.random() * 25) + '%';
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
    button.textContent = 'Lancer la Simulation';
    button.classList.remove('bg-red-600', 'hover:bg-red-700');
    button.classList.add('bg-blue-600', 'hover:bg-blue-700');
    
    // Réinitialiser la progression
    setTimeout(() => {
        document.getElementById('mapProgress').textContent = '0%';
        document.getElementById('mapBar').style.width = '0%';
        document.getElementById('reduceProgress').textContent = '0%';
        document.getElementById('reduceBar').style.width = '0%';
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
    menu.classList.toggle('hidden');
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