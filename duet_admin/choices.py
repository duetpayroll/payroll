import datetime
YEAR_CHOICES = [(r,r) for r in range(1984, datetime.date.today().year+1)]
GENDER = (
        ('', '----'),
        ('m', 'Male'),
        ('f', 'Female')
    )

EMPLOYEE_CATEGORY = (
        ('', '----'),
        ('t', 'Teacher'),
        ('o', 'Officer'),
        ('s', 'Stuff')
    )

DEPARTMENT_TYPE = (
        ('', '----'),
        ('ac' , "Academic"),
        ('ad', 'Administrative')
    )
PAYMENT_TYPE = (
        ('y', 'Yearly'),
        ('hy', 'Half Yearly'),
        ('m', 'Monthly'),
        ('o', 'One Time')
    )

EMPLOYEE_CLASS = (
        ('', '----'),
        ('fi', 'First Class'),
        ('se', 'Second Class'),
        ('th', 'Third Class'),
        ('fo', 'Fourth Class')
    )

ALLOWANCE_DEDUCTION_TYPE =(
        ('', '----'),
        ('p', 'Pay'),
        ('a', 'Allowance'),
        ('d' , 'Deduction')
    )

ADVANCE_CATEGORY = (
    ('', '----'),
    ('g', 'GPF Advance'),
    ('h', 'Home Loan'),
    )

REPORT_TYPE = (
    ('d', 'Details'),
    ('s', 'Summary'),
    )


