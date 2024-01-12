"""Cataloging URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from catalogue import views
from Cataloging import settings
from catalogue.admin import custom_admin_site

urlpatterns = [
    path('catalogue-admin/', custom_admin_site.urls),
    path('', views.index, name='homepage'),
    path('catalogue', views.cataloging, name='cataloging'),
    path('details/', views.details, name='details'),
    path('profile/', views.profile_page, name='profile'),
    path('reports/', views.reports, name='reports'),
    path('profile/check-in/', views.check_in, name='check-in'),
    path('book-returns/<str:isbn>/<int:id>', views.book_returns, name='book-returns'),
    path('book-returns/check-out/<str:isbn>/', views.book_returns_check_out, name='check-out-book-returns'),
    path('profile/<int:id>/', views.patron_borrows, name='patron-borrows'),
    path('profile/patron-signup/', views.patron_registration, name='patron-form'),
    path('notification/', views.patron_due_dates, name='notifications'),
    path('due-dates/students/download-pdf/', views.due_dates_students_pdf, name='due-dates-pdf-students'),
    path('due-dates/faculty/download-pdf/', views.due_dates_faculty_pdf, name='due-dates-pdf-faculty'),
    path('patron/due-dates/<int:position>/', views.patron_due_dates_filter, name='position-deadlines'),
    path('details/subjects/', views.filtered_subjects, name='subjects'),
    path('details/alphabetic/', views.alphabetical_books, name='alphabetical'),
    path('details/authors/', views.authors_filter, name='authors'),
    path('details/subjects/download-pdf/', views.sorted_subjects_pdf, name="subjects-pdf"),
    path('details/alphabetic/download-pdf/', views.books_alphabetical_pdf, name='alphabetic-pdf'),
    path('details/authors/download-pdf/', views.authors_pdf, name="authors-pdf"),
    path('details/available-books/download-pdf/', views.available_books_pdf, name="available-books-pdf"),
    path('profile/check-out/', views.check_out, name="check-out"),
    path('profile/reservation/', views.reservation, name="reserve"),
    path('profile/reservation/<int:id>/', views.patron_reservation_profile, name='reservation-profile'),
    path('borrow/reservation/<str:isbn>/<int:id>/<int:patron>/', views.book_borrow_reserve, name='reservation-borrow'),
    path('login/', views.authentication, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.registration_validation_online, name='register'),
    path('profile-patron/<str:username>/', views.user_patron_profile, name='user-profile'),
    path('profile-patron/check-in/<str:username>/', views.user_profile_check_in, name='user-profile-check-in'),
    path('profile-patron/reservation/<str:username>/', views.user_profile_reserve_book, name='user-profile-reserve'),
    path('profile-patron/borrow-history/<str:username>/', views.user_profile_book_borrowed_history,
         name='user-profile-history'),
    path('profile-patron/<str:username>/user-id/', views.user_profile_identification_data, name='user-profile-id'),
    path('status/borrowed/', views.borrowed_books, name='borrowed-books'),
    path('status/borrowed/download-pdf', views.borrowed_books_pdf, name='borrowed-books-pdf'),
    path('status/reserved/', views.reserved_books, name='reserved-books'),
    path('status/reserved/download-pdf', views.reserved_books_pdf, name='reserved-books-pdf'),
    path('status/available/', views.available_books, name='available-books'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance, name='attendance'),
    path('registration/', views.registration_validation, name='registration-validation'),
    path('registration/confirmation/', views.confirming_registrations, name='confirming'),
    path('registration/confirmation/<str:username>/', views.confirm_user_registration, name='confirm'),
    path('registration/decline/<str:username>/', views.declined_registration, name='decline'),
    path('registration/profile/<str:username>/', views.registering_patron_profile, name='registering_profile'),
    path('deadline/None/', views.no_deadline_check_in, name='no_deadline_checkin'),
    path('deadline/None/download-pdf/', views.no_deadline_check_in_pdf, name='no-deadline-checkin-pdf'),
    path('attendance/list/', views.attendance_list, name='attendance-list'),
    path('attendance/list/download-pdf/', views.attendance_list_pdf, name='attendance-list-pdf'),
    path('attendance/list-daily/download-pdf/', views.attendance_list_filtered_daily_pdf,
         name='attendance-list-daily-pdf'),
    path('attendance/qr-code-scan/', views.qr_code_scanner, name='qr-code-attendance'),
    path('fines-paid/<str:username>/', views.fines_paid_cash, name='fines-paid-cash'),
    path('paid-fines/', views.paid_fines, name='paid-fines'),
    path('paid-fines/download-pdf', views.paid_fines_pdf, name='paid-fines-pdf'),
    path('unpaid-fines/', views.unpaid_fines, name='unpaid-fines'),
    path('unpaid-fines/download-pdf', views.unpaid_fines_pdf, name='unpaid-fines-pdf'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('enter-token/<str:email>/', views.enter_token, name='enter-token'),
    path('change-password/<str:email>/<str:token>/', views.change_password, name='change-password'),
    path('user-profile/borrow-search-book/<str:username>/<int:id>/', views.user_patron_home_search_borrow_book,
         name='borrow-search-book'),
    path('user-profile/reserve-search-book/<str:username>/<int:id>/', views.user_patron_home_search_reserve_book,
         name='reserve-search-book'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path('profile/patron/', views.patron_profile, name='profile-patron'),
