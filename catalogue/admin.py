from django.contrib import admin
from .models import models
from django.contrib.auth.models import User, Group, UserCourse, UserDepartment, UserNumberLocation, UserPosition
from .models import BriefTitle
from .models import MaterialType
from .models import Subtype
from .models import BookStatus
from .models import Patron
from .models import Reservation
from .models import CheckIn
from .models import CheckOut
from .models import BookBorrowed
from .models import Attendance
from .models import RegistrationValidation
from .models import EmailMessage
from .models import DeclinedRegistration
from .models import Registrations
from .models import BookReserved
from .models import PromethoenixDescription
from .models import BookBorrowedHistory
from .models import PaidFines
from .models import FineRate
from django.contrib.admin import AdminSite
from ckeditor.widgets import CKEditorWidget


class FineRateAdmin(admin.ModelAdmin):
    list_display = ('title', 'fine_rate')

    def has_add_permission(self, request):
        # Disable the ability to add new FineRate objects
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete FineRate objects
        return False


class PaidFinesAdmin(admin.ModelAdmin):
    list_display = ('patron', 'date_paid')


class BookBorrowedHistoryAdmin(admin.ModelAdmin):
    list_display = ('patron', 'date_borrowed')


class PromethoenixDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()}
    }

    def has_add_permission(self, request):
        # Disable the ability to add new FineRate objects
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete FineRate objects
        return False


class BookReservedAdmin(admin.ModelAdmin):
    list_display = ('patron', 'date_reserved')


class RegistrationsAdmin(admin.ModelAdmin):
    list_display = ('instance',)


class DeclinedRegistrationAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_declined')


class ReservationValidationAdmin(admin.ModelAdmin):
    list_display = ('username',)


class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        # Disable the ability to add new FineRate objects
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete FineRate objects
        return False


class CustomAdminSite(AdminSite):
    site_title = 'Promethoenix Library Management Admin'
    site_header = 'Promethoenix Library Management'
    index_title = 'Welcome to Promethoenix Library Management Admin'


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'attendance_date')


class BookBorrowedAdmin(admin.ModelAdmin):
    list_display = ('patron', 'date_borrowed')


class CheckOutAdmin(admin.ModelAdmin):
    list_display = ('books', 'patron', 'date_returned')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course',)


class NumberLocationAdmin(admin.ModelAdmin):
    list_display = ('number_loc',)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('position',)


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('patron',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title',)


class PatronAdmin(admin.ModelAdmin):
    list_display = ('first_name',)


class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ('title',)


class SubtypeAdmin(admin.ModelAdmin):
    list_display = ('title',)


class BriefTitleAdmin(admin.ModelAdmin):
    list_display = ('title', 'book_status')


class BookStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)

    def has_add_permission(self, request):
        # Disable the ability to add new FineRate objects
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete FineRate objects
        return False


class CheckInAdmin(admin.ModelAdmin):
    list_display = ('patron', 'date_borrowed')


custom_admin_site = CustomAdminSite()

custom_admin_site.register(FineRate, FineRateAdmin)
custom_admin_site.register(PaidFines, PaidFinesAdmin)
custom_admin_site.register(BookBorrowedHistory, BookBorrowedHistoryAdmin)
custom_admin_site.register(PromethoenixDescription, PromethoenixDescriptionAdmin)
custom_admin_site.register(BookReserved, BookReservedAdmin)
custom_admin_site.register(Registrations, RegistrationsAdmin)
custom_admin_site.register(DeclinedRegistration, DeclinedRegistrationAdmin)
custom_admin_site.register(EmailMessage, EmailMessageAdmin)
custom_admin_site.register(RegistrationValidation, ReservationValidationAdmin)
custom_admin_site.register(Attendance, AttendanceAdmin)
custom_admin_site.register(BookBorrowed, BookBorrowedAdmin)
custom_admin_site.register(CheckOut, CheckOutAdmin)
custom_admin_site.register(Reservation, ReservationAdmin)
custom_admin_site.register(CheckIn, CheckInAdmin)
custom_admin_site.register(Patron, PatronAdmin)
custom_admin_site.register(MaterialType, MaterialTypeAdmin)
custom_admin_site.register(Subtype, SubtypeAdmin)
custom_admin_site.register(BriefTitle, BriefTitleAdmin)
custom_admin_site.register(BookStatus, BookStatusAdmin)
custom_admin_site.register(User)
custom_admin_site.register(Group)
custom_admin_site.register(UserPosition)
custom_admin_site.register(UserCourse)
custom_admin_site.register(UserDepartment)
custom_admin_site.register(UserNumberLocation)

