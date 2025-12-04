# Real-time Seat Booking Implementation

## Overview

Implemented WebSocket-based real-time seat booking system using Django Channels.

## What Was Added

### 1. Backend Components

#### Django Channels Configuration

- Installed: `channels`, `daphne`, `channels-redis`
- Updated `settings.py`:
  - Added `daphne` and `channels` to INSTALLED_APPS
  - Configured ASGI application
  - Set up in-memory channel layer for development

#### WebSocket Consumer (`core/consumers.py`)

- `SeatConsumer`: Handles WebSocket connections
- Manages group membership for broadcasting
- Sends seat updates to all connected clients

#### Routing (`core/routing.py`)

- WebSocket URL: `ws://localhost:8000/ws/seats/`
- Routes WebSocket connections to SeatConsumer

#### ASGI Configuration (`bookmyshow/asgi.py`)

- Updated to support both HTTP and WebSocket protocols
- Configured middleware stack for WebSocket authentication

#### Signal Handlers (`core/models.py`)

- `broadcast_seat_booked`: Triggered when SelectedSeat is created
- Broadcasts seat booking to all connected clients via WebSocket
- Also broadcasts seat unbooking when users are deleted

### 2. Frontend Components

#### WebSocket Client (`templates/seat.html`)

- Establishes WebSocket connection on page load
- Listens for real-time seat updates
- Automatically marks seats as booked when updates arrive
- Visual animation when seats are booked
- Auto-reconnect on connection loss

## How It Works

1. **User A** selects seats and completes payment
2. Server saves `SelectedSeat` records
3. Signal triggers and broadcasts seat numbers via WebSocket
4. **All connected users** (B, C, D...) receive the update instantly
5. Seats turn red with animation in real-time
6. Seats become unclickable immediately

## Testing Instructions

1. **Start the server:**

   ```bash
   python manage.py runserver
   ```

2. **Open multiple browser windows:**

   - Window 1: http://localhost:8000/seats/
   - Window 2: http://localhost:8000/seats/ (incognito/private mode)
   - Window 3: http://localhost:8000/seats/ (different browser)

3. **Test the flow:**

   - In Window 1: Select seats and proceed to payment
   - In Window 1: Upload payment screenshot and confirm
   - **Watch Windows 2 & 3**: Seats should turn red instantly without refresh!

4. **Check browser console** for WebSocket logs:
   - `[WebSocket] Connection established`
   - `[WebSocket] Received: {type: "seat_update", seats: ["A-1", "A-2"]}`
   - `[WebSocket] Marking seat as booked: A-1`

## Production Considerations

For production deployment, replace in-memory channel layer with Redis:

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## Features

- ✅ Real-time seat updates across all clients
- ✅ Visual feedback animation when seats are booked
- ✅ Automatic reconnection on connection loss
- ✅ No page refresh required
- ✅ Works with ngrok/production URLs
- ✅ Prevents double-booking with instant updates

## Files Modified

1. `bookmyshow/settings.py` - Added Channels configuration
2. `bookmyshow/asgi.py` - Updated for WebSocket support
3. `core/consumers.py` - Created WebSocket consumer
4. `core/routing.py` - Created WebSocket routing
5. `core/models.py` - Added signal for broadcasting
6. `templates/seat.html` - Added WebSocket client code
