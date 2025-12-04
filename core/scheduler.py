import threading
import time
from django.core.management import call_command
from django.conf import settings


class SeatCleanupScheduler:
    """Background scheduler for cleaning up expired seat holds"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.cleanup_interval = getattr(settings, 'SEAT_CLEANUP_INTERVAL', 60)  # seconds
    
    def start(self):
        """Start the background cleanup scheduler"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
        print(f"[SeatCleanup] Started background cleanup scheduler (interval: {self.cleanup_interval}s)")
    
    def stop(self):
        """Stop the background cleanup scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("[SeatCleanup] Stopped background cleanup scheduler")
    
    def _cleanup_loop(self):
        """Main cleanup loop running in background thread"""
        while self.running:
            try:
                call_command('cleanup_expired_holds', verbosity=0)
            except Exception as e:
                print(f"[SeatCleanup] Error during cleanup: {e}")
            
            # Sleep for the specified interval
            time.sleep(self.cleanup_interval)


# Global scheduler instance
_scheduler = None

def start_seat_cleanup_scheduler():
    """Start the global seat cleanup scheduler"""
    global _scheduler
    if not _scheduler:
        _scheduler = SeatCleanupScheduler()
    _scheduler.start()

def stop_seat_cleanup_scheduler():
    """Stop the global seat cleanup scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()