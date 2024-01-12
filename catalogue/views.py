from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .models import BriefTitle, Patron, CheckIn, BookStatus, Reservation, CheckOut, BookBorrowed, \
    RegistrationValidation, EmailMessage, DeclinedRegistration, Attendance, Registrations, BookReserved, \
    AttendanceGraph, PromethoenixDescription, BookBorrowedHistory, PaidFines, FineRate
from .forms import BriefTitleForm, PatronForm, CheckInForm, ReservationForm, PatronUserForm, CheckInUserEndForm, \
    AttendanceForm, RegistrationValidationForm, CheckInFormPatronAdminProfile, RegistrationValidationOnlineForm, \
    ReservationUserProfileForm, ForgotPasswordForm, ChangePasswordForm
from django.contrib import messages
import pdfkit
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, admin_group_required
from django.contrib.auth.models import Group, User
from django.db.models import Sum, Count
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.core.files.base import ContentFile
import cv2
import qrcode
from django.core.signing import Signer
from cryptography.fernet import Fernet
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


def index(request):
    description_about = PromethoenixDescription.objects.all()
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    today = timezone.now().date()
    daily_fine_rate = FineRate.objects.get(id=1)
    for checkin in overdue_checkins:
        if checkin.deadline is None:
            checkin.fine_amount = 0.00
        else:
            overdue_days = (today - checkin.deadline).days
            fine_rate = daily_fine_rate.fine_rate
            fine_amount = overdue_days * fine_rate
            if fine_amount < 0:
                checkin.fine_amount = 0.00
            else:
                checkin.fine_amount = fine_amount

        checkin.save()

    query = request.GET.get('q')

    if query:
        # Use Q objects to search for books with matching title or author_name
        books = BriefTitle.objects.filter(Q(title__icontains=query) | Q(author_name__icontains=query))
    else:
        # Default behavior: Do not fetch all books when there is no search query
        books = []

    return render(request, 'base.html', {
        'books': books,
        'overdue_checkins': overdue_checkins,
        'description_about': description_about,
    })


