from django.core.management.base import BaseCommand
from duet_admin.models import Settings
from duet_account.models import AllowanceDeduction
from duet_admin import settingsCode

class Command(BaseCommand):
    help = 'our help string comes here'

    def _create_settings(self):
       #Settings(name="GPF Interest Rate", code="gpf_interest", value=13).save()
       Settings(name="Maximum GPF Advance", code=settingsCode.NO_GPF_ADVANCE, value=3).save()
       Settings(name="Maximum Home loan", code=settingsCode.NO_HOME_LOAN, value=1).save()

    def _create_allowance_deduction(self):
        AllowanceDeduction(name='Home Loan', code='h.loan', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=13).save()

    def handle(self, *args, **options):
        self._create_settings()
        self._create_allowance_deduction()