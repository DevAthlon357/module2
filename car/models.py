from django.db import models
from django.contrib.auth.models import User


# like CategoryModel
class BrandModel(models.Model):
    name= models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # for admin panel
    def __str__(self):
        return self.name


# like PostModel
class CarModel(models.Model):

    # To understand what users can write
    TRANSMISSION_CHOICES = [("auto", "automatic"), ("manual", "Manual")]

    FUEL_CHOICES = [("fuel", "Fuel"), ("electric", "Electric")]

    car_name = models.CharField(max_length=200)
    car_brand = models.ForeignKey(
        BrandModel, on_delete=models.CASCADE, null=True, blank=True
    )
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    seats = models.IntegerField(null=True, blank=True)
    transmission = models.CharField(
        max_length=10, choices=TRANSMISSION_CHOICES, null=True, blank=True
    )
    fuel_type = models.CharField(
        max_length=10, choices=FUEL_CHOICES, null=True, blank=True
    )
    max_speed = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="post_image", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # for admin panel
    def __str__(self):
        return self.car_name


# for location and booking
class Location(models.Model):
    name = models.CharField("City name",max_length=200)
    address = models.CharField(default="Unknown address")
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class BookingModel(models.Model):
    car = models.ForeignKey("CarModel", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

    pickup_datetime = models.DateTimeField(null=True)
    return_datetime = models.DateTimeField(null=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car.car_name} - {self.user.username}"


class PaymentModel(models.Model):

    booking = models.OneToOneField("BookingModel", on_delete=models.CASCADE)

    PAYMENT_METHODS = [
        ("kbz", "KBZ Pay"),
        ("wave", "Wave Pay"),
        ("uab", "UAB Pay"),
        ("aya", "AYA Pay"),
    ]

    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # 🔥 RECEIPT SCREENSHOT
    screenshot = models.ImageField(upload_to="payment_screenshot/", null=True, blank=True)

    STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(max_length=10, choices=STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.booking.id} - {self.status}"


class WishlistModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "car")

    def __str__(self):
        return f"{self.user.username} - {self.car.car_name}"


class ReviewModel(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
