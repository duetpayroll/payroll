from django.core.management.base import BaseCommand
from employee.models import Employee, Designation
from duet_admin.models import Department
from duet_account.models import Grade
from django.contrib.auth.models import Group
from datetime import date

class Command(BaseCommand):
    help = 'our help string comes here'

    def _create_employees(self):
        grade_09 = Grade.objects.get(grade_no=9)
        grade_05 = Grade.objects.get(grade_no=5)
        grade_03 = Grade.objects.get(grade_no=3)
        lecturer = Designation.objects.get(name='Lecturer')
        associate_professor = Designation.objects.get(name='Associate Professor')
        professor = Designation.objects.get(name='Professor')
        dept_cse = Department.objects.get(acronym='CSE')

        group_admin = Group.objects.get(name='admin')
        group_accountant = Group.objects.get(name='accountant')

        today = date.today()

        employee_1 = Employee(first_name='Dr. Fazlul Hasan', last_name='Siddiqui', username='fh.Siddiqui',is_staff=True, is_superuser=True,
                 email='fazlul.siddiqui@duet.ac.bd', category='t', grade=grade_05, designation=associate_professor,
                 department=dept_cse, gender='m', dob=today)
        employee_1.set_password('1234')
        employee_1.save()
        employee_1.groups.add(group_admin)
        employee_1.groups.add(group_accountant)

        employee_2 = Employee(first_name='Sabah Binte', last_name='Noor', username='sb.noor', password='1234',
        email='sabah@duet.ac.bd', is_staff=True, is_superuser=True, category='t', grade=grade_09, designation=lecturer,
                         department=dept_cse, gender='f', dob=today.replace(year=1991, month=6, day=30))

        employee_2.set_password('1234')
        employee_2.save()
        employee_2.groups.add(group_admin)
        employee_2.groups.add(group_accountant)

        employee_3 = Employee(first_name='Dr. Mohammad Abul', last_name='Kashem', username='ma.kashem', password='1234',
                 email='drkashemll@duet.ac.bd', category='t', grade=grade_03,
                 designation=professor, department=dept_cse, gender='m', dob=today)
        employee_3.set_password('1234')
        employee_3.save()

        employee_3 = Employee(first_name='Dr. Mohammad Nasim', last_name='Akhter', username='mn.nasim', password='1234',
                 email='nasim_duet@yahoo.com', category='t', grade=grade_03, designation=professor,
                 department=dept_cse, gender='m', dob=today)
        employee_3.set_password('1234')
        employee_3.save()

        employee_3 = Employee(first_name='Dr. Mohammad Abdur', last_name='Rouf', username='ma.rouf', password='1234',
                 email='marouf.cse@duet.ac.bd', category='t', grade=grade_03, designation=professor,
                 department=dept_cse, gender='m', dob=today)
        employee_3.set_password('1234')
        employee_3.save()
        employee_3 = Employee(first_name='Dr. Md. Obaidur', last_name='Rahman', username='mo.rahman', password='1234',
                 email='mdobaidurrahman@dgmail.com', category='t', grade=grade_05, designation=associate_professor,
                 department=dept_cse, gender='m', dob=today)
        employee_3.set_password('1234')
        employee_3.save()

    def handle(self, *args, **options):
        self._create_employees()