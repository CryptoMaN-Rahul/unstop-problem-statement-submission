# Train Seat Reservation System
# Try here -> https://train-seat-reservation-rahulmadwalkar5.replit.app/
This project is a train seat reservation system built using Flask and Vanilla JS with PostgreSQL for data storage.

## Features

- View coach layout with 80 seats
- Reserve seats with priority options (comfort, together, or default)
- Automatically allocate best available seats based on priority
- Reset database with random pre-booked seats

## Prerequisites

- Python 3.8+
- PostgreSQL

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/CryptoMaN-Rahul/unstop-problem-statement-submission
   cd unstop-problem-statement-submission
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the PostgreSQL database and update the environment variables:
   ```
   export PGHOST=your_host
   export PGDATABASE=your_database
   export PGUSER=your_user
   export PGPASSWORD=your_password
   export PGPORT=your_port
   ```

## Running the Application Locally

1. Start the Flask server:
   ```
   python main.py
   ```
   This will initialize the database, create the necessary tables, and pre-book some random seats.

2. Open a web browser and navigate to `http://localhost:5000` to use the application.

## Deployment to Heroku

1. Create a Heroku account and install the Heroku CLI.

2. Log in to Heroku:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

4. Add the PostgreSQL add-on to your Heroku app:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. Set the necessary environment variables:
   ```
   heroku config:set PGHOST=your_heroku_db_host
   heroku config:set PGDATABASE=your_heroku_db_name
   heroku config:set PGUSER=your_heroku_db_user
   heroku config:set PGPASSWORD=your_heroku_db_password
   heroku config:set PGPORT=your_heroku_db_port
   ```

6. Deploy your application to Heroku:
   ```
   git push heroku main
   ```

7. Open your application:
   ```
   heroku open
   ```

## API Endpoints

- `GET /api/seats`: Get the current state of all seats
- `POST /api/reserve`: Reserve seats
- `POST /api/reset`: Reset the database
- `GET /api/test_db`: Test the database connection

## Code Structure

- `main.py`: Contains the Flask application and all the backend logic
- `schema.sql`: SQL script for creating the database schema
- `static/css/style.css`: CSS styles for the frontend
- `static/js/script.js`: JavaScript code for the frontend
- `templates/index.html`: HTML template for the main page
- `Procfile`: Specifies the commands that are executed by the app on startup (for Heroku)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
