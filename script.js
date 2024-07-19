document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/pin_states')
        .then(response => response.json())
        .then(data => {
            const statusContainer = document.getElementById('pinStatus');
            statusContainer.innerHTML = '<ul>';
            Object.keys(data).forEach(pin => {
                statusContainer.innerHTML += `<li>Pin ${pin}: ${data[pin] ? 'High' : 'Low'}</li>`;
            });
            statusContainer.innerHTML += '</ul>';
        });
});
