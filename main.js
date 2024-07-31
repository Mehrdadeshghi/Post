document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('sensorChart').getContext('2d');
    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Movements',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    data: []
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Movements'
                    }
                }
            }
        }
    });

    function updateSensorData(sensorName) {
        fetch(`/api/movements/${sensorName}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('total_movements').innerText = data.total_movements;
                document.getElementById('last_24h_movements').innerText = data.last_24h_movements;
                document.getElementById('last_week_movements').innerText = data.last_week_movements;
                document.getElementById('last_month_movements').innerText = data.last_month_movements;
                document.getElementById('last_movement').innerText = data.last_movement;

                let labels = [];
                let movementData = [];

                data.all_movements.forEach(movement => {
                    labels.push(movement[0]);
                    movementData.push(1);
                });

                chart.data.labels = labels;
                chart.data.datasets[0].data = movementData;
                chart.update();
            });
    }

    const sensorName = document.getElementById('sensorName').innerText;
    updateSensorData(sensorName);
    setInterval(() => updateSensorData(sensorName), 1000);
});
