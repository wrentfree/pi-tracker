CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    date DATE,
    name TEXT,
    address TEXT,
    street_address TEXT,
    city TEXT,
    zipcode TEXT,
    age_at_arrest INTEGER,
    arresting_agency TEXT,
    charges TEXT,
    police_id VARCHAR(255),
    UNIQUE(date, name, charges, police_id)
);

CREATE TABLE schedule (
    id SERIAL PRIMARY KEY,
    date DATE,
    local_success BOOLEAN,
    heroku_success BOOLEAN,
    drive_success BOOLEAN,
    UNIQUE(date)
);