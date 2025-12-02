Seat addition:
- templates/seat.html — Added 2 seats to Row X and Row W in the top-left1 section (seats 1 and 2) using class "seat teal" and data-ids 'X4-1', 'X4-2', 'W4-1', 'W4-2'.

Notes:
- No other files changed.
- Backend seat population script still has larger seat counts for X and W (33 and 34). If you'd like seeded seats aligned with front-end, we can update `events/management/commands/populate_seats.py` in a follow-up change.