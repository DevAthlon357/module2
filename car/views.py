from django.shortcuts import render, redirect, get_object_or_404
from car.models import CarModel, BrandModel, BookingModel, Location, PaymentModel,WishlistModel,ReviewModel
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import math
from datetime import datetime
from django.utils import timezone
from .form import RegisterForm
from django.contrib.admin.views.decorators import staff_member_required


def Index(request):
    brands = BrandModel.objects.all()
    brand_id = request.GET.get("brand")

    if brand_id:
        selected_brand = BrandModel.objects.get(id=brand_id)
    else:
        selected_brand = brands.first()

    print("Selected brand:", selected_brand)
    print("Selected brand ID:", selected_brand.id)

    cars = CarModel.objects.filter(car_brand_id=selected_brand.id)

    print("Cars:", cars)

    return render(
        request,
        "index.html",
        {
            "brands": brands,
            "cars": cars,
            "selected_brand": selected_brand,
        },
    )


@staff_member_required
def CarList(request):
    brands = BrandModel.objects.all()
    cars = CarModel.objects.all()
    return render(request, "car_list.html", {"cars": cars, "brands": brands})


def CarCreate(request):
    brands = BrandModel.objects.all().order_by("-created_at")
    if request.method == "GET":
        return render(request, "car_create.html", {"brands": brands})
    if request.method == "POST":
        car_name = request.POST.get("car_name")
        car_brand = request.POST.get("car_brand")
        price_per_day = request.POST.get("price_per_day")
        seats = request.POST.get("seats")
        transmission = request.POST.get("transmission")
        fuel_type = request.POST.get("fuel_type")
        max_speed = request.POST.get("max_speed")
        image = request.FILES.get("image")
        car = CarModel.objects.create(
            car_name=car_name,
            price_per_day=price_per_day,
            seats=seats,
            transmission=transmission,
            fuel_type=fuel_type,
            max_speed=max_speed,
            image=image,
            car_brand_id=car_brand,
            # come from model(car_brand)=brands
        )
        car.save()
        messages.success(request, "Car created successfully")
        return redirect("/")


def CarUpdate(request, pk):
    brands = BrandModel.objects.all().order_by("-created_at")
    car = CarModel.objects.get(id=pk)

    if request.method == "GET":
        return render(request, "car_update.html", {"car": car, "brands": brands})

    if request.method == "POST":
        car_name = request.POST.get("car_name")
        car_brand = request.POST.get("car_brand")
        price_per_day = request.POST.get("price_per_day")
        seats = request.POST.get("seats")
        transmission = request.POST.get("transmission")
        fuel_type = request.POST.get("fuel_type")
        max_speed = request.POST.get("max_speed")
        image = request.FILES.get("image")

        car.car_name = car_name
        car.car_brand_id = car_brand
        car.price_per_day = price_per_day
        car.seats = seats
        car.transmission = transmission
        car.fuel_type = fuel_type
        car.max_speed = max_speed

        if image:
            car.image.delete()
            car.image = image

        car.save()
        messages.success(request, "Car updated successfully")

        return redirect("/")


def CarDelete(request, pk):
    car = CarModel.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "car_delete.html", {"car": car})
    if request.method == "POST":
        if car.image:
            car.image.delete()
        car.delete()
        messages.success(request, "Car deleted successfully")
        return redirect("/car/list/")


def BrandCreate(request):
    if request.method == "GET":
        return render(request, "brand_create.html")
    if request.method == "POST":
        name = request.POST.get("name")
        brand = BrandModel.objects.create(name=name)
        brand.save()
        return redirect("/car/list/")


def BrandUpdate(request, pk):
    brand = BrandModel.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "brand_update.html", {"brand": brand})
    if request.method == "POST":
        name = request.POST.get("name")
        brand.name = name
        brand.save()
        return redirect("/car/list/")


def BrandDelete(request, pk):
    brand = BrandModel.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "brand_delete.html", {"brand": brand})
    if request.method == "POST":
        brand.delete()
        return redirect("/car/list/")


def is_car_available(car, pickup, return_):
    return not BookingModel.objects.filter(
        car=car,
        status="confirmed",
        pickup_datetime__lt=return_,
        return_datetime__gt=pickup,
    ).exists()


