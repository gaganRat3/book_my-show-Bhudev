from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Start background services when Django is ready"""
        # Import here to avoid circular imports
        from .scheduler import start_seat_cleanup_scheduler
        
        # Only start scheduler in main process (not during migrations, etc.)
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            start_seat_cleanup_scheduler()
