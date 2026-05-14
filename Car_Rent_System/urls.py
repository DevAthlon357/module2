from django.contrib import admin
from django.urls import path
from car import views
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.Index),
    path("car/list/", views.CarList),
    path("car/create/", views.CarCreate),
    path("car/update/<int:pk>/", views.CarUpdate),
    path("car/delete/<int:pk>/", views.CarDelete),
    path("brand/create/", views.BrandCreate),
    path("brand/update/<int:pk>/", views.BrandUpdate),
    path("brand/delete/<int:pk>/", views.BrandDelete),
    path("booking/<int:pk>/", views.BookCar, name="book_car"),
    path("payment/<int:booking_id>/", views.payment_page, name="payment"),
    path("booking/history/", views.booking_history, name="booking_history"),
    path("cancel-booking/<int:pk>/", views.cancel_booking_user, name="cancel_booking"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("confirm/<int:pk>/", views.confirm_booking),
    path("cancel/<int:pk>/", views.cancel_booking),
    path("compare/", views.compare_cars, name="compare"),
    path("wishlist/", views.wishlist_page, name="wishlist"),
    path("wishlist/add/<int:car_id>/", views.add_to_wishlist, name="add_wishlist"),
    path(
        "wishlist/remove/<int:car_id>/", views.remove_wishlist, name="remove_wishlist"
    ),
    path("review/add/", views.add_review, name="add_review"),
    path("reviews/", views.review_page, name="reviews"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
