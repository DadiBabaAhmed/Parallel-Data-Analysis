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
});

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