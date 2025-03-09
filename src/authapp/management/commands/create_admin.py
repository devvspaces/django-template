from django.core.management.base import BaseCommand

from authapp.models import User

username = "admin"
password = "admin"


class Command(BaseCommand):
    help = "Creating Super User"

    def handle(self, *args, **options):
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS("Super User already exists"))
            return
        try:
            User.objects.create_superuser(
                username=username,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Completed Successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error: %s" % e))
