function updateSystemInfo() {
    fetch('/api/system_info')
        .then(response => response.json())
        .then(data => {
            document.getElementById('system_name').innerText = data.system_name;
            document.getElementById('system_ip').innerText = data.system_ip;
            document.getElementById('system_uptime').innerText = data.system_uptime;
            document.getElementById('cpu_temp').innerText = data.cpu_temp + '°C';
            document.getElementById('cpu_usage').innerText = data.cpu_usage + '%';
            document.getElementById('memory_usage').innerText = data.memory_usage + '%';
            document.getElementById('disk_usage').innerText = data.disk_usage + '%';
            document.getElementById('network_upload').innerText = data.network_upload + ' bytes';
            document.getElementById('network_download').innerText = data.network_download + ' bytes';
            document.getElementById('active_processes').innerText = data.active_processes;
            updateChart(data);
        });
}

function updateChart(data) {
    let labels = chart.data.labels;
    let datasets = chart.data.datasets;

    let now = new Date().toLocaleTimeString();

    labels.push(now);
    datasets[0].data.push(data.cpu_usage);
    datasets[1].data.push(data.memory_usage);
    datasets[2].data.push(data.disk_usage);

    if (labels.length > 20) {
        labels.shift();
        datasets[0].data.shift();
        datasets[1].data.shift();
        datasets[2].data.shift();
    }

    chart.update();
}

setInterval(updateSystemInfo, 1000);

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('systemChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CPU Usage (%)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    data: []
                },
                {
                    label: 'Memory Usage (%)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    data: []
                },
                {
                    label: 'Disk Usage (%)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
                        text: 'Usage (%)'
                    }
                }
            }
        }
    });
    updateSystemInfo();
});
