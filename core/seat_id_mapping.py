def backend_to_frontend_seat_id(seat_id):
    import re
    match = re.match(r'G-(\d+)', seat_id)
    if match:
        num = int(match.group(1))
        if 13 <= num <= 29:
            return f'G2-{num - 12}'
    return seat_id
