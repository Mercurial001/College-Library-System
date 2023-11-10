from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User, UserCourse, UserNumberLocation, UserPosition, UserDepartment
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class MaterialType(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self):
        return self.title


class Subtype(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self):
        return self.title


class BookStatus(models.Model):
    objects = None
    status = models.CharField(max_length=255)

    def __str__(self):
        return self.status


class BriefTitle(models.Model):
    book_status = models.ForeignKey(BookStatus, related_name='status_book', on_delete=models.CASCADE, default=2)
    subject = models.CharField(max_length=255, null=True)
    date_inputted_added = models.DateTimeField(auto_now_add=True)
    material = models.ForeignKey(MaterialType, related_name='material', on_delete=models.CASCADE)
    sub_type = models.ForeignKey(Subtype, related_name='sub_type', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    call_number = models.CharField(max_length=255)
    edition = models.CharField(max_length=255)
    # Standard Numbers
    lccn = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=255, blank=True, null=True)
    issn = models.CharField(max_length=255, blank=True, null=True)
    # Author, Added July 28, 2023
    # Added Nov 6, 2023 'editor' field
    editor = models.CharField(max_length=255, null=True)
    author_name = models.CharField(max_length=255)
    date = models.DateField()
    # Publication Information, Added July 28, 2023
    info_place = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    info_date = models.DateField()
    info_copyright = models.DateField()
    # Added Nov 6, 2023 'book_price' field
    book_price = models.IntegerField(default=0)
    # Physical Description, Added July 28, 2023
    extent = models.CharField(max_length=1000, blank=True, null=True)
    other_details = models.CharField(max_length=1000, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    # Added October 3, 2023
    date_borrowed = models.DateField(null=True)
    # Added October 17, 2023
    date_reserved = models.DateField(null=True)

    def __str__(self):
        return f'{self.title} - IBSN: {self.isbn}'

    class Meta:
        ordering = ['-date_inputted_added']
        verbose_name_plural = 'Books'


class Position(models.Model):
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.position


class Department(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self):
        return self.title


class Patron(models.Model):
    objects = None
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, related_name='patron_department', on_delete=models.CASCADE)
    last_name = models.CharField(max_length=255)
    position = models.ForeignKey(Position, related_name='patron_position', blank=True, null=True, on_delete=models.CASCADE)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)

    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'


class CheckIn(models.Model):
    objects = None
    patron = models.ForeignKey(User, related_name='patrons', on_delete=models.CASCADE)
    books = models.ManyToManyField(BriefTitle, related_name='patron_books', blank=True)
    date_borrowed = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-date_borrowed']


class CheckOut(models.Model):
    books = models.ForeignKey(BriefTitle, related_name='returned_books', on_delete=models.CASCADE)
    patron = models.ForeignKey(User, related_name='returned_book_borrower', on_delete=models.CASCADE)
    date_returned = models.DateField(auto_now_add=True)


class Reservation(models.Model):
    patron = models.ForeignKey(User, related_name='patrons_reserve', on_delete=models.CASCADE)
    books = models.ManyToManyField(BriefTitle, related_name='patron_books_reserve', blank=True)
    date_reserved = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_reserved']


class BookBorrowed(models.Model):
    books = models.ManyToManyField(BriefTitle, related_name='borrowed_book')
    patron = models.ForeignKey(User, related_name='book_borrower', on_delete=models.CASCADE)
    date_borrowed = models.DateField(auto_now_add=True)


class BookReserved(models.Model):
    books = models.ManyToManyField(BriefTitle, related_name='book_reserved')
    patron = models.ForeignKey(User, related_name='book_reserved_for', on_delete=models.CASCADE)
    date_reserved = models.DateField(auto_now_add=True)


class BookBorrowedHistory(models.Model):
    patron = models.ForeignKey(User, related_name='patron_borrows_history', on_delete=models.CASCADE)
    books = models.ManyToManyField(BriefTitle, related_name='books_borrowed_history')
    date_borrowed = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_borrowed']


# Added on 9/12/2023 NumberLocation, Course, PatronUser
class NumberLocation(models.Model):
    number_loc = models.CharField(max_length=20)

    def __str__(self):
        return self.number_loc


class Course(models.Model):
    course = models.CharField(max_length=255)

    def __str__(self):
        return self.course


class Attendance(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(UserDepartment, related_name='attendance_patron_department',
                                   on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(UserCourse, related_name='attendance_patron_course',
                               on_delete=models.CASCADE, blank=True, null=True)
    position = models.ForeignKey(UserPosition, related_name='attendance_position',
                                 on_delete=models.CASCADE, blank=True, null=True)
    attendance_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:

        ordering = ['-attendance_date']


class AttendanceGraph(models.Model):
    name = models.CharField(max_length=255)
    attendance_date = models.DateField(auto_now_add=True, null=True)

    class Meta:

        ordering = ['-attendance_date']


class RegistrationValidation(models.Model):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.CharField(max_length=255)
    # Ataya gud 9/12/2023
    department = models.ForeignKey(UserDepartment, related_name='register_patron_department', on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(UserCourse, related_name='register_patron_course', on_delete=models.CASCADE, null=True)
    number_loc = models.ForeignKey(UserNumberLocation, related_name='register_patron_number_location', on_delete=models.CASCADE, null=True)
    position = models.ForeignKey(UserPosition, related_name='register_position', on_delete=models.CASCADE, null=True)
    contact_no = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, null=True)
    # Endatayaoi
    patron_id = models.ImageField(null=True, upload_to='images/')
    password = models.CharField(max_length=255)
    date_registered = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Username:{self.username}, Firstname: {self.first_name}, Lastname: {self.last_name}'


class EmailMessage(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()


class DeclinedRegistration(models.Model):
    username = models.CharField(max_length=150)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.CharField(max_length=255)
    # Ataya gud 9/12/2023
    number_loc = models.ForeignKey(UserNumberLocation, related_name='declined_register_patron_number_location',
                                   on_delete=models.CASCADE, null=True)
    contact_no = models.IntegerField(blank=True, null=True)
    # Endatayaoi
    date_declined = models.DateField(auto_now_add=True)


class Registrations(models.Model):
    instance = models.CharField(max_length=255)
    date_registered = models.DateField(auto_now_add=True)


class PromethoenixDescription(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()


class PaidFines(models.Model):
    patron = models.ForeignKey(User, related_name='paid_fines_patron', on_delete=models.CASCADE)
    fine_paid = models.CharField(max_length=100)
    department = models.ForeignKey(UserDepartment, related_name='paid_fines_patron_department',
                                   on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(UserCourse, related_name='paid_fines_patron_course',
                               on_delete=models.CASCADE, blank=True, null=True)
    position = models.ForeignKey(UserPosition, related_name='paid_fines_patron_position',
                                 on_delete=models.CASCADE, blank=True, null=True)
    date_paid = models.DateTimeField(auto_now_add=True)


class FineRate(models.Model):
    title = models.CharField(max_length=255)
    fine_rate = models.IntegerField()