@admin_group_required
@login_required(login_url='login')
def cataloging(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    if request.method == 'POST':
        form = BriefTitleForm(request.POST)
        if form.is_valid():
            articles = form.save(commit=False)
            if BriefTitle.objects.filter(title=articles.title).exists() \
                    and BriefTitle.objects.filter(call_number=articles.call_number).exists() \
                    and BriefTitle.objects.filter(edition=articles.edition).exists() \
                    and BriefTitle.objects.filter(author_name=articles.author_name).exists():
                existing_book = BriefTitle.objects.filter(title=articles.title,
                                                          call_number=articles.call_number,
                                                          edition=articles.edition,
                                                          author_name=articles.author_name)
                date_catalogued = existing_book.order_by('-date_inputted_added').first()
                if date_catalogued:
                    catalogued_date = date_catalogued.date_inputted_added
                    formatted_date = catalogued_date.strftime("%B %d, %Y")

                    messages.error(request, f'A book with that title, call number, author, and edition already exists.'
                                            f' It was catalogued on {formatted_date}')
            elif articles.lccn and BriefTitle.objects.filter(lccn=articles.lccn).exists():
                messages.error(request, 'A book with that LCCN already exists')
            elif articles.isbn and BriefTitle.objects.filter(isbn=articles.isbn).exists():
                messages.error(request, 'A book with that ISBN already exists')
            elif articles.issn and BriefTitle.objects.filter(issn=articles.issn).exists():
                messages.error(request, 'A book with that ISSN already exists')
            else:
                form.save()
                messages.success(request, 'Congratulations! The Book has been catalogued!')
    else:
        form = BriefTitleForm()

    return render(request, 'cataloging.html', {
        'form': form,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def details(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    detail = BriefTitle.objects.all()
    return render(request, 'details.html', {
        'detail': detail,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def authors_filter(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    authors_book = BriefTitle.objects.all().order_by('author_name')
    author_books = {}
    for authors in authors_book:
        author = authors.author_name
        if author not in author_books:
            author_books[author] = [authors]
        else:
            author_books[author].append(authors)
    return render(request, 'authors_filter.html', {
        'author_books': author_books,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def filtered_subjects(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    books = BriefTitle.objects.all().order_by('subject', '-date_inputted_added')
    # Preprocess the books data to group books by subject
    grouped_books = {}
    for book in books:
        subject = book.subject
        if subject not in grouped_books:
            grouped_books[subject] = [book]
        else:
            grouped_books[subject].append(book)

    return render(request, 'subjects_filtered.html', {
        'grouped_books': grouped_books,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def alphabetical_books(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())

    # Group books by the initial letter
    books_by_letter = {}
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        books_by_letter[letter] = BriefTitle.objects.filter(
            title__istartswith=letter
        ).order_by('title')

    return render(request, 'alphabetical.html', {
        'books_by_letter': books_by_letter,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def sorted_subjects_pdf(request):
    books = BriefTitle.objects.all()
    grouped_books = {}
    for book in books:
        subject = book.subject
        if subject not in grouped_books:
            grouped_books[subject] = [book]
        else:
            grouped_books[subject].append(book)
    html = render_to_string('subjects_&_books.html', {
        'grouped_books': grouped_books,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="subjects.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def books_alphabetical_pdf(request):
    books = BriefTitle.objects.all().order_by('title')

    html = render_to_string('alphabetical_print.html', {
        'books': books,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="alphabetical_titles.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def authors_pdf(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    authors_book = BriefTitle.objects.all().order_by('author_name')
    author_books = {}
    for authors in authors_book:
        author = authors.author_name
        if author not in author_books:
            author_books[author] = [authors]
        else:
            author_books[author].append(authors)

    html = render_to_string('authors_pdf.html', {
        'author_books': author_books,
        'overdue_checkins': overdue_checkins,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="authors.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def profile_page(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    query = request.GET.get('q')
    patron_link = CheckIn.objects.all()
    if query:
        # Use Q objects to search for Patron objects with matching names
        patrons = User.objects.filter(
            (Q(first_name__icontains=query) |
            Q(username__icontains=query) |
            Q(last_name__icontains=query)) &
            Q(patrons__isnull=False)  # Filter based on the existence of related CheckIn objects
        ).distinct()
    else:
        # Default behavior: Fetch all patrons who are currently borrowing books
        patrons = []

    return render(request, 'profile_page.html', {
        'patrons': patrons,
        'patron_link': patron_link,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def patron_registration(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    if request.method == 'POST':
        form = PatronForm(request.POST)
        if form.is_valid():
            patron = form.save(commit=False)
            if Patron.objects.filter(first_name=patron.first_name,
                                     middle_name=patron.middle_name,
                                     last_name=patron.last_name).exists():
                messages.error(request, 'Patron already exists')
            else:
                form.save()
                messages.success(request, 'Patron Registered!')
    else:
        form = PatronForm()
    return render(request, 'profile_form.html', {
        'form': form,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def check_in(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    today = timezone.now().date()
    filtered_patron = CheckIn.objects.exclude(books=None)
    daily_fine_rate = FineRate.objects.get(id=1)
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            patron = form.cleaned_data['patron']
            checkin, created = CheckIn.objects.get_or_create(patron=patron)

            selected_books = form.cleaned_data['books']

            # Book History Object
            book_history = BookBorrowedHistory.objects.create(patron=patron)
            book_history.books.add(*selected_books)
            book_history.save()

            # Add the selected books to the existing CheckIn instance
            checkin.books.add(*selected_books)
            checkin.deadline = form.cleaned_data['deadline']

            # Updates the date borrowed field
            checkin.date_borrowed = timezone.now()

            # Create BookBorrwed object
            books_borrowed = BookBorrowed.objects.create(patron=patron)
            books_borrowed.books.add(*selected_books)
            books_borrowed.save()

            # Added September 3, 2023
            if checkin.deadline is None:
                checkin.fine_amount = 0.00
            else:
                overdue_days = (today - checkin.deadline).days
                fine_rate = daily_fine_rate.fine_rate
                fine_amount = overdue_days * fine_rate
                if fine_amount < 0:
                    checkin.fine_amount = 0.00
                else:
                    checkin.fine_amount = fine_amount

            checkin.save()

            # Update the book statuses
            for book in selected_books:
                book.book_status_id = 1  # Set status to "Borrowed" (assuming the ID of "Borrowed" is 1)
                book.date_borrowed = today
                book.date_reserved = today
                book.save()

            messages.success(request, 'Patron has borrowed a book')
    else:
        form = CheckInForm()
    return render(request, 'check_in.html', {
        'form': form,
        'overdue_checkins': overdue_checkins,
        'filtered_patron': filtered_patron,
    })


# def patron_profile(request):
#     overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
#     patrons = CheckIn.objects.all()
#     reservations = Reservation.objects.all()
#     reservation_filtered = Reservation.objects.exclude(books=None)
#     yasha = CheckIn.objects.filter(books=None)
#     filtered_patron = CheckIn.objects.exclude(books=None)
#     return render(request, 'patron_profile.html', {
#         'patrons': patrons,
#         'reservations': reservation_filtered,
#         'overdue_checkins': overdue_checkins,
#         'filtered_patron': filtered_patron,
#         'yasha': yasha,
#     })


@admin_group_required
@login_required(login_url='login')
def patron_borrows(request, id):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    books = CheckIn.objects.all()
    patrons = CheckIn.objects.filter(id=id)
    checkin_objects = CheckIn.objects.get(id=id)
    patron = checkin_objects.patron
    today = timezone.now().date()
    daily_fine_rate = FineRate.objects.get(id=1)
    if request.method == 'POST':
        form = CheckInFormPatronAdminProfile(request.POST, instance=checkin_objects)
        if form.is_valid():
            patron = form.cleaned_data['patron']
            checkin, created = CheckIn.objects.get_or_create(patron=patron)

            selected_books = form.cleaned_data['books']

            # Add the selected books to the existing CheckIn instance
            checkin.books.add(*selected_books)

            # Create a BookBorrowed object
            book_borrowed = BookBorrowed.objects.create(patron=patron)
            book_borrowed.books.add(*selected_books)
            book_borrowed.save()

            # Book History Object
            book_history = BookBorrowedHistory.objects.create(patron=patron)
            book_history.books.add(*selected_books)
            book_history.save()

            checkin.deadline = form.cleaned_data['deadline']

            # Updates the date_borrowed field to the current date borrowed

            # Added September 3, 2023
            if checkin.deadline is None:
                checkin.fine_amount = 0.00
            else:
                overdue_days = (today - checkin.deadline).days
                fine_rate = daily_fine_rate.fine_rate
                fine_amount = overdue_days * fine_rate
                if fine_amount < 0:
                    checkin.fine_amount = 0.00
                else:
                    checkin.fine_amount = fine_amount

            if checkin.books.count() == 0:
                checkin.deadline = None
                # Commented on 11/4/2023. A function was created for its functionality
                # checkin.fine_amount = 0.00
            checkin.date_borrowed = timezone.now()
            checkin.save()

            # Update the book statuses
            for book in selected_books:
                book.book_status_id = 1
                book.date_borrowed = today

                book.save()

            return redirect('patron-borrows', id=id)
    else:
        form = CheckInFormPatronAdminProfile(instance=checkin_objects, initial={
            'patron': patron,
        })

    return render(request, 'test_profile.html', {
        'patrons': patrons,
        'checkin_objects': checkin_objects,
        'patron': patron,
        'form': form,
        'books': books,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def reports(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    status = BookStatus.objects.all()
    return render(request, 'reports_page.html', {
        'status': status,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def reserved_books(request):
    active_books_reserved = Reservation.objects.all().annotate(books_reserved=Count('books'))
    active_books_reserved_count_report = active_books_reserved.aggregate(total_sum=Sum('books_reserved'))['total_sum']
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    books = Reservation.objects.all()
    return render(request, 'reserved_books.html', {
        'books': books,
        'overdue_checkins': overdue_checkins,
        'active_books_reserved_count_report': active_books_reserved_count_report,
    })


@admin_group_required
@login_required(login_url='login')
def reserved_books_pdf(request):
    books = Reservation.objects.all()

    html = render_to_string('reserved_books_pdf.html', {
        'books': books,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reserved_books.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def available_books(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    books = BriefTitle.objects.filter(book_status__status='Available')
    return render(request, 'available_books.html', {
        'books': books,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def available_books_pdf(request):
    books = BriefTitle.objects.filter(book_status__status='Available')

    html = render_to_string('available_books_pdf.html', {
        'books': books,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="available_books.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def borrowed_books(request):
    active_borrowed_books = CheckIn.objects.all().annotate(active_books_count=Count('books'))
    active_books_sum_books_borrowed = active_borrowed_books.aggregate(total_sum=Sum('active_books_count'))['total_sum']
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    books = CheckIn.objects.all()
    return render(request, 'borrowed_books.html', {
        'books': books,
        'overdue_checkins': overdue_checkins,
        'active_books_sum_books_borrowed': active_books_sum_books_borrowed,
    })


@admin_group_required
@login_required(login_url='login')
def borrowed_books_pdf(request):
    books = CheckIn.objects.all()

    html = render_to_string('borrowed_books_pdf.html', {
        'books': books,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="borrowed_books.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def book_returns(request, isbn, id):

    try:
        # Get the book instance
        book = BriefTitle.objects.get(isbn=isbn)

        # Retrieve the CheckIn record related to the book
        checkin = CheckIn.objects.get(books=book)

        # Remove the book from the CheckIn's books
        checkin.books.remove(book)

        patron = checkin.patron.id
        check_out_patron = User.objects.get(id=patron)
        # today = timezone.now().date()

        checkout = CheckOut.objects.create(books=book, patron=check_out_patron)
        checkout.save()

        if checkin.books.count() == 0:
            checkin.deadline = None
            # Commented on 11/4/2023. A function has been created for its functionality
            # checkin.fine_amount = 0.00

        checkin.save()

        # Update the book status to "Available"
        book.book_status_id = 2
        book.date_borrowed = None
        book.save()

        return redirect('patron-borrows', id=id)
    except BriefTitle.DoesNotExist:
        pass


@admin_group_required
@login_required(login_url='login')
def patron_due_dates(request):
    today = timezone.now().date()
    # overdue_checkins = CheckIn.objects.filter(deadline__lt=today)
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    daily_fine_rate = FineRate.objects.get(id=1)
    for checkin in overdue_checkins:
        if checkin.deadline is None:
            checkin.fine_amount = 0.00
        else:
            overdue_days = (today - checkin.deadline).days
            fine_rate = daily_fine_rate.fine_rate
            fine_amount = overdue_days * fine_rate
            if fine_amount < 0:
                checkin.fine_amount = 0.00
            else:
                checkin.fine_amount = fine_amount

        checkin.save()

    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    overdue_check = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    overdue_checkin = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    # Filter the overdue_checkins by the patron's position
    position_filter = Q(patron__position__position='Student')
    position_filter_faculty = Q(patron__position__position='Faculty')
    overdue_check = overdue_check.filter(position_filter)
    overdue_checkins_faculty = overdue_checkin.filter(position_filter_faculty)

    return render(request, 'notification_page.html', {
        'overdue_checkins': overdue_checkins,
        'overdue_checkins_faculty': overdue_checkins_faculty,
        'overdue_check': overdue_check,
    })


@admin_group_required
@login_required(login_url='login')
def due_dates_students_pdf(request):
    overdue_check = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    # Filter the overdue_checkins by the patron's position
    position_filter = Q(patron__position__position='Student')
    overdue_check = overdue_check.filter(position_filter)

    html = render_to_string('due_dates_students_pdf.html', {
        'overdue_check': overdue_check,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="due_dates_students.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def due_dates_faculty_pdf(request):
    overdue_checkin = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    # Filter the overdue_checkins by the patron's position
    position_filter_faculty = Q(patron__position__position='Faculty')
    overdue_checkins_faculty = overdue_checkin.filter(position_filter_faculty)

    html = render_to_string('due_dates_faculty_pdf.html', {
        'overdue_checkins_faculty': overdue_checkins_faculty,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="due_dates_faculty.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def patron_due_dates_filter(request, position):
    patron = User.objects.filter(position=position)
    patrons = CheckIn.objects.filter(patron=patron)
    return render(request, 'deadline_positions.html', {
        'patrons': patrons,
    })


@admin_group_required
@login_required(login_url='login')
def check_out(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    borrowed_books = BriefTitle.objects.filter(book_status=1)
    query = request.GET.get('q')

    if query:
        # Use Q objects to search for books with matching title or author_name
        # books = CheckIn.objects.filter(Q(books__title__icontains=query) | Q(patron__first_name__icontains=query) |
        #                                Q(patron__last_name__icontains=query))
        books = borrowed_books.filter(Q(title__icontains=query) | Q(isbn__icontains=query))
    else:
        # Default behavior: Do not fetch all books when there is no search query
        books = []

    return render(request, 'check-out.html', {
        'books': books,
        'overdue_checkins': overdue_checkins,
        'borrowed_books': borrowed_books,
    })


@admin_group_required
@login_required(login_url='login')
def book_returns_check_out(request, isbn):
    try:
        # Get the book instance
        book = BriefTitle.objects.get(isbn=isbn)

        # Retrieve the CheckIn record related to the book
        checkin = CheckIn.objects.get(books=book)

        # Remove the book from the CheckIn's books
        checkin.books.remove(book)

        patron = checkin.patron.id
        check_out_patron = User.objects.get(id=patron)
        # today = timezone.now().date()

        checkout = CheckOut.objects.create(books=book, patron=check_out_patron)
        checkout.save()

        if checkin.books.count() == 0:
            checkin.deadline = None
            # Commented on 11/4/2023. A function was created for its functionality
            # checkin.fine_amount = 0.00

        checkin.save()

        # Update the book status to "Available"
        book.book_status_id = 2
        book.date_reserved = None
        book.date_borrowed = None
        book.save()

        referring_url = request.META.get('HTTP_REFERER')

        if referring_url:
            # Redirect back to the referring page
            return HttpResponseRedirect(referring_url)
        else:
            # If there's no referring URL, redirect to a default page
            return redirect('check-out')
    except BriefTitle.DoesNotExist:
        pass


@admin_group_required
@login_required(login_url='login')
def reservation(request):
    patron_reservation = Reservation.objects.exclude(books=None)
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            patron = form.cleaned_data['patron']
            reserve, created = Reservation.objects.get_or_create(patron=patron)

            selected_books = form.cleaned_data['books']

            # Add the selected books to the existing CheckIn instance
            reserve.books.add(*selected_books)

            # Create a BookReserve Object
            book_reserve = BookReserved.objects.create(patron=patron)
            book_reserve.books.add(*selected_books)
            book_reserve.save()

            reserve.save()

            # Update the book statuses
            for book in selected_books:
                book.book_status_id = 3  # Set status to "Reserved" (The ID of "Reserved" is 3)
                book.date_reserved = timezone.now()
                book.save()

            messages.success(request, 'Book has been reserved for Patron!')
    else:
        form = ReservationForm()
    return render(request, 'reservation.html', {
        'form': form,
        'overdue_checkins': overdue_checkins,
        'patron_reservation': patron_reservation,
    })


@admin_group_required
@login_required(login_url='login')
def patron_reservation_profile(request, id):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    patron_reservation = Reservation.objects.filter(id=id)

    return render(request, 'reservation_profile_details.html', {
        'patron_reservation': patron_reservation,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def book_borrow_reserve(request, isbn, id, patron):
    try:
        today = timezone.now().date()
        # Get the book instance
        book = BriefTitle.objects.get(isbn=isbn)

        reservation_book = Reservation.objects.get(books=book)
        reservation_book.books.remove(book)
        reservation_book.save()

        patrons = User.objects.get(id=patron)
        # Retrieve the CheckIn record related to the book
        checkin, created = CheckIn.objects.get_or_create(patron=patrons)

        # Remove the book from the CheckIn's books
        checkin.books.add(book)

        if checkin.books.count() == 0:
            checkin.deadline = None

        # Updates the date_borrowed field to the currect date of borrow
        checkin.date_borrowed = timezone.now()
        checkin.save()

        # Create a Borrow Instance
        borrow_instance = BookBorrowed.objects.create(patron=patrons)
        borrow_instance.books.add(book)
        borrow_instance.save()

        # Book History Object
        book_history = BookBorrowedHistory.objects.create(patron=patrons)
        book_history.books.add(book)
        book_history.save()

        # Update the book status to "Borrowed"
        book.book_status_id = 1
        book.date_borrowed = today
        book.date_reserved = None
        book.save()

        return redirect('reservation-profile', id=id)
    except BriefTitle.DoesNotExist:
        pass


@admin_group_required
@login_required(login_url='login')
def fines_paid_cash(request, username):

    user = User.objects.get(username=username)

    check_in_instance = CheckIn.objects.get(patron=user)

    # Now Let's create a PaidFines object from the retrieved check in instance
    paid_fines = PaidFines.objects.create(patron=check_in_instance.patron,
                                          fine_paid=check_in_instance.fine_amount,
                                          department=user.department,
                                          course=user.course,
                                          position=user.position,
                                          )

    check_in_instance.fine_amount = 0
    check_in_instance.save()
    paid_fines.save()
    return redirect('patron-borrows', id=check_in_instance.id)


@admin_group_required
@login_required(login_url='login')
def paid_fines(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    fine_paid = PaidFines.objects.all()
    return render(request, 'paid_fines.html', {
        'fine_paid': fine_paid,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def paid_fines_pdf(request):
    fine_paid = PaidFines.objects.all()

    html = render_to_string('paid_fines_pdf.html', {
        'fine_paid': fine_paid,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="paid_fines.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def unpaid_fines(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    unpaid_fine = CheckIn.objects.exclude(fine_amount=0)
    return render(request, 'unpaid_fines.html', {
        'unpaid_fine': unpaid_fine,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def unpaid_fines_pdf(request):
    unpaid_fine = CheckIn.objects.exclude(fine_amount=0)

    html = render_to_string('unpaid_fines_pdf.html', {
        'unpaid_fine': unpaid_fine,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="unpaid_fines.pdf"'
    return response


@unauthenticated_user
def authentication(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, "Invalid form data. Please try again")

    return render(request, 'login.html', {'overdue_checkins': overdue_checkins})


def user_logout(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def registration(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    else:
        form = PatronUserForm
        if request.method == 'POST':
            form = PatronUserForm(request.POST)
            if form.is_valid():
                userForm = form.save()
                user = form.cleaned_data.get('username')
                group = Group.objects.get(name='patrons')
                userForm.groups.add(group)
                userForm.save()
                messages.success(request, 'Account successfully created ' + user)
                return redirect('login')

    return render(request, 'register.html', {
        'form': form,
    })


@login_required(login_url='login')
def user_patron_profile(request, username):
    # User object
    user = User.objects.get(username=username)

    # Check if the user has already liked the post
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())

    # Present Date
    today = timezone.now().date()
    # Patron in CheckIn Objecct
    # patron = CheckIn.objects.get(patron=user.id)
    # patron_deadline = patron.patron.username

    # Retrieving CheckIn & Reservation foreign objects through filter function
    patrons = CheckIn.objects.filter(patron=user.id)
    reservations = Reservation.objects.filter(patron=user.id)
    # Deadline of Patron's Borrowed Book(s) in CheckIn object

    # Number of Active Borrowed Books from CheckIn Model
    active_borrowed_books = CheckIn.objects.filter(patron=user.id).annotate(active_books_count=Count('books'))
    active_books_sum_user_profile = active_borrowed_books.aggregate(total_sum=Sum('active_books_count'))['total_sum']

    # Number of Active Reserved Books from Reservation Model
    active_books_reserved = Reservation.objects.filter(patron=user.id).annotate(books_reserved=Count('books'))
    active_books_reserved_count_user_profile = active_books_reserved.aggregate(total_sum=Sum('books_reserved'))['total_sum']

    # Borrow Form & Reservation Form
    # borrow_form = CheckInForm(initial={'patron': user.id, 'deadline': patron_deadline})
    borrow_form = CheckInUserEndForm(initial={'patron': user.id})
    reservation_form = ReservationUserProfileForm(initial={'patron': user.id})

    # Create QR Code for each user
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Keys
    key = b'bSKEk2cT2V8vllCpMtQWsO2FxUVQdl3S_IHwBbEE4eQ='
    cipher_suite = Fernet(key)
    signing_key = b'Cold'
    signer = Signer(key=signing_key)

    encrypted_username = signer.sign(user.username) # 1st Encrypt the username
    data = encrypted_username.encode('utf-8') # 2 Convert encrypted_username to bytes
    encrypted_data = cipher_suite.encrypt(data) # Final

    plain_text = cipher_suite.decrypt(encrypted_data)  # 1
    my_string = plain_text.decode('utf-8')  # 2
    decrypted_username = signer.unsign(my_string) # 3

    qr.add_data(encrypted_data)
    qr.make(fit=True)

    # Create a Pillow image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    img.save(f'catalogue/static/images/QR-Code-{user.username}.png')

    if request.method == 'POST':
        if 'patron-borrow-form' in request.POST:
            borrow_form = CheckInUserEndForm(request.POST)
            if borrow_form.is_valid():
                patron = borrow_form.cleaned_data['patron']
                if patron != user:
                    return HttpResponseBadRequest("You can only borrow books for your own patron account.")
                checkin, created = CheckIn.objects.get_or_create(patron=patron)

                selected_books = borrow_form.cleaned_data['books']

                # Create a Borrow instance
                borrowed_books_patron = BookBorrowed.objects.create(patron=patron)
                borrowed_books_patron.books.add(*selected_books)
                borrowed_books_patron.save()

                # Book History Object
                book_history = BookBorrowedHistory.objects.create(patron=patron)
                book_history.books.add(*selected_books)
                book_history.save()

                # Add the selected books to the existing CheckIn instance
                checkin.books.add(*selected_books)

                # updates the date_borrowed field according to the current date of borrow
                checkin.date_borrowed = timezone.now()

                checkin.save()

                # Update the book statuses
                for book in selected_books:
                    book.book_status_id = 1  # Set status to "Borrowed" (assuming the ID of "Borrowed" is 1)
                    book.date_borrowed = today
                    book.save()

                messages.success(request, 'Patron has borrowed a book')
        elif 'patron-reservation-form' in request.POST:
            reservation_form = ReservationUserProfileForm(request.POST)
            if reservation_form.is_valid():
                patron = reservation_form.cleaned_data['patron']
                if patron != user:
                    return HttpResponseBadRequest("You can only reserve books for your own patron account.")
                reserve, created = Reservation.objects.get_or_create(patron=patron)

                selected_books = reservation_form.cleaned_data['books']

                # Add the selected books to the existing CheckIn instance
                reserve.books.add(*selected_books)
                reserve.date_reserved = today
                reserve.save()

                # Create a Reserve Instance
                reserved_books_patron = BookReserved.objects.create(patron=patron)
                reserved_books_patron.books.add(*selected_books)
                reserved_books_patron.save()

                # Update the book statuses
                for book in selected_books:
                    book.book_status_id = 3  # Set status to "Reserved" (The ID of "Reserved" is 3)
                    book.date_reserved = today
                    book.save()
                messages.success(request, 'Book has been reserved for Patron!')

    return render(request, 'user_patron_profile.html', {
        'user': user,
        'borrow_form': borrow_form,
        'reservation_form': reservation_form,
        'overdue_checkins': overdue_checkins,
        'patrons': patrons,
        'reservations': reservations,
        'img': img,
        'encrypted_data': encrypted_data,
        'plain_text': decrypted_username,
        'active_books_sum_user_profile': active_books_sum_user_profile,
        'active_books_reserved_count_user_profile': active_books_reserved_count_user_profile,
    })


@login_required(login_url='login')
def user_profile_check_in(request, username):
    user = User.objects.get(username=username)
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    today = timezone.now().date()

    borrow_form = CheckInUserEndForm(initial={'patron': user.id})
    if request.method == 'POST':
        borrow_form = CheckInUserEndForm(request.POST)
        if borrow_form.is_valid():
            patron = borrow_form.cleaned_data['patron']
            if patron != user:
                return HttpResponseBadRequest("You can only borrow books for your own patron account.")
            checkin, created = CheckIn.objects.get_or_create(patron=patron)

            selected_books = borrow_form.cleaned_data['books']

            # Create a Borrow instance
            borrowed_books_patron = BookBorrowed.objects.create(patron=patron)
            borrowed_books_patron.books.add(*selected_books)
            borrowed_books_patron.save()

            # Book History Object
            book_history = BookBorrowedHistory.objects.create(patron=patron)
            book_history.books.add(*selected_books)
            book_history.save()

            # Add the selected books to the existing CheckIn instance
            checkin.books.add(*selected_books)

            # updates the date_borrowed field according to the current date of borrow
            checkin.date_borrowed = timezone.now()

            checkin.save()

            # Update the book statuses
            for book in selected_books:
                book.book_status_id = 1  # Set status to "Borrowed" (assuming the ID of "Borrowed" is 1)
                book.date_borrowed = today
                book.save()

            messages.success(request, 'Patron has borrowed a book')
    return render(request, 'user_profile_check_in.html', {
        'overdue_checkins': overdue_checkins,
        'borrow_form': borrow_form,
    })


@login_required(login_url='login')
def user_profile_reserve_book(request, username):
    user = User.objects.get(username=username)
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    reservation_form = ReservationUserProfileForm(initial={'patron': user.id})
    today = timezone.now().date()
    if request.method == 'POST':
        reservation_form = ReservationUserProfileForm(request.POST)
        if reservation_form.is_valid():
            patron = reservation_form.cleaned_data['patron']
            if patron != user:
                return HttpResponseBadRequest("You can only reserve books for your own patron account.")
            reserve, created = Reservation.objects.get_or_create(patron=patron)

            selected_books = reservation_form.cleaned_data['books']

            # Add the selected books to the existing CheckIn instance
            reserve.books.add(*selected_books)
            reserve.date_reserved = today
            reserve.save()

            # Create a Reserve Instance
            reserved_books_patron = BookReserved.objects.create(patron=patron)
            reserved_books_patron.books.add(*selected_books)
            reserved_books_patron.save()

            # Update the book statuses
            for book in selected_books:
                book.book_status_id = 3  # Set status to "Reserved" (The ID of "Reserved" is 3)
                book.date_reserved = today
                book.save()
            messages.success(request, 'Book has been reserved for Patron!')
    return render(request, 'user_profile_book_reserve.html', {
        'reservation_form': reservation_form,
        'overdue_checkins': overdue_checkins,
    })


@login_required(login_url='login')
def user_profile_book_borrowed_history(request, username):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    user = User.objects.get(username=username)
    book_history = BookBorrowedHistory.objects.filter(patron=user)
    return render(request, 'user_profile_book_borrowed_history.html', {
        'book_history': book_history,
        'overdue_checkins': overdue_checkins,
    })


@login_required(login_url='login')
def user_profile_identification_data(request, username):
    user = User.objects.get(username=username)
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    return render(request, 'user_profile_user_id.html', {
        'user': user,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def no_deadline_check_in(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    no_deadline = CheckIn.objects.filter(Q(deadline=None) & Q(books__isnull=False)).distinct()

    return render(request, 'no_deadline_checkins.html', {
        'no_deadline': no_deadline,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def no_deadline_check_in_pdf(request):
    no_deadline = CheckIn.objects.filter(Q(deadline=None) & Q(books__isnull=False)).distinct()

    html = render_to_string('no_deadline_checkins_pdf.html', {
        'no_deadline': no_deadline,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="no_deadline_checkins.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def dashboard(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    current_date = timezone.now().date()
    start_of_day = datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0,)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)
    # Summing the borrowed books from BookBorrowed Model
    borrowed_books_total = BookBorrowed.objects.all().annotate(book_count=Count('books'))
    total_books_count = borrowed_books_total.aggregate(total_count=Sum('book_count'))['total_count']

    # Total Number of Books
    total_books_sum = BriefTitle.objects.all()

    # Number of Active Borrowed Books from CheckIn Model
    active_borrowed_books = CheckIn.objects.all().annotate(active_books_count=Count('books'))
    active_books_sum = active_borrowed_books.aggregate(total_sum=Sum('active_books_count'))['total_sum']

    # Number of Active Reserved Books from Reservation Model
    active_books_reserved = Reservation.objects.all().annotate(books_reserved=Count('books'))
    active_books_reserved_count = active_books_reserved.aggregate(total_sum=Sum('books_reserved'))['total_sum']

    # Percentage of Borrowed Books
    percentage_borrowed_books = (active_books_sum / total_books_sum.count()) * 100

    # Total Number of Patrons
    total_patrons = User.objects.all()
    no_admin_total_patrons = (total_patrons.count() - 1)

    # Patron Category Segregation (Student)
    student_patrons = User.objects.filter(position__position='Student').annotate(students_patron=Count('username'))
    student_patrons_count = student_patrons.aggregate(student_patrons=Sum('students_patron'))['student_patrons']

    # Patron Category Segregation (Faculty)
    faculty_patron = User.objects.filter(position__position='Faculty').annotate(faculty_pat=Count('username'))
    faculty_patron_count = (faculty_patron.aggregate(faculty_patrons=Sum('faculty_pat'))['faculty_patrons']) - 1

    # Patron Percentage (Faculty)
    faculty_percentage = (faculty_patron_count / no_admin_total_patrons) * 100

    # Patron Percentage (Student)
    student_percentage = (student_patrons_count / no_admin_total_patrons) * 100

    # Number of Borrowing Patrons
    filtered_patron = CheckIn.objects.exclude(books=None).annotate(patron_count=Count('patron'))
    active_patron_sum = filtered_patron.aggregate(patron_sum=Sum('patron_count'))['patron_sum']

    # Percentage of Borrowers
    no_admin = (active_patron_sum / (total_patrons.count() - 1)) * 100

    # Total Number of Checkouts
    total_checkouts = CheckOut.objects.all()

    # Number of Daily Checkout
    daily_checkouts = CheckOut.objects.filter(date_returned=current_date)

    # Number of Active Reservation(s)
    number_of_active_reservations = Reservation.objects.exclude(books=None)

    # Number of Daily Borrowed Books
    daily_borrowed_books = BookBorrowed.objects.filter(date_borrowed=current_date).annotate(daily_books=Count('books'))
    daily_books_number = daily_borrowed_books.aggregate(daily_books_count=Sum('daily_books'))['daily_books_count']
    
    # Daily Reservation
    books_reserved_count = BookReserved.objects.filter(date_reserved=current_date).annotate(books_reserve=Count('books'))
    daily_books_reserved = books_reserved_count.aggregate(daily_books=Sum('books_reserve'))['daily_books']

    # Patron Attendance
    total_attendance = Attendance.objects.all()
    attendance_daily = Attendance.objects.filter(attendance_date__range=(start_of_day, end_of_day)).annotate(
        attendance=Count('name'))
    daily_attendance = attendance_daily.aggregate(daily_attendance=Sum('attendance'))['daily_attendance']

    # Registration
    declined_registries = DeclinedRegistration.objects.all().count()
    total_registration = no_admin_total_patrons + declined_registries

    # Daily Registration
    daily_registration = Registrations.objects.filter(date_registered=current_date).annotate(
        register_daily=Count('instance'))
    daily_registrations = daily_registration.aggregate(daily_register=Sum('register_daily'))['daily_register']
    # Patron for Verification
    registry_for_verification = RegistrationValidation.objects.all().count()

    # No Deadline Patrons or CheckIn
    no_deadline = CheckIn.objects.filter(Q(deadline=None) & Q(books__isnull=False)).distinct()

    # Date for graph
    ten_days_ago = timezone.now() - timedelta(days=10)

    # Graph Section

    # Books Borrowed BarGraph
    data = BookBorrowed.objects.filter(date_borrowed__gte=ten_days_ago) \
        .values('date_borrowed') \
        .annotate(book_count=Count('books'))

    dates = [entry['date_borrowed'].strftime('%Y-%m-%d') for entry in data]
    book_counts = [entry['book_count'] for entry in data]

    # Books CheckOuts BarGraph
    data_checkout = CheckOut.objects.filter(date_returned__gte=ten_days_ago) \
        .values('date_returned') \
        .annotate(book_count=Count('books'))

    dates_checkout = [entry['date_returned'].strftime('%Y-%m-%d') for entry in data_checkout]
    book_counts_checkout = [entry['book_count'] for entry in data_checkout]

    # Book Reserved BarGraph
    data_reserved = BookReserved.objects.filter(date_reserved__gte=ten_days_ago) \
        .values('date_reserved') \
        .annotate(book_count=Count('books'))

    dates_reserved = [entry['date_reserved'].strftime('%Y-%m-%d') for entry in data_reserved]
    book_counts_reserved = [entry['book_count'] for entry in data_reserved]

    # Attendance BarGraph
    data_attendance = AttendanceGraph.objects.filter(attendance_date__gte=ten_days_ago) \
        .values('attendance_date') \
        .annotate(attendance_count=Count('name'))

    dates_attendance = [entry['attendance_date'].strftime('%Y-%m-%d') for entry in data_attendance]
    counts_attendance = [entry['attendance_count'] for entry in data_attendance]

    return render(request, 'dashboard.html', {
        'overdue_checkins': overdue_checkins,
        'total_books_count': total_books_count,
        'active_books_sum': active_books_sum,
        'active_books_reserved_count': active_books_reserved_count,
        'active_patron_sum': active_patron_sum,
        'total_books_sum': total_books_sum,
        'total_patrons': no_admin_total_patrons,
        'total_checkouts': total_checkouts,
        'no_admin': no_admin,
        'percentage_borrowed_books': percentage_borrowed_books,
        'daily_checkouts': daily_checkouts,
        'number_of_active_reservations': number_of_active_reservations,
        'daily_books_number': daily_books_number,
        'daily_books_reserved': daily_books_reserved,
        'total_attendance': total_attendance,
        'daily_attendance': daily_attendance,
        'declined_registries': total_registration,
        'daily_registrations': daily_registrations,
        'registry_for_verification': registry_for_verification,
        'student_patrons_count': student_patrons_count,
        'faculty_patron_count': faculty_patron_count,
        'faculty_percentage': faculty_percentage,
        'student_percentage': student_percentage,
        'no_deadline': no_deadline,
        # Date Borrowed graph
        'dates': dates,
        'book_counts': book_counts,
        # Checkout graph
        'dates_checkout': dates_checkout,
        'book_counts_checkout': book_counts_checkout,
        # Book Reserved Graph
        'dates_reserved': dates_reserved,
        'book_counts_reserved': book_counts_reserved,
        # Attendance Graph
        'dates_attendance': dates_attendance,
        'counts_attendance': counts_attendance,
    })


@admin_group_required
@login_required(login_url='login')
def attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance_form = form.save(commit=False)
            if not User.objects.filter(username=attendance_form.name).exists():
                messages.error(request, "User does not exist. Enter a Valid Username")
            else:
                user_instance = User.objects.get(username=attendance_form.name)
                attendance_instance = Attendance.objects.create(name=attendance_form.name)

                attendance_instance.department = user_instance.department
                attendance_instance.course = user_instance.course
                attendance_instance.position = user_instance.position
                attendance_instance.save()

                attendance_graph_data = AttendanceGraph.objects.create(name=attendance_form.name)
                attendance_graph_data.save()

                messages.success(request, "Attendance Recorded!")
    else:
        form = AttendanceForm()

    return render(request, 'attendance.html', {
        'form': form,
    })


@admin_group_required
@login_required(login_url='login')
def attendance_list(request):
    default_date = date.today()
    attendances_default = Attendance.objects.all()

    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = None

    if selected_date:  # Check if a date is selected
        attendances = Attendance.objects.filter(attendance_date__date=selected_date)
    else:
        attendances = []

    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())

    return render(request, 'attendance_list.html', {
        'attendances': attendances,
        'overdue_checkins': overdue_checkins,
        'selected_date': selected_date,
        'attendances_default': attendances_default,
        'default_date': default_date,
    })


@admin_group_required
@login_required(login_url='login')
def attendance_list_pdf(request):
    attendances_default = Attendance.objects.all()

    html = render_to_string('attendance_list_pdf.html', {
        'attendances_default': attendances_default,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_list.pdf"'
    return response


@admin_group_required
@login_required(login_url='login')
def attendance_list_filtered_daily_pdf(request):
    default_date = date.today()
    attendances_default = Attendance.objects.all()

    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%b. %d, %Y').date()
    else:
        selected_date = None

    if selected_date:  # Check if a date is selected
        attendances = Attendance.objects.filter(attendance_date__date=selected_date)
    else:
        attendances = []

    html = render_to_string('attendance_list_filtered_daily_pdf.html', {
        # 'selected_date_str': selected_date_str,
        'attendances': attendances,
        'attendances_default': attendances_default,
        'default_date': default_date,
        'selected_date': selected_date,
    })

    options = {
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'quiet': '',
        'print-media-type': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
    }

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_list_daily.pdf"'
    return response


@unauthenticated_user
def registration_validation_online(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    if request.method == 'POST':
        form = RegistrationValidationOnlineForm(request.POST, request.FILES)
        if form.is_valid():

            user = form.save(commit=False)
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if User.objects.filter(email=user.email).exists() or\
                    RegistrationValidation.objects.filter(email=user.email).exists():
                messages.error(request, 'Email Already Exists')
            if password1 == password2 and not User.objects.filter(email=user.email).exists() and not \
                    RegistrationValidation.objects.filter(email=user.email).exists():
                hashed_password = make_password(password1)
                user.password = hashed_password

                # cap = cv2.VideoCapture(0)  # Use the default camera (usually the built-in webcam)
                # ret, frame = cap.read()
                # cap.release()  # Release the camera
                # if ret:
                #     # Convert the captured frame to JPEG format
                #     _, buffer = cv2.imencode('.jpg', frame)

                user.save()

                # Create Register Instance
                registration_instance = Registrations.objects.create(instance=user.username)
                registration_instance.save()

                return HttpResponseBadRequest("You can only reserve books for your own patron account.")

            elif password1 != password2:
                messages.error(request, 'Password not the same')

            if User.objects.filter(username=user.username).exists() or \
                    RegistrationValidation.objects.filter(username=user.username).exists():
                messages.error(request, 'Username Already Exists')

    else:
        form = RegistrationValidationOnlineForm()
    return render(request, 'registration_validation_online.html', {
        'form': form,
        'overdue_checkins': overdue_checkins,
    })


@unauthenticated_user
def registration_validation(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    if request.method == 'POST':
        form = RegistrationValidationForm(request.POST, request.FILES)
        if form.is_valid():

            user = form.save(commit=False)
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if User.objects.filter(email=user.email).exists() or\
                    RegistrationValidation.objects.filter(email=user.email).exists():
                messages.error(request, 'Email Already Exists')
            if password1 == password2 and not User.objects.filter(email=user.email).exists() and not \
                    RegistrationValidation.objects.filter(email=user.email).exists():
                hashed_password = make_password(password1)
                user.password = hashed_password

                cap = cv2.VideoCapture(0)  # Use the default camera (usually the built-in webcam)
                ret, frame = cap.read()
                cap.release()  # Release the camera
                if ret:
                    # Convert the captured frame to JPEG format
                    _, buffer = cv2.imencode('.jpg', frame)
                    user.patron_id.save(f'{user.username}.jpg', ContentFile(buffer.tobytes()), save=True)

                user.save()

                # Create Register Instance
                registration_instance = Registrations.objects.create(instance=user.username)
                registration_instance.save()

                return HttpResponseBadRequest("You can only reserve books for your own patron account.")

            elif password1 != password2:
                messages.error(request, 'Password not the same')

            if User.objects.filter(username=user.username).exists() or \
                    RegistrationValidation.objects.filter(username=user.username).exists():
                messages.error(request, 'Username Already Exists')

    else:
        form = RegistrationValidationForm()
    return render(request, 'registration_validation.html', {
        'form': form,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def confirming_registrations(request):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    registrations = RegistrationValidation.objects.all()
    return render(request, 'confirming_registrations.html', {
        'registrations': registrations,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
def confirm_user_registration(request, username):
    try:
        confirming_message = EmailMessage.objects.get(title='Registration Verified')
        confirming_registration = RegistrationValidation.objects.get(username=username)

        user = User.objects.create(
            username=confirming_registration.username,
            first_name=confirming_registration.first_name,
            last_name=confirming_registration.last_name,
            email=confirming_registration.email,
            department=confirming_registration.department,
            course=confirming_registration.course,
            number_loc=confirming_registration.number_loc,
            position=confirming_registration.position,
            contact_no=confirming_registration.contact_no,
            address=confirming_registration.address,
            password=confirming_registration.password,
        )

        group = Group.objects.get(name='patrons')
        user.groups.add(group)
        user.save()

        # Sending Email or Message
        name = confirming_registration.first_name
        from_email = 'Autodidacticism'
        subject = confirming_message.title
        message = confirming_message.content
        to_email = [confirming_registration.email]
        html_message = render_to_string('confirmed_registration_message.html', {
            'name': name,
            'subject': subject,
            'message': message,
        })
        send_mail(
            subject=subject,
            from_email=from_email,
            recipient_list=to_email,
            message=message,
            html_message=html_message,
            fail_silently=False
        )
        # End of Sending Email

        confirming_registration.delete()

        referring_url = request.META.get('HTTP_REFERER')

        if referring_url:
            # Redirect back to the referring page
            return HttpResponseRedirect(referring_url)
        else:
            # If there's no referring URL, redirect to a default page
            return redirect('confirm')
    except RegistrationValidation.DoesNotExist:
        # Handle the case where the RegistrationValidation object doesn't exist for the given username
        # You might want to display an error message or take appropriate action here.
        pass


@admin_group_required
@login_required(login_url='login')
def declined_registration(request, username):
    try:
        email_message = EmailMessage.objects.get(title="Registration Declined")
        registering_patron = RegistrationValidation.objects.get(username=username)
        registering_patron.delete()

        decline_registration = DeclinedRegistration.objects.create(
            username=registering_patron.username,
            first_name=registering_patron.first_name,
            last_name=registering_patron.last_name,
            email=registering_patron.email,
            contact_no=registering_patron.contact_no,
            number_loc=registering_patron.number_loc,
        )
        decline_registration.save()

        referring_url = request.META.get('HTTP_REFERER')

        # Send email
        from_email = 'LMS'
        name = registering_patron.first_name
        to_email = [registering_patron.email]
        message = email_message.content
        subject = email_message.title
        html_message = render_to_string('declined_registration.html', {
            'name': name,
            'message': message,
        })

        send_mail(
            subject=subject,
            from_email=from_email,
            recipient_list=to_email,
            message=message,
            html_message=html_message,
            fail_silently=False,
        )
        # End send email

        if referring_url:
            # Redirect back to the referring page
            return HttpResponseRedirect(referring_url)
        else:
            # If there's no referring URL, redirect to a default page
            return redirect('confirm')

    except RegistrationValidation.DoesNotExist:
        pass


@admin_group_required
@login_required(login_url='login')
def registering_patron_profile(request, username):
    overdue_checkins = CheckIn.objects.filter(deadline__lt=timezone.now().date())
    registering_patrons = RegistrationValidation.objects.filter(username=username)
    return render(request, 'registering_patrons_profile_confirmation.html', {
        'registering_patrons': registering_patrons,
        'overdue_checkins': overdue_checkins,
    })


@admin_group_required
@login_required(login_url='login')
@csrf_exempt
def qr_code_scanner(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        scanned_data = data.get('scanned_data')
        # Process or store the scanned data as needed

        # encrypted_username = signer.sign(user.username)  # 1st Encrypt the username
        # data = encrypted_username.encode('utf-8')  # 2 Convert encrypted_username to bytes
        # encrypted_data = cipher_suite.encrypt(data)  # Final

        key = b'bSKEk2cT2V8vllCpMtQWsO2FxUVQdl3S_IHwBbEE4eQ='
        cipher_suite = Fernet(key)
        signing_key = b'Cold'
        signer = Signer(key=signing_key)

        # encrypted_username = signer.sign(user.username)  # 1st Encrypt the username
        # data = encrypted_username.encode('utf-8')  # 2 Convert encrypted_username to bytes
        # encrypted_data = cipher_suite.encrypt(data)  # Final

        plain_text = cipher_suite.decrypt(scanned_data)  # 1
        my_string = plain_text.decode('utf-8')  # 2
        decrypted_username = signer.unsign(my_string)  # 3

        if User.objects.filter(username=decrypted_username).exists():
            user_instance = User.objects.get(username=decrypted_username)

            # Create Attendance Instance
            attendance_object = Attendance.objects.create(
                name=user_instance.username,
                department=user_instance.department,
                course=user_instance.course,
                position=user_instance.position
            )
            attendance_object.save()

            attendance_data = AttendanceGraph.objects.create(name=decrypted_username)
            attendance_data.save()

            # For example, return a JSON response
            # messages.success(request, f'Welcome, {decrypted_username}')
            # return redirect('qr-code-attendance') and JsonResponse({decrypted_username: True})
            return JsonResponse({'status': 'success', 'message': f'Welcome, {decrypted_username}'})
        elif not User.objects.filter(username=decrypted_username).exists():
            # messages.error(request, 'Scanned Data Does not Exists')
            # return redirect('qr-code-attendance') and JsonResponse({decrypted_username: True})
            return JsonResponse({'status': 'error', 'message': 'Scanned Data Does not Exist'})
        # return JsonResponse({decrypted_username: True})

    return render(request, 'qr_code_attendance.html')


class MyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        try:
            email_confirmed = user.profile.email_confirmed
        except AttributeError:
            email_confirmed = ''

        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(email_confirmed)
        )


token_generator = MyTokenGenerator()


@unauthenticated_user
def forgot_password(request):
    forgot_password_form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)

                # Generate a unique token for the user
                token = token_generator.make_token(user)

                # Send email
                from_email = 'LMS'
                name = user.first_name
                to_email = [user.email]
                message = 'Your Token Is'
                subject = 'Change Password'
                html_message = render_to_string('forgot_password_message_to_email.html', {
                    'name': name,
                    'message': message,
                    'token': token,
                    'username': user.username,
                    'email': user.email,
                })

                send_mail(
                    subject,
                    message,
                    'LMS <dandan321321321@gmail.com>',
                    to_email,

                    html_message=html_message,
                    fail_silently=False,
                )
                # End send email
                messages.success(request, 'Email sent!')
            else:
                messages.error(request, 'Email not found')

    return render(request, 'forgot_password.html', {
        'form': forgot_password_form,
    })


@unauthenticated_user
def enter_token(request, email):
    if request.method == 'POST':
        token = request.POST.get('token')
        # email = request.POST.get('email')

        # Check if the token is valid
        if token_generator.check_token(User.objects.get(email=email), token):
            return redirect('change-password', email=email, token=token)
        else:
            messages.error(request, 'Invalid token. Please try again.')

    return render(request, 'enter_token.html')


@unauthenticated_user
def change_password(request, email, token):
    user = User.objects.get(email=email)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password1'] == form.cleaned_data['password2']:
                hashed_password = make_password(form.cleaned_data['password1'])
                user.password = hashed_password
                user.save()
                messages.success(request, "You've successfully reset your password")
                return redirect('login')
            else:
                messages.error(request, "Password does not match")

    form = ChangePasswordForm()

    return render(request, 'change_password.html', {
        'form': form,
    })


@login_required(login_url='login')
def user_patron_home_search_borrow_book(request, username, id):
    today = timezone.now().date()

    user_object = User.objects.get(username=username)

    check_in_object, created_object = CheckIn.objects.get_or_create(patron=user_object)
    book = BriefTitle.objects.get(id=id)

    check_in_object.books.add(book)
    check_in_object.save()

    # Create a Borrow Instance
    borrow_instance = BookBorrowed.objects.create(patron=user_object)
    borrow_instance.books.add(book)
    borrow_instance.save()

    # Book History Object
    book_history = BookBorrowedHistory.objects.create(patron=user_object)
    book_history.books.add(book)
    book_history.save()

    book.book_status_id = 1
    book.date_borrowed = today
    book.date_reserved = None
    book.save()

    return redirect('user-profile', username=user_object.username)


@login_required(login_url='login')
def user_patron_home_search_reserve_book(request, username, id):
    today = timezone.now().date()

    user_object = User.objects.get(username=username)

    reservation_object, created_object = Reservation.objects.get_or_create(patron=user_object)
    book = BriefTitle.objects.get(id=id)

    reservation_object.books.add(book)
    reservation_object.save()

    # Create a BookReserve Object
    book_reserve = BookReserved.objects.create(patron=user_object)
    book_reserve.books.add(book)
    book_reserve.save()

    book.book_status_id = 3
    book.date_borrowed = None
    book.date_reserved = today
    book.save()

    return redirect('user-profile', username=user_object.username)
