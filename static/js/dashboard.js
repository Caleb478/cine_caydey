// Configurar los datos y generar las gráficas
document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('/api/dashboard-data');
    const data = await response.json();

    // Gráfica de Ventas Totales por Mes
    const ventasTotalesCtx = document.getElementById('ventasTotalesChart').getContext('2d');
    new Chart(ventasTotalesCtx, {
        type: 'line',
        data: {
            labels: data.ventas_totales.meses,
            datasets: [{
                label: 'Ingresos ($)',
                data: data.ventas_totales.valores,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true
            }]
        }
    });

    // Gráfica de Entradas Vendidas por Género
    const entradasGeneroCtx = document.getElementById('entradasGeneroChart').getContext('2d');
    new Chart(entradasGeneroCtx, {
        type: 'bar',
        data: {
            labels: data.generos.labels,
            datasets: [{
                label: 'Entradas Vendidas',
                data: data.generos.valores,
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }]
        }
    });

    // Gráfica de Clasificación
    const clasificacionCtx = document.getElementById('clasificacionChart').getContext('2d');
    new Chart(clasificacionCtx, {
        type: 'doughnut',
        data: {
            labels: data.clasificacion.labels,
            datasets: [{
                data: data.clasificacion.valores,
                backgroundColor: ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)']
            }]
        }
    });

    // Gráfica de Ocupación Promedio de Salas
    const ocupacionSalasCtx = document.getElementById('ocupacionSalasChart').getContext('2d');
    new Chart(ocupacionSalasCtx, {
        type: 'radar',
        data: {
            labels: data.ocupacion_salas.labels,
            datasets: [{
                label: 'Ocupación (%)',
                data: data.ocupacion_salas.valores,
                backgroundColor: 'rgba(255, 159, 64, 0.6)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
            }]
        }
    });
});