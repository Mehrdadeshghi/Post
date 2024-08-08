<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assign User to PIR Sensor</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="/">Raspberry Pi Management</a>
    </nav>
    <div class="container mt-5">
        <h1 class="mb-4">Assign User to PIR Sensor ID: {{ sensor_id }}</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="post" action="{{ url_for('assign_user', sensor_id=sensor_id) }}">
            <div class="form-group">
                <label for="user_id">Select User</label>
                <select class="form-control" id="user_id" name="user_id" required>
                    {% for user in users %}
                    <option value="{{ user.user_id }}">{{ user.username }}</option>
                    {% endfor %}
                </select>
            </div>
            <input type="hidden" name="raspberry_id" value="{{ raspberry_id }}">
            <button type="submit" class="btn btn-primary">Assign User</button>
        </form>
        <button class="btn btn-secondary mt-4" onclick="window.location.href='/raspberry/{{ raspberry_id }}/pirs'">Back to PIR Sensors</button>
    </div>
</body>
</html>
