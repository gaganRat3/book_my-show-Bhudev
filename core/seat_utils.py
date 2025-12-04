def normalize_seat_id(seat_id):
    import re
    match = re.match(r'G2-(\d+)', seat_id)
    if match:
        num = int(match.group(1))
        return f'G-{num + 12}'
    return seat_id
