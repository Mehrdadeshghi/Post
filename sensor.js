var ctx = document.getElementById('movementChart').getContext('2d');
var movementChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Timestamps will go here
        datasets: [{
            label: 'Movements',
            data: [], // Data points will go here
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'minute'
                }
            }
        }
    }
});

var socket = io();
socket.on('movement', function(data) {
    if (data.sensor === sensorName) {
        var currentTime = new Date().toISOString();
        movementChart.data.labels.push(currentTime);
        movementChart.data.datasets[0].data.push(1); // 1 for a new movement
        movementChart.update();
    }
});
