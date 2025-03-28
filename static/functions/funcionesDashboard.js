document.addEventListener("DOMContentLoaded", function() {
    const presentacionesData = JSON.parse(document.getElementById('presentacionesData').textContent);

    const presentacionesLabels = presentacionesData.map(item => item.tipoVenta);
    const presentacionesValues = presentacionesData.map(item => item.total);
    
    const ctxVentas = document.getElementById('ventasChart').getContext('2d');
    new Chart(ctxVentas, {
        type: 'bar',
        data: {
            labels: presentacionesLabels,
            datasets: [{
                label: 'Cantidad vendida',
                data: presentacionesValues,
                backgroundColor: '#8B5E3B'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: 'black' }
                },
                x: {
                    ticks: { color: 'black' }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'black'
                    }
                }
            }
        }
    });
    
    const gananciasData = JSON.parse(document.getElementById('gananciasData').textContent);
    
    const gananciasLabels = gananciasData.map(item => item.fecha);
    const gananciasValues = gananciasData.map(item => item.ganancias_diarias);
    
    const ctxGanancias = document.getElementById('gananciasChart').getContext('2d');
    new Chart(ctxGanancias, {
        type: 'bar',
        data: {
            labels: gananciasLabels,
            datasets: [{
                label: 'Ganancias diarias $',
                data: gananciasValues,
                backgroundColor: '#8B5E3B'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: 'black' }
                },
                x: {
                    ticks: { color: 'black' }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'black'
                    }
                }
            }
        }
    });
});
