from django.forms import Select, DateInput, Textarea, TextInput, ModelForm, SelectMultiple, NumberInput
from django import forms
from .models import BriefTitle, Patron, CheckIn, Reservation, Attendance, RegistrationValidation
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _


class RegistrationValidationForm(ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'registration_validation_field',
                                          'placeholder': 'Password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'registration_validation_field',
                                          'placeholder': 'Confirm Password'}),
        strip=False,
    )

    class Meta:
        model = RegistrationValidation
        fields = [
            'username', 'first_name', 'last_name', 'email', 'department', 'course',
            'number_loc', 'position', 'contact_no', 'address', # 'patron_id'
        ]
        widgets = {
            'username': TextInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Username'
            }),
            'first_name': TextInput(attrs={
                'class': "registration_validation_name_field",
                'placeholder': 'First Name'
            }),
            'last_name': TextInput(attrs={
                'class': "registration_validation_name_field",
                'placeholder': 'Last Name'
            }),
            'email': TextInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Email Address'
            }),
            'department': Select(attrs={
                'class': "registration_validation_select_field",
            }),
            'course': Select(attrs={
                'class': "registration_validation_select_field",
            }),
            'position': Select(attrs={
                'class': "registration_validation_select_field",
            }),
            'number_loc': Select(attrs={
                'class': "registration_validation_field_num_loc",
            }),
            'contact_no': forms.NumberInput(attrs={
                'class': "registration_validation_field_con_num",
                'placeholder': 'Your Contact Number'
            }),
            'address': TextInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Address'
            }),
            # 'patron_id': forms.ClearableFileInput(attrs={
            #     'class': "try",
            #     'placeholder': 'Your ID (Optional)'
            # }),
        }


class RegistrationValidationOnlineForm(ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'registration_validation_field',
                                          'placeholder': 'Password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'registration_validation_field',
                                          'placeholder': 'Confirm Password'}),
        strip=False,
    )

    class Meta:
        model = RegistrationValidation
        fields = [
            'username', 'first_name', 'last_name', 'email', 'department', 'course',
            'number_loc', 'position', 'contact_no', 'address', 'patron_id'
        ]
        widgets = {
            'username': TextInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Username'
            }),
            'first_name': TextInput(attrs={
                'class': "registration_validation_name_field",
                'placeholder': 'First Name'
            }),
            'last_name': TextInput(attrs={
                'class': "registration_validation_name_field",
                'placeholder': 'Last Name'
            }),
            'email': TextInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Email Address'
            }),
            'department': Select(attrs={
                'class': "registration_validation_select_field",
            }),
            'course': Select(attrs={
                'class': "registration_validation_select_field",
            }),
            'position': Select(attrs={
                'class': "registration_validation_select_field",
            }),
            'number_loc': Select(attrs={
                'class': "registration_validation_field_num_loc",
            }),
            'contact_no': forms.NumberInput(attrs={
                'class': "registration_validation_field_con_num",
                'placeholder': 'Your Contact Number'
            }),
            'address': TextInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Address'
            }),
            'patron_id': forms.ClearableFileInput(attrs={
                'class': "registration_validation_field",
                'placeholder': 'Your ID (Optional)'
            }),
        }


class AttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={
                'class': "attendance-field",
            }),
        }


