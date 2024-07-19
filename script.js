<script>
async function fetchPinStates() {
    const response = await fetch('/api/get_pin_states');
    const states = await response.json();
    const devicesResp = await fetch('/api/get_devices');
    const devices = await devicesResp.json();

    const table = document.getElementById('pinStatusTable');
    table.innerHTML = '';
    Object.keys(states).forEach(pin => {
        const row = table.insertRow();
        const pinCell = row.insertCell();
        const statusCell = row.insertCell();
        const actionCell = row.insertCell();

        pinCell.innerHTML = pin;
        statusCell.innerHTML = states[pin];
        statusCell.className = states[pin] === 'Kein Gerät' ? 'free' : 'occupied';

        let buttonHTML = devices[pin] ? devices[pin] : (states[pin] === 'Gerät angeschlossen' ? `<input type="text" id="name${pin}" placeholder="Device Name">
        <button class="btn btn-primary" onclick="addDevice(${pin})">Add Device</button>` : 'N/A');
        actionCell.innerHTML = buttonHTML;
    });
}

async function addDevice(pin) {
    const name = document.getElementById('name' + pin).value;
    if (!name) {
        alert('Please enter a name.');
        return;
    }

    const response = await fetch('/api/add_device', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ pin: pin, name: name })
    });

    if (response.ok) {
        fetchPinStates();
    } else {
        alert('Failed to add device. It might already exist.');
    }
}

fetchPinStates(); // Erste Abfrage sofort ausführen
setInterval(fetchPinStates, 10000); // Update alle 10 Sekunden
</script>
