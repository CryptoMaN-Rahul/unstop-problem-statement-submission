-- Drop the table if it exists
DROP TABLE IF EXISTS seats;

-- Create the seats table
CREATE TABLE seats (
    seat_number INTEGER PRIMARY KEY,
    is_reserved BOOLEAN NOT NULL DEFAULT FALSE
);

-- Insert 80 seats
INSERT INTO seats (seat_number)
SELECT generate_series(1, 80);
