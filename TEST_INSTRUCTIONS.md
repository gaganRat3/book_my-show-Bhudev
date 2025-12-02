How to verify seat changes locally

1. Start Django dev server and visit the seat layout page:

```powershell
# Activate your virtual env (if using venv) and run:
python manage.py runserver
# Visit http://127.0.0.1:8000/seat or the route you use for seat selection
```

2. Check the seats for Row X and Row W in the top-left section — seat numbers 1 and 2 should now be visible.

3. If you want to reflect these changes in the backend DB (seeded seats), run the management command to populate seats (note: the command uses seat_ranges and will still very likely create many seats):

```powershell
python manage.py populate_seats
```

4. Optional: Align backend with front-end if you prefer smaller seat counts for X and W (follow-up change).