class BriefTitleForm(ModelForm):
    class Meta:
        model = BriefTitle
        fields = [
            'material',
            'sub_type',
            'title',
            'subject',
            'subtitle',
            'call_number',
            'edition',
            'lccn',
            'isbn',
            'issn',
            'author_name',
            'date',
            'info_place',
            'publisher',
            'info_date',
            'info_copyright',
            'extent',
            'other_details',
            'size',
            'book_price',
            'editor',
        ]
        labels = {
            # "material": "",
            # "sub_type": "",
            # "title": "",
            "info_place": "Place of Publication",
            "info_date": "Date of Publication",
            "info_copyright": "Copyright Date",
            "extent": "Volume",
            "book_price": 'Book Price',
            "editor": 'Editor',
            # "subtitle": "",
            # "edition": "",
            # "lccn": "",
            # "ibsn": "",
            # "issn": "",
        }
        widgets = {
            'editor': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'book_price': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'material': Select(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'sub_type': Select(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'title': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'subject': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'subtitle': TextInput(attrs={
                'class': "catalogue-brief-title-field",

            }),
            'call_number': TextInput(attrs={
                'class': "catalogue-brief-title-field",

            }),
            'edition': TextInput(attrs={
                'class': "catalogue-brief-title-field",

            }),
            'lccn': TextInput(attrs={
                'class': "catalogue-brief-title-field",

            }),
            'isbn': TextInput(attrs={
                'class': "catalogue-brief-title-field",

            }),
            'issn': TextInput(attrs={
                'class': "catalogue-brief-title-field",

            }),
            # Author, Added July 28, 2023
            'author_name': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'date': DateInput(attrs={
                'class': "catalogue-brief-title-field",
                'type': 'date',
            }),
            # Publication Information, Added July 28, 2023
            'info_place': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'publisher': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'info_date': DateInput(attrs={
                'class': "catalogue-brief-title-field",
                'type': 'date',
            }),
            'info_copyright': DateInput(attrs={
                'class': "catalogue-brief-title-field",
                'type': 'date',
            }),
            # Physical Description, Added July 28, 2023
            'extent': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'other_details': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
            'size': TextInput(attrs={
                'class': "catalogue-brief-title-field",
            }),
        }


class PatronForm(ModelForm):
    class Meta:
        model = Patron
        fields = '__all__'
        widgets = {
            'gender': Select(attrs={
                'class': "profile-field",
            }),
            'first_name': TextInput(attrs={
                'class': "profile-field",
            }),
            'middle_name': TextInput(attrs={
                'class': "profile-field",
            }),
            'last_name': TextInput(attrs={
                'class': "profile-field",
            }),
            'department': Select(attrs={
                'class': "profile-field",
            }),
            'position': TextInput(attrs={
                'class': "profile-field",
            }),
        }


class CheckInForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the books field to include only available books
        self.fields['books'].queryset = BriefTitle.objects.filter(book_status__status='Available')
        # Add a deadline field for each book

    class Meta:
        model = CheckIn
        fields = ['patron', 'books', 'deadline']
        widgets = {
            'patron': forms.Select(attrs={
                'class': "check-in-field",
            }),
            # 'books': FilteredSelectMultiple("Books", is_stacked=False),
            'books': forms.SelectMultiple(attrs={
                'class': "check-in-field-books"
            }),
            'deadline': DateInput(attrs={
                'class': "check-in-field",
                'type': 'date',
            }),
        }


class CheckInFormPatronAdminProfile(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the books field to include only available books
        self.fields['books'].queryset = BriefTitle.objects.filter(book_status__status='Available')
        # Add a deadline field for each book

    class Meta:
        model = CheckIn
        fields = ['patron', 'books', 'deadline']
        widgets = {
            'patron': forms.Select(attrs={
                'class': "patron-profile-admin-check-in-field",
            }),
            # 'books': FilteredSelectMultiple("Books", is_stacked=False),
            'books': forms.SelectMultiple(attrs={
                'class': "patron-profile-admin-check-in-field-books"
            }),
            'deadline': DateInput(attrs={
                'class': "patron-profile-admin-check-in-field",
                'type': 'date',
            }),
        }


class CheckInUserEndForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the books field to include only available books
        self.fields['books'].queryset = BriefTitle.objects.filter(book_status__status='Available')
        # Add a deadline field for each book

    class Meta:
        model = CheckIn
        fields = ['patron', 'books']
        widgets = {
            'patron': forms.Select(attrs={
                'class': "check-in-user-field",
            }),
            # 'books': FilteredSelectMultiple("Books", is_stacked=False),
            'books': forms.SelectMultiple(attrs={
                'class': "check-in-user-field-borrows"
            }),
        }


class ReservationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the books field to include only available books
        self.fields['books'].queryset = BriefTitle.objects.filter(book_status__status='Available')
        # Add a deadline field for each book

    class Meta:
        model = Reservation
        fields = ['patron', 'books']
        widgets = {
            'patron': forms.Select(attrs={
                'class': "reservation-field",
            }),
            # 'books': FilteredSelectMultiple("Books", is_stacked=False),
            'books': forms.SelectMultiple(attrs={
                'class': "reservation-books-field"
            }),
        }


class ReservationUserProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the books field to include only available books
        self.fields['books'].queryset = BriefTitle.objects.filter(book_status__status='Available')
        # Add a deadline field for each book

    class Meta:
        model = Reservation
        fields = ['patron', 'books']
        widgets = {
            'patron': forms.Select(attrs={
                'class': "reservation-user-profile-field",
            }),
            # 'books': FilteredSelectMultiple("Books", is_stacked=False),
            'books': forms.SelectMultiple(attrs={
                'class': "reservation-user-profile-books-field"
            }),
        }


class PatronUserForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'register-field',
               'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'register-field',
               'placeholder': 'Confirm Password'}))

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists!")
        return email

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'course', 'department',
                  'contact_no', 'email', 'address', 'number_loc', 'position']

        widgets = {
            'username': TextInput(attrs={
                'class': "register-field",
                'placeholder': 'Username'
            }),
            'address': TextInput(attrs={
                'class': "register-field",
                'placeholder': 'Address'
            }),
            'first_name': TextInput(attrs={
                'class': "register-field",
                'placeholder': 'First Name'
            }),
            'last_name': TextInput(attrs={
                'class': "register-field",
                'placeholder': 'Last Name'
            }),
            'email': TextInput(attrs={
                'class': "register-field",
                'placeholder': 'Email'
            }),
            'course': forms.Select(attrs={
                'class': "register-field",
            }),
            'department': forms.Select(attrs={
                'class': "register-field",
            }),
            'number_loc': forms.Select(attrs={
                'class': "register-field-number-loc",
            }),
            'position': forms.Select(attrs={
                'class': "register-field",
            }),
            'contact_no': forms.NumberInput(attrs={
                'class': "register-field-contact-no",
                'placeholder': 'Contact No.'
            }),
        }


class ForgotPasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']

        widgets = {
            'email': TextInput(attrs={
                'class': "forgot-password-field",
                'placeholder': 'Your Email'
            }),
        }


class ChangePasswordForm(ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'change-password-field',
               'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'change-password-field',
               'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['password1', 'password2']
