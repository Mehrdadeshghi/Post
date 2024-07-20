<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PIR Sensor Controller</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>PIR Sensor Controller: {{ controller_name }}</h1>
        <div class="theme-switch-wrapper">
            <span>Light Mode</span>
            <label class="theme-switch" for="checkbox">
                <input type="checkbox" id="checkbox">
                <div class="slider round"></div>
            </label>
            <span>Dark Mode</span>
        </div>
        <div class="list-group">
            {% for sensor in sensors %}
            <a href="/sensor/{{ sensor.name }}" class="list-group-item list-group-item-action">GPIO {{ sensor.gpio }} = {{ sensor.name }}</a>
            {% endfor %}
        </div>
    </div>
    <script src="{{ url_for('static', filename='scripts.js') }}"></script>
</body>
</html>
