CREATE TABLE IF NOT EXISTS Buildings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    street VARCHAR(100),
    house_number VARCHAR(10),
    hostname VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS PIR_Sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rp_hostname VARCHAR(50),
    sensor_number INT,
    postbox_number VARCHAR(50),
    port INT,
    FOREIGN KEY (rp_hostname) REFERENCES Buildings(hostname)
);

CREATE TABLE IF NOT EXISTS Ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname VARCHAR(50),
    port INT,
    state VARCHAR(10),
    FOREIGN KEY (hostname) REFERENCES Buildings(hostname)
);

CREATE TABLE IF NOT EXISTS Devices (
    pin INTEGER PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL
);
