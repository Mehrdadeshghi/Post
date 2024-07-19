document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/pin_states')
        .then(response => response.json())
        .then(data => {
            const statusContainer = document.getElementById('pinStatus');
            statusContainer.innerHTML = '';
            Object.keys(data).forEach(pin => {
                const statusClass = data[pin] ? 'status-high' : 'status-low';
                const statusText = data[pin] ? 'High' : 'Low';
                statusContainer.innerHTML += `
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Pin ${pin}</h5>
                                <p class="card-text ${statusClass}">${statusText}</p>
                            </div>
                        </div>
                    </div>`;
            });
        });
});
