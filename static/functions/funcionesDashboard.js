
const ctxVentas = document.getElementById('ventasChart').getContext('2d');
new Chart(ctxVentas, {
    type: 'bar',
    data: {
        labels: ['Paquete 1 kg', 'Paquete 700 gr', 'Paquete 1/2 kg', 'Peso 500 gr', 'Peso 100 gr'],
        datasets: [{
            label: 'Cantidad vendida',
            data: [100, 75, 60, 50, 25],
            backgroundColor: '#8B5E3B'
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: { color: 'black' } // Color de los números del eje Y
            },
            x: {
                ticks: { color: 'black' } // Color de los nombres del eje X
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: 'black' // Color de la leyenda
                }
            }
        }
    }
});

const ctxGanancias = document.getElementById('gananciasChart').getContext('2d');
new Chart(ctxGanancias, {
    type: 'bar',
    data: {
        labels: ['12/03', '13/03', '14/03', '15/03', '16/03'],
        datasets: [{
            label: 'Ganancias ($)',
            data: [4000, 3000, 6000, 1000, 5500],
            backgroundColor: '#8B5E3B'
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: { color: 'black' } // Color de los números del eje Y
            },
            x: {
                ticks: { color: 'black' } // Color de los nombres del eje X
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: 'black' // Color de la leyenda
                }
            }
        }
    }
});
