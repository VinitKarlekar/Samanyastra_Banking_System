from django.db import models
from django.utils.timezone import now

class Customer(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(unique=True)
    customer_mobile = models.CharField(max_length=15)
    customer_password = models.CharField(max_length=255)
    customer_images = models.ImageField(upload_to='customer_images/',
                                        default='/medias/customer_images/default.jpeg', 
                                        blank=True, null=True)

    def __str__(self):
        return self.customer_name

class CustomUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    aadhaar = models.CharField(max_length=12, unique=True)
    pan = models.CharField(max_length=10, unique=True) 
    account_number = models.CharField(max_length=20, unique=True) 
    password = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)

    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zips = models.CharField(max_length=10, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    branch = models.CharField(max_length=255, null=True, blank=True)
    ifsc_code = models.CharField(max_length=15, null=True, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    account_type = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    security_pin = models.CharField(max_length=6, blank=True, null=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.branch}"
    
class TransactionType(models.TextChoices):
    WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
    DEPOSIT = "DEPOSIT", "Deposit"
    TRANSFER = "TRANSFER", "Transfer"

class FlowDirection(models.TextChoices):
    INCOMING = "Incoming", "Incoming"
    OUTGOING = "Outgoing", "Outgoing"

class Transfer(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_transfers")
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_transfers", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    flow_direction = models.CharField(max_length=10, choices=FlowDirection.choices)
    transfer_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"Transfer {self.id} from {self.from_user} to {self.to_user} - {self.amount}"

class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=now)
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"{self.user.first_name} - {self.transaction_type} - {self.amount}"


from django.contrib.auth.models import User


class BankingMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}"