from datetime import date, datetime
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, User)
from django.conf import settings
import uuid


class Customer(models.Model):
    customerId = models.IntegerField()
    customerName = models.CharField(max_length=80)
    customerAddress = models.CharField(max_length=80)
    customerPhone = models.CharField(max_length=80)
    customerEmail = models.CharField(max_length=80)
    customerStatus = models.BooleanField()
    customerComment = models.CharField(max_length=80)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def publish(self, request):
        self.save()

    def get_absolute_url(self):
        return reverse("customer_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("customer_update", args=(self.pk,))


class OrderData(models.Model):
    orderNumber = models.CharField(max_length=80, default=-1)
    quantity = models.IntegerField()
    color_CHOICES = [
        ("red", 'Rot'),
        ("yellow", 'Gelb'),
        ("blue", 'Blau'),
        ("green", 'Grün'),
    ]
    color = models.CharField(
        max_length=10,
        choices=color_CHOICES,
        default="red",
    )
    screw_CHOICES = [
        ("round", 'Rund'),
        ("hexagon", 'Sechskant'),
    ]
    screw = models.CharField(
        max_length=10,
        choices=screw_CHOICES,
        default="round",
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    orderStatus_CHOICES = [
        ("NEW", 'Neu'),
        ("PROCESSING", 'In Bearbeitung'),
        ("FINISHED", 'Beendet'),
    ]
    orderStatus = models.CharField(
        max_length=10, choices=orderStatus_CHOICES, default="NEW")
    orderDate = models.DateTimeField(blank=True, null=True)
    orderTime = models.TimeField(blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kw):
        # if self._state.adding:
        #     insert_list = []
        #     for i in range(self.quantity):
        #         #Abruf der höchsten Bestellnummer, z.B. HTW-0001-1
        #         try:
        #             max_code=OrderData.objects.latest('id').orderNumber
        #         except:
        #             max_code="HTW-0000-0"
        #         #Abtrennen der letzten 6 Zeichen, z.B. 0001-1
        #         max_code = max_code[-6:]
        #         #Abtrennen der vorderen 4 Zeiche, z.B. 0001
        #         max_code = int(max_code[:4])
        #         #Erhöhung des Zählers um eins, 0001 wird zu 2
        #         max_code += 1
        #         #Voranstellen von führenden Nullen, 2 wird zu 0002
        #         max_code= f"{max_code:04d}"
        #         #Zusammenführen der einzelen Bestandteile, HTW-0002, Anzeige des aktuellen Teils -> bei Menge 2 dann -1 und -2
        #         self.orderNumber = "HTW-"+str(max_code)+"-"+str(i+1)
        #         self.orderTime = datetime.now()
        #         self.orderDate = datetime.now()
        #         insert_list.append(OrderData(orderNumber=self.orderNumber,quantity=self.quantity, orderTime=self.orderTime, orderDate=self.orderDate, screw=self.screw, color=self.color, orderStatus=self.orderStatus, customer=self.customer ))
        #     self.objects.bulk_create(insert_list)
        if self._state.adding:
            print("SELF:", self)
            for i in range(self.quantity):
                # Abruf der höchsten Bestellnummer, z.B. HTW-0001-1
                try:
                    max_code = OrderData.objects.latest('id').orderNumber
                except:
                    max_code = "HTW-0000"
                # Abtrennen der letzten 6 Zeichen, z.B. 0001-1
                max_code = int(max_code[-4:])
                # Abtrennen der vorderen 4 Zeiche, z.B. 0001
                #max_code = int(max_code[:4])
                # Erhöhung des Zählers um eins, 0001 wird zu 2
                max_code += 1
                # Voranstellen von führenden Nullen, 2 wird zu 0002
                max_code = f"{max_code:04d}"
                # Zusammenführen der einzelen Bestandteile, HTW-0002, Anzeige des aktuellen Teils -> bei Menge 2 dann -1 und -2
                self.orderNumber = "HTW-"+str(max_code)
                self.orderTime = datetime.now()
                self.orderDate = datetime.now()
                return super(OrderData, self).save(*args, **kw)
            return super(OrderData, self).save(*args, **kw)

    def publish(self, request):
        self.save()

    def get_absolute_url(self):
        return reverse("order_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("order_update", args=(self.pk,))


def order_post_save(instance, created, *args, **kwargs):
    if created == True:
        for i in range(instance.quantity):
            stationsCount = Stations.objects.filter(stationStatus=True).count()
            for j in range(stationsCount):
                OrderStatus.objects.create(
                    orderStation=j+1,
                    orderNumber=instance,
                    orderStatus=instance.orderStatus,
                    orderPart=i+1,
                    employee="",
                    orderStatusDescription=""
                )
            # OrderData.objects.create(orderNumber="HTW-0010-[i]",orderDate=datetime.now(), orderTime=datetime.now(), customer=instance.customer, orderStatus="NEW", quantity=instance.quantity)


post_save.connect(order_post_save, sender=OrderData)


class OrderStatus(models.Model):
    orderNumber = models.ForeignKey(OrderData, on_delete=models.CASCADE)
    orderStation_CHOICES = [
        (1, 'Station 1'),
        (2, 'Station 2'),
        (3, 'Station 3'),
        (4, 'Station 4'),
        (5, 'Station 5'),
        (6, 'Station 6'),
    ]
    orderStation = models.IntegerField(
        choices=orderStation_CHOICES,
        default=1,
    )
    orderPart = models.CharField(max_length=10)
    timeBeginn = models.DateTimeField(blank=True, null=True)
    timeEnd = models.DateTimeField(blank=True, null=True)
    employee = models.CharField(max_length=80)
    orderStatus = models.CharField(max_length=10)
    orderStatusDescription = models.CharField(max_length=80)


class QualityData(models.Model):
    orderNumber = models.ForeignKey(OrderData, on_delete=models.CASCADE)
    orderPart = models.CharField(max_length=10)
    quality = models.CharField(max_length=80)
    qualityDate = models.DateTimeField(blank=True, null=True)
    qualityStatus = models.CharField(max_length=10)
    qualityComment = models.CharField(max_length=80)


class Stations(models.Model):
    stationName = models.CharField(max_length=80)
    stationId = models.IntegerField()
    stationStatus = models.BooleanField()
    stationLocation = models.CharField(max_length=80)


class GameRound(models.Model):
    gameRoundId = models.IntegerField()
    gameRoundStatus = models.BooleanField()
    gameRoundComment = models.CharField(max_length=80)
    gameRoundDate = models.DateField()


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
            Creates and saves a User with the given email and password.
            """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
            Creates and saves a staff user with the given email and password.
            """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
            Creates and saves a superuser with the given email and password.
            """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

    def create_studentuser(self, email, password, ):
        """
            Creates and saves a superuser with the given email and password.
            """
        user = self.create_user(
            email,
            password=password,
        )
        user.student = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=25, default="")
    last_name = models.CharField(max_length=25, default="")
    postalcode = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=25, default="")
    adress = models.CharField(max_length=25, default="")
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser
    student = models.BooleanField(default=False)  # a user who is a student
    identifier = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=True)

    # notice the absence of a "Password field", that is built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    @property
    def is_student(self):
        "Is the user a student?"
        return self.student

    def get_update_url(self):
        return reverse("user_update", args=(self.pk,))

    def get_absolute_url(self):
        return reverse("user_update", args=(self.pk,))

    object = UserManager()
