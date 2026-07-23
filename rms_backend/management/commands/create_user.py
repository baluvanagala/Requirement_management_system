from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a user with email, password and optional mobile"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email address")
        parser.add_argument("--password", required=True, help="Password")
        parser.add_argument(
            "--mobile", required=False, help="Mobile number (10 digits)"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="If set, reset password for existing user",
        )

    def handle(self, *args, **options):
        from rms_backend.models import CustomUser

        email = options["email"]
        password = options["password"]
        mobile = options.get("mobile") or "0000000000"
        username = email.split("@")[0]

        existing = CustomUser.objects.filter(email__iexact=email).first()
        if existing:
            if options.get("force"):
                existing.set_password(password)
                if mobile:
                    existing.mobile = mobile
                existing.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated password for existing user: {existing.pk} {existing.email}"
                    )
                )
                return
            else:
                self.stdout.write(
                    self.style.WARNING(f"User with email {email} already exists")
                )
                return

        user = CustomUser.objects.create_user(
            username=username, email=email, password=password, mobile=mobile
        )
        self.stdout.write(self.style.SUCCESS(f"Created user: {user.pk} {user.email}"))
