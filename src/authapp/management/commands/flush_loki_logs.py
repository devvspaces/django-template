from django.core.management.base import BaseCommand
import logging

class Command(BaseCommand):
    help = 'Flush any queued logs to Loki'

    def handle(self, *args, **options):
        from django.conf import settings
        
        # Find Loki handler
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'flush') and handler.__class__.__name__ == 'LokiQueueHandler':
                self.stdout.write('Flushing Loki logs...')
                handler.flush()
                self.stdout.write(self.style.SUCCESS('Loki logs flushed successfully'))
                return
                
        self.stdout.write(self.style.ERROR('No LokiQueueHandler found'))