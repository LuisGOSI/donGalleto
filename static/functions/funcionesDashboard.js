document.addEventListener("DOMContentLoaded", function() {
    const presentacionesData = JSON.parse(document.getElementById('presentacionesData').textContent);
    const presentacionesLabels = presentacionesData.map(item => item.tipoVenta);
    const presentacionesValues = presentacionesData.map(item => item.total);
    const total = presentacionesValues.reduce((sum, value) => sum + value, 0);
    const ctxVentas = document.getElementById('ventasChart').getContext('2d');
    new Chart(ctxVentas, {
        type: 'pie',
        data: {
            labels: presentacionesLabels.map((label, i) => {
                const percentage = ((presentacionesValues[i] / total) * 100).toFixed(1);
                return `${label}(${percentage}%)`;
            }),
            datasets: [{
                label: 'Cantidad vendida $',
                data: presentacionesValues,
                backgroundColor: ['#8B5E3B','#A67C52','#C19A6B','#D9B38C','#E3C7A1'],
                borderColor: '#4E3629',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: 'black' }
                },
                title: {
                    display: true,
                    text: 'Distribución de tipos de venta($)',
                    color: 'black',
                    font: { size: 20 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return ` $${value.toLocaleString()} `;
                        }
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
                y: { beginAtZero: true, ticks: { color: 'black' } },
                x: { ticks: { color: 'black' } }
            },
            plugins: {
                legend: { labels: { color: 'black' } }
            }
        }
    });
});