// Dark Mode Umschaltung
const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;

if (currentTheme) {
    document.documentElement.setAttribute('data-theme', currentTheme);

    if (currentTheme === 'dark') {
        toggleSwitch.checked = true;
        document.body.classList.add('dark-mode');
    }
}

toggleSwitch.addEventListener('change', (e) => {
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

async function selectSensor() {
    const sensorId = document.getElementById('sensorSelector').value;
    const response = await fetch(`/movements/${sensorId}`);
    const data = await response.json();
    document.getElementById('sensorData').innerText = JSON.stringify(data, null, 2);
}
