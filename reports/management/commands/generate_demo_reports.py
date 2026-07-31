from django.core.management.base import BaseCommand
from django.utils import timezone

from reports.models import Report


class Command(BaseCommand):

    help = "Create demo reports"

    def handle(self, *args, **kwargs):

        reports = [

            {
                "title": "Monthly Attendance Report",
                "category": "attendance",
                "description": "Generated attendance report for members"
            },

            {
                "title": "Monthly Payment Report",
                "category": "finance",
                "description": "Generated member contribution report"
            },

            {
                "title": "Compliance Report",
                "category": "compliance",
                "description": "Generated compliance status report"
            },

        ]

        for item in reports:

            report = Report.objects.create(
                title=item["title"],
                category=item["category"],
                description=item["description"],
                created_at=timezone.now()
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created report: {report.title}"
                )
            )
