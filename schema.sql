-- Drop the table if it exists
DROP TABLE IF EXISTS seats;

-- Create the seats table
CREATE TABLE seats (
    seat_number INTEGER PRIMARY KEY,
    is_reserved BOOLEAN NOT NULL DEFAULT FALSE
);

-- Insert 80 seats
INSERT INTO seats (seat_number, is_reserved)
SELECT generate_series(1, 80), FALSE;

-- Pre-book some seats (for testing purposes)
UPDATE seats SET is_reserved = TRUE WHERE seat_number IN (5, 10, 15, 20, 25);
