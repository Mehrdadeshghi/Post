document.addEventListener('DOMContentLoaded', function() {
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
            document.body.classList.add('dark-mode');
        }
    }

    toggleSwitch.addEventListener('change', function(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            document.body.classList.add('dark-mode');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            document.body.classList.remove('dark-mode');
        }
    });

    let movementChart;
    let hourlyChart;

    async function fetchMovements() {
        try {
            const response = await fetch('/movements');
            const data = await response.json();
            updateChart(data);
            updateTable(data);
        } catch (error) {
            console.error('Error fetching movements:', error);
        }
    }

    async function fetchSummary() {
        try {
            const response = await fetch('/summary');
            const data = await response.json();
            document.getElementById('total_movements').innerText = data.total_movements;
            document.getElementById('last_24_hours_movements').innerText = data.last_24_hours_movements;
            document.getElementById('last_week_movements').innerText = data.last_week_movements;
            document.getElementById('last_month_movements').innerText = data.last_month_movements;
            document.getElementById('last_motion_time').innerText = data.last_motion_time;
        } catch (error) {
            console.error('Error fetching summary:', error);
        }
    }

    async function fetchHourlyMovements() {
        try {
            const response = await fetch('/hourly_movements');
            const data = await response.json();
            updateHourlyChart(data);
        } catch (error) {
            console.error('Error fetching hourly movements:', error);
        }
    }

    function updateChart(movements) {
        const labels = movements.map(time => new Date(time).toLocaleTimeString());
        const dataPoints = movements.map((time, index) => index + 1);

        if (movementChart) {
            movementChart.data.labels = labels;
            movementChart.data.datasets[0].data = dataPoints;
            movementChart.update();
        } else {
            const ctx = document.getElementById('movementChart').getContext('2d');
            movementChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Movement Number',
                        data: dataPoints,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        fill: false,
                        tension
