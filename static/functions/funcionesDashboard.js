document.addEventListener("DOMContentLoaded", function() {
    const presentacionesData = JSON.parse(document.getElementById('presentacionesData').textContent);
    const presentacionesLabels = presentacionesData.map(item => item.tipoVenta);
    const presentacionesValues = presentacionesData.map(item => item.total);
    const ctxVentas = document.getElementById('ventasChart').getContext('2d');
    new Chart(ctxVentas, {
        type: 'pie',
        data: {
            labels: presentacionesLabels,
            datasets: [{
                label: 'Cantidad vendida',
                data: presentacionesValues,
                backgroundColor: [
                    '#8B5E3B',
                    '#A67C52',
                    '#C19A6B',
                    '#D9B38C',
                    '#E3C7A1'
                ],
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
                    text: 'Distribución de tipos de venta',
                    color: 'black',
                    font: { size: 20 }
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
    const ventasData = JSON.parse(document.getElementById('ventasData').textContent);
    const fechasConDatos = ventasData.map(item => {
        const fechaOriginal = new Date(item[0]);
        const fechaMasUnDia = new Date(fechaOriginal);
        fechaMasUnDia.setDate(fechaOriginal.getDate() + 1);
        return fechaMasUnDia;
    });
    const ventasDiariasValues = ventasData.map(item => item[1]);
    const ultimaFecha = new Date(fechasConDatos[fechasConDatos.length - 1]);
    const fechasExtendidas = [...fechasConDatos];
    for (let i = 1; i <= 2; i++) {
        const nuevaFecha = new Date(ultimaFecha);
        nuevaFecha.setDate(ultimaFecha.getDate() + i);
        fechasExtendidas.push(nuevaFecha);
    }
    const ventasDiariasLabels = fechasExtendidas.map(fecha => {
        return fecha.toLocaleDateString('es-ES', {
            weekday: 'short', 
            day: 'numeric',
            month: 'short'
        });
    });
    const valoresExtendidos = [...ventasDiariasValues, null, null];
    const ctxVentasDiarias = document.getElementById('ventasDiariasChart').getContext('2d');
    new Chart(ctxVentasDiarias, {
        type: 'line',
        data: {
            labels: ventasDiariasLabels,
            datasets: [{
                label: 'Ventas por día',
                data: valoresExtendidos,
                backgroundColor: 'rgba(139, 94, 59, 0.2)',
                borderColor: '#8B5E3B',
                borderWidth: 2,
                pointBackgroundColor: '#8B5E3B',
                pointRadius: function(context) {
                    return context.dataset.data[context.dataIndex] !== null ? 5 : 0;
                },
                pointHoverRadius: function(context) {
                    return context.dataset.data[context.dataIndex] !== null ? 7 : 0;
                },
                tension: 0,
                borderJoinStyle: 'miter',
                fill: true,
                spanGaps: false
            }]
        },
        options: {
            responsive: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: Math.max(...ventasDiariasValues.filter(v => v !== null)) + 5,
                    ticks: { 
                        color: 'black',
                        callback: function(value) {
                            return value.toLocaleString('es-ES');
                        }
                    }
                },
                x: {
                    ticks: { 
                        color: 'black',
                        maxRotation: 0,
                        minRotation: 0
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    labels: { 
                        color: 'black',
                        boxWidth: 12,
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y !== null ? ` Ventas: ${context.parsed.y}` : ' Sin datos';
                        },
                        title: function(context) {
                            return context[0].label;
                        }
                    },
                    displayColors: false,
                    backgroundColor: 'rgba(78, 54, 41, 0.9)',
                    titleFont: { size: 14 },
                    bodyFont: { size: 12 },
                    padding: 12
                }
            }
        }
    });
});