@login_required(login_url="/login/")
def BookCar(request, pk):
    car = get_object_or_404(CarModel, id=pk)
    locations = Location.objects.all()

    if request.method == "POST":
        location_id = request.POST.get("location")
        location = get_object_or_404(Location, id=location_id)

        pickup_date = request.POST.get("pickup_date")
        pickup_time = request.POST.get("pickup_time")

        return_date = request.POST.get("return_date")
        return_time = request.POST.get("return_time")

        pickup_datetime = timezone.make_aware(
            datetime.strptime(f"{pickup_date} {pickup_time}", "%Y-%m-%d %H:%M")
        )

        return_datetime = timezone.make_aware(
            datetime.strptime(f"{return_date} {return_time}", "%Y-%m-%d %H:%M")
        )

        if pickup_datetime < timezone.now():
            return render(
                request,
                "booking.html",
                {
                    "car": car,
                    "locations": locations,
                    "error": "Pickup cannot be in the past",
                },
            )

        if return_datetime <= pickup_datetime:
            return render(
                request,
                "booking.html",
                {
                    "car": car,
                    "locations": locations,
                    "error": "Return must be after pickup",
                },
            )

        if not is_car_available(car, pickup_datetime, return_datetime):
            return render(
                request,
                "booking.html",
                {
                    "car": car,
                    "locations": locations,
                    "error": "Car already booked",
                },
            )

        diff = (return_datetime - pickup_datetime).total_seconds()
        days = math.ceil(diff / (60 * 60 * 24))

        total_price = days * car.price_per_day
        total_price += location.extra_price

        booking = BookingModel.objects.create(
            car=car,
            user=request.user,
            location=location,
            pickup_datetime=pickup_datetime,
            return_datetime=return_datetime,
            total_price=total_price,
            status="pending",
        )
        return redirect(f"/payment/{booking.id}/")

    return render(request, "booking.html", {"car": car, "locations": locations})


@login_required
def cancel_booking_user(request, pk):

    booking = get_object_or_404(BookingModel, id=pk, user=request.user)

    # only pending bookings can cancel
    if booking.status == "pending":
        booking.status = "cancelled"
        booking.save()

    return redirect("booking_history")


@login_required
def payment_page(request, booking_id):

    booking = get_object_or_404(BookingModel, id=booking_id)

    
    if PaymentModel.objects.filter(booking=booking).exists():
        return redirect("/booking/history/")

    if request.method == "POST":

        method = request.POST.get("method")

        screenshot = request.FILES.get("screenshot")

        PaymentModel.objects.create(
            booking=booking,
            method=method,
            amount=booking.total_price,
            screenshot=screenshot,
            status="paid",
        )

       
        booking.status = "pending"
        booking.save()

        return redirect("/booking/history/")

    return render(request, "payment.html", {"booking": booking})


@login_required
def booking_history(request):
    bookings = BookingModel.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "booking_history.html", {"bookings": bookings})


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Account created successfully")

            return redirect("login")

        else:

            for field, errors in form.errors.items():

                for error in errors:

                    messages.error(request, error)

    else:

        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


def user_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

        except:
            user = None

        if user is not None:

            login(request, user)

            messages.success(request, "Login successful")

            if next_url:
                return redirect(next_url)

            return redirect("/")

        else:

            messages.error(request, "Invalid email or password")

            return redirect("login")

    return render(request, "auth/login.html")


def user_logout(request):
    logout(request)
    return redirect("/")


@staff_member_required
def admin_dashboard(request):
    bookings = BookingModel.objects.all().order_by("-created_at")
    return render(request, "dashboard/admin_dashboard.html", {"bookings": bookings})


@staff_member_required
def confirm_booking(request, pk):
    booking = BookingModel.objects.get(id=pk)
    booking.status = "confirmed"
    booking.save()
    return redirect("admin_dashboard")


@staff_member_required
def cancel_booking(request, pk):
    booking = BookingModel.objects.get(id=pk)
    booking.status = "cancelled"
    booking.save()
    return redirect("admin_dashboard")


@login_required
def compare_cars(request):

    id1 = request.GET.get("car1")
    id2 = request.GET.get("car2")

    car1 = get_object_or_404(CarModel, id=id1)
    car2 = get_object_or_404(CarModel, id=id2)

    return render(request, "compare.html", {
        "car1": car1,
        "car2": car2,
    })


@login_required
def add_to_wishlist(request, car_id):

    car = get_object_or_404(CarModel, id=car_id)

    WishlistModel.objects.get_or_create(user=request.user, car=car)

    return redirect("/")


@login_required
def remove_wishlist(request, car_id):

    car = get_object_or_404(CarModel, id=car_id)

    WishlistModel.objects.filter(user=request.user, car=car).delete()

    return redirect("/wishlist/")

@login_required
def wishlist_page(request):

    wishlist = WishlistModel.objects.filter(
        user=request.user
    )

    return render(request, "wishlist.html", {
        "wishlist": wishlist
    })


@login_required
def add_review(request):

    if request.method == "POST":

        message = request.POST.get("message")

        ReviewModel.objects.create(user=request.user, message=message)

        messages.success(request, "Review added successfully")

        return redirect("/")


def review_page(request):

    reviews = ReviewModel.objects.all().order_by("-id")

    return render(request, "reviews.html", {"reviews": reviews})
