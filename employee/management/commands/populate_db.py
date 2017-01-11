from django.core.management.base import BaseCommand
from employee.models import Employee, Designation
from duet_admin.models import Department
from duet_account.models import EmployeeClass, Grade, AllowanceDeduction
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'our help string comes here'

    def _create_designations(self):
        Designation(name='Professor').save()
        Designation(name='Associate Professor').save()
        Designation(name='Assistant Professor').save()
        Designation(name='Lecturer').save()

    def _create_departments(self):
        Department(name='Computer Science and Engineering', acronym='CSE', type='ac').save()
        Department(name='Electrical Electronics Engineering', acronym='EEE', type='ac').save()
        Department(name='Mechanical Engineering', acronym='ME', type='ac').save()
        Department(name='Civil Engineering', acronym='CE', type='ac').save()
        Department(name='Textile Engineering', acronym='TE', type='ac').save()
        Department(name='Industrial Production Engineering', acronym='IPE', type='ac').save()
        Department(name='Architecture', acronym='ARCH', type='ac').save()
        Department(name='Exam Section', type='ad').save()
        Department(name='Controller Section',type='ad').save()
        Department(name='Academic Section',type='ad').save()
        Department(name='Engineering Section',type='ad').save()
        Department(name='Transport Section',type='ad').save()

    def _create_employee_class(self):
        EmployeeClass(name='First Class').save()
        EmployeeClass(name='Second Class').save()
        EmployeeClass(name='Third Class').save()
        EmployeeClass(name='Fourth Class').save()

    def _create_employee_grade(self):

        first_class = EmployeeClass.objects.get(name='First Class')

        Grade(grade_no=1, employee_class=first_class, description='Tk 78000 (Fixed)').save()
        Grade(grade_no=2, employee_class=first_class, description= 'Tk 66000-68480-71050-73720-76790').save()
        Grade(grade_no=3, employee_class=first_class, description= 'Tk 56500-58760-61120-63570-'
                                                                   '66120-68770-71530-74400').save()
        Grade(grade_no=4, employee_class=first_class, description= 'Tk 50000-52000-54080-56250-58500-60840-63280-65820-'
                                                                   '68460-71200' ).save()
        Grade(grade_no=5, employee_class=first_class, description= 'Tk 43000-44940-46970-49090-51300-53610-56030-58560-'
                                                                   '61200-63960-66840-69850' ).save()
        Grade(grade_no=6, employee_class=first_class, description= 'Tk 35500-37280-39150-41110-43170-45330-47600-49980-'
                                                                   '52480-55110-57870-60770-63810-67010' ).save()
        Grade(grade_no=7, employee_class=first_class, description='TK ''29000-30450-31980-33580-35260-37030-38890-40840'
                                                                  '-42890-45040-47300-49670-'
                                                                 '52160-54770-57510-60390-63410').save()
        Grade(grade_no=8, employee_class=first_class, description='TK 23000-24150-25360-26630-27970-29370-30840-32390-'
                                                                  '34010-35720-37510-39390-41360-43430-45610-'
                                                                  '47900-50300-52820-55470').save()
        Grade(grade_no=9, employee_class=first_class, description='Tk 22000-23100-24260-25480-26760-28100-29510-30990-'
                                                                  '32540-34170-35880-37680-39570-41550-43630-45820-48120'
                                                                  '-50530-53060').save()

    def _create_allowance_deduction(self):

        #### Pay ####
        AllowanceDeduction(name='Basic Pay', code='bp', category='p', is_applicable=True, is_percentage=False, payment_type='m', order=1).save()
        AllowanceDeduction(name='Personal Pay', code='pp', category='p', is_applicable=True, is_percentage=False, payment_type='m', order=2).save()

        #### Allowances ####
        AllowanceDeduction(name='Dearness Allowance', code='da', category='a', is_applicable=False, is_percentage=False,
                           payment_type='m',order=3).save()
        AllowanceDeduction(name='House Rent Allowance ', category='a', is_applicable=True, is_percentage=True,
                           payment_type='m', order=4).save()
        AllowanceDeduction(name='Medical Allowance ', category='a', is_applicable=True, is_percentage=False,
                           payment_type='m', order=5).save()
        AllowanceDeduction(name='CA/Honorium ', category='a', is_applicable=True, is_percentage=False,
                           payment_type='o', order=6).save()
        AllowanceDeduction(name='Cell Phone Allowance', category='a', is_applicable=True, is_percentage=False,
                           payment_type='m', order=7).save()
        AllowanceDeduction(name='Education Allowance ', category='a', is_applicable=True, is_percentage=False,
                           payment_type='m', order=8).save()
        AllowanceDeduction(name='Festival Allowance ', category='a', is_applicable=True, is_percentage=False,
                           payment_type='y', order=9).save()
        AllowanceDeduction(name='Professional Allowance ', category='a', is_applicable=True, is_percentage=False,
                           payment_type='y', order=10).save()
        AllowanceDeduction(name='Bangla New Year Allowance ', category='a', is_applicable=True, is_percentage=False,
                           payment_type='y', order=11).save()
        AllowanceDeduction(name='Others', category='a', is_applicable=True, is_percentage=False,
                           payment_type='m', order=12).save()

        #### Deductions ####

        AllowanceDeduction(name='G. Providentfund Subscription', code='gpf', category='d', is_applicable=True, \
                                                                                               is_percentage=False,
                           payment_type='m', order=1).save()
        AllowanceDeduction(name='Benevolent Fund', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=2).save()
        AllowanceDeduction(name='Group Insurance', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=3).save()
        AllowanceDeduction(name='House Rent', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=4).save()
        AllowanceDeduction(name='Gas Bill', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=5).save()
        AllowanceDeduction(name='Electricity Bill', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=6).save()
        AllowanceDeduction(name='Telephone Bill', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=7).save()
        AllowanceDeduction(name='G. House Rent', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=8).save()
        AllowanceDeduction(name='Vehicle Fare', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=9).save()
        AllowanceDeduction(name='Club Subscription', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=10).save()
        AllowanceDeduction(name='Income Tax on Salary', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=11).save()
        AllowanceDeduction(name='Revenue Stamp + Others', category='d', is_applicable=True, is_percentage=False,
                           payment_type='m', order=12).save()

    def _create_group(self):
        Group(name='admin').save()
        Group(name='accountant').save()


    def handle(self, *args, **options):
        self._create_designations()
        self._create_departments()
        self._create_employee_class()
        self._create_employee_grade()
        self._create_allowance_deduction()
        self._create_group()
