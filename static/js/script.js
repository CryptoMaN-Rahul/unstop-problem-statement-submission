document.addEventListener('DOMContentLoaded', () => {
    const coachSvg = document.getElementById('coach-svg');
    const numSeatsInput = document.getElementById('num-seats');
    const prioritySelect = document.getElementById('priority');
    const reserveBtn = document.getElementById('reserve-btn');
    const reservationResult = document.getElementById('reservation-result');
    const reservationInfo = document.getElementById('reservation-info');

    const seatWidth = 30;
    const seatHeight = 30;
    const seatSpacing = 10;
    const rowSpacing = 20;

    let seats = [];

    function createSeat(seatNumber, x, y) {
        const seat = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        seat.setAttribute('x', x);
        seat.setAttribute('y', y);
        seat.setAttribute('width', seatWidth);
        seat.setAttribute('height', seatHeight);
        seat.setAttribute('class', 'seat available');
        seat.setAttribute('data-seat-number', seatNumber);
        coachSvg.appendChild(seat);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x + seatWidth / 2);
        text.setAttribute('y', y + seatHeight / 2);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'central');
        text.setAttribute('font-size', '12');
        text.textContent = seatNumber;
        coachSvg.appendChild(text);
    }

    function createCoachLayout() {
        let seatNumber = 1;
        for (let row = 0; row < 11; row++) {
            for (let col = 0; col < 7; col++) {
                const x = col * (seatWidth + seatSpacing) + seatSpacing;
                const y = row * (seatHeight + rowSpacing) + rowSpacing;
                createSeat(seatNumber, x, y);
                seatNumber++;
            }
        }
        // Last row with 3 seats
        for (let col = 0; col < 3; col++) {
            const x = col * (seatWidth + seatSpacing) + seatSpacing;
            const y = 11 * (seatHeight + rowSpacing) + rowSpacing;
            createSeat(seatNumber, x, y);
            seatNumber++;
        }
    }

    function updateSeats() {
        fetch('/api/seats')
            .then(response => response.json())
            .then(data => {
                seats = data;
                const availableSeats = seats.filter(seat => !seat.is_reserved).length;
                const reservedSeats = seats.filter(seat => seat.is_reserved).length;
                reservationInfo.innerHTML = `
                    <p>Total seats: ${seats.length}</p>
                    <p>Available seats: ${availableSeats}</p>
                    <p>Reserved seats: ${reservedSeats}</p>
                `;
                seats.forEach(seat => {
                    const seatElement = document.querySelector(`[data-seat-number="${seat.seat_number}"]`);
                    if (seatElement) {
                        seatElement.setAttribute('class', `seat ${seat.is_reserved ? 'reserved' : 'available'}`);
                    }
                });
            });
    }

    function reserveSeats() {
        const numSeats = parseInt(numSeatsInput.value);
        const priority = prioritySelect.value;
        if (numSeats < 1 || numSeats > 7) {
            alert('Please enter a number between 1 and 7');
            return;
        }

        fetch('/api/reserve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ num_seats: numSeats, priority: priority }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    reservationResult.textContent = `Error: ${data.error}`;
                } else {
                    reservationResult.textContent = `Reserved seats: ${data.reserved_seats.join(', ')}`;
                    updateSeats();
                }
            });
    }

    function resetDatabase() {
        fetch('/api/reset', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                updateSeats();
                reservationResult.textContent = 'Database reset. Some seats are now pre-booked.';
            })
            .catch(error => console.error('Error resetting database:', error));
    }

    createCoachLayout();
    resetDatabase();  // Call this function when the page loads

    reserveBtn.addEventListener('click', reserveSeats);
});
