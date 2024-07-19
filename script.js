document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/pin_states')
        .then(response => response.json())
        .then(data => {
            const statusContainer = document.getElementById('pinStatus');
            statusContainer.innerHTML = '';
            data.forEach(item => {
                const statusClass = item.status ? 'status-high' : 'status-low';
                const statusText = item.status ? 'High' : 'Low';
                let content = `<div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Pin ${item.pin}</h5>
                            <p class="card-text ${statusClass}">${statusText}</p>
                            <p>${item.name ? item.name : ''}</p>`;
                if (!item.name) {
                    content += `<input type="text" placeholder="Name" id="name${item.pin}">
                                <button onclick="addDevice(${item.pin})" class="btn btn-primary">Add Device</button>`;
                }
                content += `   </div>
                    </div>
                </div>`;
                statusContainer.innerHTML += content;
            });
        });
});

function addDevice(pin) {
    const name = document.getElementById(`name${pin}`).value;
    fetch('/api/add_device', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ pin: pin, name: name })
    }).then(response => response.json())
      .then(data => {
          if (data.error) {
              alert(data.error);
          } else {
              alert('Device added successfully!');
              location.reload();
          }
      });
}
