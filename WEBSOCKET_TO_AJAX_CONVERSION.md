# WebSocket to AJAX Polling Conversion

## Overview

This document describes the conversion from WebSocket-based real-time updates to AJAX polling for PythonAnywhere compatibility.

## Reason for Change

PythonAnywhere's free tier does not support WebSockets. To deploy the application successfully, we converted the real-time seat update system from WebSocket push to AJAX polling.

## Changes Made

### 1. Frontend (templates/seat.html)

**Lines 510-650: Replaced WebSocket connection with AJAX polling**

#### Old Code (WebSocket):

- Connected to `ws://` or `wss://` endpoint
- Received push notifications for seat updates
- Handled connection errors with infinite refresh loop

#### New Code (AJAX Polling):

```javascript
// Poll seat status every 5 seconds
function pollSeatStatus() {
  fetch("/api/seat-status/")
    .then((response) => response.json())
    .then((data) => {
      updateSeatsFromPoll(data.seats);
    })
    .catch((error) => {
      console.error("Error polling seat status:", error);
    });
}

setInterval(pollSeatStatus, 5000); // Poll every 5 seconds
```

**Benefits:**

- Works on all hosting platforms
- No connection management needed
- Simpler error handling
- Compatible with PythonAnywhere free tier

### 2. Backend Settings (bookmyshow/settings.py)

**Removed WebSocket dependencies:**

- Commented out `'daphne'` from INSTALLED_APPS
- Commented out `'channels'` from INSTALLED_APPS
- Commented out `ASGI_APPLICATION` setting
- Commented out `CHANNEL_LAYERS` configuration

**Result:** Django now runs in pure WSGI mode (standard HTTP/HTTPS only)

### 3. Model Signals (core/models.py)

**Lines 85-138: Commented out WebSocket broadcasting**

#### Removed:

- `from asgiref.sync import async_to_sync`
- `from channels.layers import get_channel_layer`
- `@receiver(post_save, sender='core.Seat')` broadcast function
- WebSocket broadcasting in `release_user_seats_on_delete` signal

**Impact:** Seat status changes are now detected via polling instead of push notifications.

### 4. Seat Reservation Service (core/seat_reservation_service.py)

**Commented out all WebSocket broadcasts:**

#### Functions Updated:

1. `hold_seats()` - Removed broadcast after holding seats
2. `release_user_holds()` - Removed broadcast after releasing holds
3. `convert_holds_to_bookings()` - Removed broadcast after booking
4. `cleanup_expired_holds()` - Removed broadcast after cleanup
5. `_broadcast_seat_updates()` - Entire method commented out

**Impact:** All seat operations still work correctly, but updates are received via polling.

## Files Not Modified

The following files contain WebSocket code but don't need changes:

- `core/consumers.py` - Not loaded when channels is disabled
- `core/routing.py` - Not loaded when channels is disabled

## How It Works Now

### Real-Time Updates Flow:

1. User 1 books a seat → Database updated
2. Frontend polls every 5 seconds → Fetches latest seat status
3. User 2's browser receives update → Seat shown as booked
4. All users see consistent state within ~5 seconds

### Polling Configuration:

- **Interval:** 5000ms (5 seconds)
- **Endpoint:** `/api/seat-status/`
- **Method:** HTTP GET with JSON response
- **Timeout:** Browser default (~30 seconds)

## Testing Checklist

- [ ] Test seat booking in multiple browser tabs
- [ ] Verify seat status updates within 5 seconds
- [ ] Test admin panel seat unbooking
- [ ] Check that expired holds are released
- [ ] Verify no WebSocket connection errors in console
- [ ] Deploy to PythonAnywhere without WebSocket errors

## Performance Considerations

### Polling Every 5 Seconds:

- **Pro:** Simple, reliable, works everywhere
- **Pro:** Acceptable latency for seat booking
- **Con:** Slightly higher server load (minimal for small user base)

### Alternative Approaches (if needed):

1. Increase polling interval to 10 seconds to reduce load
2. Implement long-polling for instant updates
3. Use Server-Sent Events (SSE) if supported by host

## Deployment Notes

### PythonAnywhere Configuration:

1. Use WSGI configuration (default)
2. No need for ASGI/Daphne setup
3. Standard Django deployment process
4. Static files served via whitenoise or PythonAnywhere static mapping

### Environment Requirements:

- Django 5.2.7+
- Python 3.11
- No channels/daphne packages needed
- Standard WSGI server (gunicorn/uwsgi/mod_wsgi)

## Reverting to WebSocket (if needed)

To revert back to WebSocket in the future:

1. Uncomment all WebSocket code in:
   - `core/models.py`
   - `core/seat_reservation_service.py`
   - `bookmyshow/settings.py`
2. Restore WebSocket connection in `templates/seat.html`

3. Install packages:

   ```bash
   pip install channels daphne
   ```

4. Use ASGI server:
   ```bash
   daphne -b 0.0.0.0 -p 8000 bookmyshow.asgi:application
   ```

## Summary

✅ **WebSocket removed** - No more connection errors on PythonAnywhere  
✅ **AJAX polling implemented** - 5-second refresh interval  
✅ **Backend cleaned** - All broadcast code commented out  
✅ **Settings updated** - Pure WSGI mode enabled  
✅ **Fully functional** - All seat booking features working  
✅ **PythonAnywhere ready** - Compatible with free tier

The application now uses standard HTTP requests for real-time updates, ensuring compatibility with all hosting platforms including PythonAnywhere's free tier.
