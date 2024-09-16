import os
import traceback
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        database=os.environ['PGDATABASE'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        port=os.environ['PGPORT']
    )
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())
    
    # Ensure all seats are not reserved
    cur.execute('UPDATE seats SET is_reserved = FALSE;')
    
    # Randomly pre-book 10-20% of seats
    total_seats = 80
    num_prebooked = random.randint(8, 16)  # 10-20% of 80 seats
    prebooked_seats = random.sample(range(1, total_seats + 1), num_prebooked)
    cur.execute('UPDATE seats SET is_reserved = TRUE WHERE seat_number = ANY(%s);', (prebooked_seats,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    app.logger.info(f"Pre-booked {num_prebooked} seats: {prebooked_seats}")

# Initialize the database on startup
with app.app_context():
    init_db()

@app.route('/')
def index():
    init_db()
    return render_template('index.html')

@app.route('/api/reset', methods=['POST'])
def reset_database():
    init_db()
    return jsonify({'message': 'Database reset successfully'})

@app.route('/api/seats', methods=['GET'])
def get_seats():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM seats ORDER BY seat_number;')
    seats = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(seats)

def find_best_seats(cur, num_seats, priority):
    # Get all seats
    cur.execute('SELECT COUNT(*) FROM seats;')
    total_seats = cur.fetchone()['count']
    
    # Get all available seats
    cur.execute('SELECT seat_number, (seat_number - 1) / 7 AS row FROM seats WHERE is_reserved = FALSE ORDER BY seat_number;')
    available_seats = cur.fetchall()
    
    # Get reserved seats
    cur.execute('SELECT seat_number FROM seats WHERE is_reserved = TRUE ORDER BY seat_number;')
    reserved_seats = [row['seat_number'] for row in cur.fetchall()]
    
    app.logger.info(f"Total seats: {total_seats}")
    app.logger.info(f"Available seats: {len(available_seats)}")
    app.logger.info(f"Reserved seats: {reserved_seats}")
    
    # Group seats by row
    seats_by_row = {}
    for seat in available_seats:
        row = seat['row']
        if row not in seats_by_row:
            seats_by_row[row] = []
        seats_by_row[row].append(seat['seat_number'])
    
    def find_consecutive_seats(row_seats, num_seats):
        for i in range(len(row_seats) - num_seats + 1):
            if all(row_seats[i+j] == row_seats[i]+j for j in range(num_seats)):
                return row_seats[i:i+num_seats]
        return None
    
    def calculate_seat_distance(seat1, seat2):
        row1, col1 = divmod(seat1 - 1, 7)
        row2, col2 = divmod(seat2 - 1, 7)
        return abs(row1 - row2) + abs(col1 - col2)
    
    def find_nearby_seats(available_seats, num_seats):
        available_seats.sort(key=lambda x: x['seat_number'])
        best_seats = []
        total_distance = float('inf')
        
        for i in range(len(available_seats) - num_seats + 1):
            seats = [seat['seat_number'] for seat in available_seats[i:i+num_seats]]
            distance = sum(calculate_seat_distance(seats[j], seats[j+1]) for j in range(num_seats-1))
            if distance < total_distance:
                best_seats = seats
                total_distance = distance
        
        return best_seats
    
    # Try to find seats based on priority
    if priority == 'comfort':
        # Implement comfort-based seat selection
        window_seats = [s['seat_number'] for s in available_seats if s['seat_number'] % 7 in (1, 0)]
        aisle_seats = [s['seat_number'] for s in available_seats if s['seat_number'] % 7 in (3, 5)]
        middle_seats = [s['seat_number'] for s in available_seats if s['seat_number'] % 7 in (2, 4, 6)]
        
        comfort_seats = window_seats + aisle_seats + middle_seats
        
        # Try to keep seats in the same row when possible
        for row, seats in seats_by_row.items():
            consecutive_seats = find_consecutive_seats(seats, num_seats)
            if consecutive_seats:
                return sorted(consecutive_seats, key=lambda x: comfort_seats.index(x))
        
        return comfort_seats[:num_seats]
    
    elif priority == 'together' or priority == 'default':
        # Try to find consecutive seats in a single row
        for row, seats in seats_by_row.items():
            consecutive_seats = find_consecutive_seats(seats, num_seats)
            if consecutive_seats:
                return consecutive_seats
        
        # If not possible, find nearby seats
        return find_nearby_seats(available_seats, num_seats)
    
    # If no suitable seats found, return any available seats
    return [seat['seat_number'] for seat in available_seats[:num_seats]]

@app.route('/api/reserve', methods=['POST'])
def reserve_seats():
    try:
        data = request.json
        num_seats = data['num_seats']
        priority = data.get('priority', 'default')  # 'comfort', 'together', or 'default'

        app.logger.info(f"Reservation request: {num_seats} seats with {priority} priority")

        if num_seats < 1 or num_seats > 7:
            return jsonify({'error': 'Number of seats must be between 1 and 7'}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Start a transaction
            cur.execute('BEGIN;')

            # Check available seats
            cur.execute('SELECT COUNT(*) FROM seats WHERE is_reserved = FALSE;')
            available_seats_count = cur.fetchone()['count']

            if available_seats_count < num_seats:
                conn.rollback()
                return jsonify({'error': f'Not enough seats available. Only {available_seats_count} seats left.'}), 400

            best_seats = find_best_seats(cur, num_seats, priority)

            if len(best_seats) < num_seats:
                conn.rollback()
                return jsonify({'error': f'Could not find {num_seats} seats matching the criteria. Try a different priority or fewer seats.'}), 400

            # Reserve the seats
            cur.execute('UPDATE seats SET is_reserved = TRUE WHERE seat_number = ANY(%s);', (best_seats,))

            # Commit the transaction
            conn.commit()

            app.logger.info(f"Successfully reserved seats: {best_seats}")

            return jsonify({'reserved_seats': best_seats})

        except Exception as e:
            conn.rollback()
            app.logger.error(f"Database error: {str(e)}")
            return jsonify({'error': 'A database error occurred. Please try again later.'}), 500

        finally:
            cur.close()
            conn.close()

    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500

@app.route('/api/test_db', methods=['GET'])
def test_db_connection():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Database connection successful'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
