from _decimal import Decimal as D
from duet_admin.settingsCode import GPF_INTEREST_RATE as g_interest_rate
from duet_admin.models import Settings


class SalarySheetCalculations:
	@staticmethod
	def get_gpf_interest_rate():
		return Settings.objects.get(code=g_interest_rate).value

	@staticmethod
	def calculate_percentage_from_basic(basic_pay, personal_pay, percentage):
		return D((basic_pay + personal_pay) * percentage / 100)

	@staticmethod
	def calculate_default_values(basic_pay, personal_pay, default_value, is_percentage):
		if is_percentage:
			return (basic_pay + personal_pay) * default_value / 100
		else:
			return default_value

	@staticmethod
	def calculate_gpf_interest(date, deduction):
		interest_rate = SalarySheetCalculations.get_gpf_interest_rate()

		def get_working_month(date):
			month = date.month
			if month > 6:
				return 12 - (6 + month) % interest_rate
			else:
				return 13 - (6 + month) % interest_rate

		return round(deduction * D((interest_rate / 12 * get_working_month(date))/100), 2)

	@staticmethod
	def calculate_gpf_interest_for_year(deduction):
		return D(deduction * SalarySheetCalculations.get_gpf_interest_rate() /100);



