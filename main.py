import os
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

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
    conn.commit()
    cur.close()
    conn.close()

# Initialize the database on startup
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/seats', methods=['GET'])
def get_seats():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM seats ORDER BY seat_number;')
    seats = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(seats)

@app.route('/api/reserve', methods=['POST'])
def reserve_seats():
    data = request.json
    num_seats = data['num_seats']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Start a transaction
        cur.execute('BEGIN;')

        # Get available seats
        cur.execute('SELECT seat_number FROM seats WHERE is_reserved = FALSE ORDER BY seat_number LIMIT %s FOR UPDATE;', (num_seats,))
        available_seats = cur.fetchall()

        if len(available_seats) < num_seats:
            conn.rollback()
            return jsonify({'error': 'Not enough seats available'}), 400

        # Reserve the seats
        seat_numbers = [seat['seat_number'] for seat in available_seats]
        cur.execute('UPDATE seats SET is_reserved = TRUE WHERE seat_number = ANY(%s);', (seat_numbers,))

        # Commit the transaction
        conn.commit()

        return jsonify({'reserved_seats': seat_numbers})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
