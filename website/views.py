from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import transaction
from decimal import Decimal
import logging
import random
import string
from decimal import Decimal, InvalidOperation
from .models import Customer, CustomUser, Transaction, Transfer, TransactionType, FlowDirection
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.contrib import messages
from .forms import TransferForm, CustomUserUpdateForm
from django.core.mail import send_mail
from django.utils.timezone import now
from django.http import JsonResponse
from .models import BankingMessage
from django.core.files.storage import FileSystemStorage


logger = logging.getLogger(__name__)

def home(req):
    return render(req, "home.html")

def Register(req):
    if req.method == "POST":
        customer_name = req.POST['customer_name']
        customer_mobile = req.POST['customer_mobile']
        customer_email = req.POST['customer_email']
        customer_password = req.POST['customer_password']
        
        # Check if user with the email already exists
        if Customer.objects.filter(customer_email=customer_email).exists():
            return render(req, "Register.html", {"error": "⚠️ User with this email already exists. Please login!"})

        # Handle image upload
        customer_images = req.FILES.get('customer_images')
        if customer_images:
            if not customer_images.name.lower().endswith(('.jpg', '.jpeg')):  # Restrict to JPEG
                return render(req, "Register.html", {"error": "⚠️ Only JPEG images are allowed!"})
        else:
            customer_images = "/medias/customer_images/default.jpeg"  # Default image inside media/

        # Create user
        customer = Customer.objects.create(
            customer_name=customer_name,
            customer_mobile=customer_mobile,
            customer_email=customer_email,
            customer_password=customer_password,
            customer_images=customer_images
        )

        # Store user info in session
        req.session['customer_id'] = customer.id
        req.session['customer_name'] = customer.customer_name
        req.session['customer_email'] = customer.customer_email
        req.session['customer_images'] = customer.customer_images.url 

        return redirect("/Dashboard")

    return render(req, "Register.html")

def create_account(req):
    customer = Customer(
        customer_name=req.POST['customer_name'],
        customer_mobile=req.POST['customer_mobile'],
        customer_email=req.POST['customer_email'],
        customer_password=req.POST['customer_password'],
        customer_images = req.FILES['customer_images'],
    )
    customer.save()
    return redirect("/")

def Dashboard(req):
    user_id = req.session.get("user_id")
    user_name = req.session.get("customer_name", "Guest")
    user_image = req.session.get("customer_images", "/medias/customer_images/default.jpeg") 
    return render(req, "Dashboard.html", {"user_name": user_name, "user_image": user_image})

def login(req):
    return render(req, "login.html")

def login_process(req):
    if req.method == "POST":
        customer_mobile = req.POST['customer_mobile']
        customer_password = req.POST['customer_password']
        
        customer = Customer.objects.filter(customer_mobile=customer_mobile).first()

        if not customer:
            return render(req, "login.html", {"error": "⚠️ Invalid mobile number. Please try again!"})
        elif customer.customer_password != customer_password:
            return render(req, "login.html", {"error": "⚠️ Invalid password. Please try again!"})
        else:
            req.session['customer_id'] = customer.id
            req.session['customer_name'] = customer.customer_name
            req.session['customer_email'] = customer.customer_email
            req.session['customer_password'] = customer.customer_password
            return redirect("/Dashboard")
    
    return render(req, "login.html")

def bank_informations(req):
    return render(req, "bank_informations.html")

def generate_account_number():
    return ''.join(random.choices("0123456789", k=12))

def generate_password(first_name, phone):
    last_four_digits = phone[-4:] if len(phone) >= 4 else phone
    return first_name + last_four_digits

def generate_ifsc(branch):
    bank_code = "BANK"  
    branch_code = "".join(random.choices(string.digits, k=7))  
    return f"{bank_code}{branch_code}"

def generate_security_pin():
    return str(random.randint(100000, 999999))

def save_bank_info(req):
    if req.method == "POST":
        try:
            account_number = generate_account_number()
            first_name = req.POST['first_name']
            last_name = req.POST['last_name']
            phone = req.POST['phone']
            pan = req.POST['pan']
            aadhaar = req.POST['aadhaar']
            email = req.POST['email']
            branch = req.POST['branch']
            password = generate_password(first_name, phone)
            ifsc_code = generate_ifsc(branch)  
            security_pin = generate_security_pin()  

            if CustomUser.objects.filter(pan=pan).exists():
                return render(req, "bank_informations.html", {"error": "⚠️ A user with this PAN number already exists."})
            if CustomUser.objects.filter(aadhaar=aadhaar).exists():
                return render(req, "bank_informations.html", {"error": "⚠️ A user with this Aadhaar number already exists."})

            CustomUser.objects.create(
                branch=branch,
                first_name=first_name,
                last_name=last_name,
                email=email,
                street=req.POST['street'],
                city=req.POST['city'],
                state=req.POST['state'],
                account_type=req.POST['account_type'],
                category=req.POST['category'],
                country=req.POST['country'],
                phone=phone,
                aadhaar=aadhaar,
                pan=pan,
                account_number=account_number,
                ifsc_code=ifsc_code, 
                password=make_password(password),
                security_pin=security_pin  
            )

            email_subject = "Your Bank Account & Security Details"
            email_message = (
                f"Dear {first_name} {last_name},\n\n"
                f"Your account has been successfully created. Below are your credentials:\n\n"
                f"🔹 Account Number: {account_number}\n"
                f"🔹 IFSC Code: {ifsc_code}\n"
                f"🔹 Temporary Password: {password}\n"
                f"🔹 Security PIN: {security_pin}\n\n"
                f"Please log in and change your password and security PIN for security.\n\n"
                f"Regards,\nYour Bank"
            )

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email="hariom.sharma1628@gmail.com",
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect("/bank_login/")  
        except IntegrityError:
            return render(req, "bank_informations.html", {"error": "⚠️ A user with this Aadhaar or PAN number already exists."})
    
    return render(req, "bank_informations.html", {"error": "❌ Invalid request."})

def bank_login(req):
    return render(req, "bank_login.html")

def bank_login_process(req):
    if req.method == "POST":
        account_number = req.POST["account_number"]
        password = req.POST["password"]

        user = CustomUser.objects.filter(account_number=account_number).first()

        if not user:
            return render(req, "bank_login.html", {"error": "⚠️ Invalid account number. Please try again!"})
        elif not check_password(password, user.password):
            return render(req, "bank_login.html", {"error": "⚠️ Invalid password. Please try again!"})
        else:
            req.session["user_id"] = user.id
            return redirect("/bank_details/")

    return redirect("/bank_login/")

def bank_details(req):
    user_image = req.session.get("customer_images", "/medias/customer_images/default.jpeg") 
    user_id = req.session.get("user_id")
    
    if not user_id:
        return redirect("/bank_login/")

    user = CustomUser.objects.get(id=user_id)
    return render(req, "bank.html", {"user": user, "user_image": user_image})

def user_profile(request):
    user_image = request.session.get("customer_images", "/medias/customer_images/default.jpeg")
    return render(request, "user_profile.html" , {"user_image": user_image})

def profile_view(request):
    user_id = request.session.get("user_id") 
    if not user_id:
        return redirect("/bank_login/") 

    try:
        profile = CustomUser.objects.get(id=user_id) 
    except CustomUser.DoesNotExist:
        return redirect("/bank_login/")  

    print("User Data:", profile.__dict__)  

    return render(request, "profile.html", {"profile": profile})
    
def update_profile(request):
    user_id = request.session.get("user_id") 
    if not user_id:
        return redirect("/bank_login/")  

    try:
        user = CustomUser.objects.get(id=user_id)  
    except CustomUser.DoesNotExist:
        return redirect("/bank_login/")  

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)

            if form.cleaned_data["password"]:
                user.password = make_password(form.cleaned_data["password"])

            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('/profile_view/')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserUpdateForm(instance=user)

    return render(request, 'update_profile.html', {'form': form})

def view_balance(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/bank_login/")

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('/bank_details/')

    if request.method == "POST":
        try:
            amount = request.POST.get("amount")
            entered_pin = request.POST.get("security_pin")

            if not amount or not entered_pin:
                messages.error(request, "Please enter an amount and security PIN.")
                return redirect("/view_balance/")

            if entered_pin != user.security_pin:
                messages.error(request, "Incorrect PIN! Transaction denied.")
                return redirect("/view_balance/")

            amount = Decimal(amount)

            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect("/view_balance/")

            previous_balance = user.balance
            user.balance += amount
            user.save()

            Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                previous_balance=previous_balance,
                available_balance=user.balance
            )

            messages.success(request, f"₹{amount} added successfully! New balance: ₹{user.balance}")

        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid amount entered.")
            return redirect("/view_balance/")

    return render(request, "view_balance.html", {"user": user})

def withdraw_money(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/bank_login/")

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('/bank_details/')

    if request.method == "POST":
        try:
            amount = request.POST.get("amount")
            entered_pin = request.POST.get("security_pin")

            if not amount or not entered_pin:
                messages.error(request, "Please enter an amount and security PIN.")
                return redirect("/view_balance/")

            if entered_pin != user.security_pin:
                messages.error(request, "Incorrect PIN! Transaction denied.")
                return redirect("/view_balance/")

            amount = Decimal(amount)

            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect("/view_balance/")

            if user.balance < amount:
                messages.error(request, "Insufficient balance!")
                return redirect("/view_balance/")

            previous_balance = user.balance
            user.balance -= amount
            user.save()

            Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type=TransactionType.WITHDRAWAL,
                previous_balance=previous_balance,
                available_balance=user.balance
            )

            messages.success(request, f"₹{amount} withdrawn successfully! New balance: ₹{user.balance}")

        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid amount entered.")
            return redirect("/view_balance/")

    return redirect("/view_balance/")

def transfer_money(request):
    user_id = request.session.get("user_id")  # Get user from session
    if not user_id:
        return redirect("/bank_login/")  # Redirect if session is missing

    try:
        user = CustomUser.objects.get(id=user_id)  # Fetch user manually
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect("/bank_login/")  # Redirect to login

    if request.method == "POST":
        receiver_acc = request.POST.get("receiver_acc")
        receiver_ifsc = request.POST.get("ifsc_code")
        amount = request.POST.get("amount")
        entered_pin = request.POST.get("security_pin")

        if not receiver_acc or not receiver_ifsc or not amount or not entered_pin:
            messages.error(request, "Please fill in all fields.")
            return render(request, "transfer_money.html")

        if entered_pin != user.security_pin:
            messages.error(request, "Incorrect PIN! Transaction denied.")
            return render(request, "transfer_money.html")

        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return render(request, "transfer_money.html")

            try:
                to_user = CustomUser.objects.get(account_number=receiver_acc, ifsc_code=receiver_ifsc)
            except CustomUser.DoesNotExist:
                messages.error(request, "Receiver account not found!")
                return render(request, "transfer_money.html")

            if user == to_user:
                messages.error(request, "You cannot transfer money to yourself!")
                return render(request, "transfer_money.html")

            if user.balance < amount:
                messages.error(request, "Insufficient balance!")
                return render(request, "transfer_money.html")

            # Transaction block to ensure atomicity
            with transaction.atomic():
                previous_balance_sender = user.balance
                user.balance -= amount
                user.save()

                previous_balance_receiver = to_user.balance
                to_user.balance += amount
                to_user.save()

                transfer_record = Transfer.objects.create(
                    from_user=user,
                    to_user=to_user,
                    amount=amount,
                    flow_direction=FlowDirection.OUTGOING,
                    transfer_date=now()
                )

                Transaction.objects.create(
                    user=user,
                    amount=amount,
                    transaction_type=TransactionType.TRANSFER,
                    previous_balance=previous_balance_sender,
                    available_balance=user.balance,
                    transfer=transfer_record  
                )

                Transaction.objects.create(
                    user=to_user,
                    amount=amount,
                    transaction_type=TransactionType.TRANSFER,
                    previous_balance=previous_balance_receiver,
                    available_balance=to_user.balance,
                    transfer=transfer_record  
                )

            messages.success(request, f"₹{amount} successfully transferred to {to_user.first_name}! New balance: ₹{user.balance}")
            return render(request, "transfer_money.html")  # Stay on the same page

        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid amount entered.")
            return render(request, "transfer_money.html")

    return render(request, "transfer_money.html")

def all_transactions(request):
    """Displays all transactions for the logged-in user."""
    
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/bank_login/")

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("/bank_details/")

    transaction_list = []

    transactions = Transaction.objects.filter(user=user).order_by("-created_at")

    for txn in transactions:
        transfer = txn.transfer  # ✅ Access the transfer field directly

        if transfer:
            if transfer.from_user == user:
                flow = "Outgoing"
                receiver = transfer.to_user.first_name if transfer.to_user else "Unknown"
            else:
                flow = "Incoming"
                receiver = transfer.from_user.first_name if transfer.from_user else "Unknown"
        else:
            if txn.transaction_type == TransactionType.DEPOSIT:
                flow = "N/A"
                receiver = "Bank"
            elif txn.transaction_type == TransactionType.WITHDRAWAL:
                flow = "N/A"
                receiver = "ATM/Bank"
            else:
                flow = "N/A"
                receiver = "Unknown"

        transaction_list.append({
            "date": txn.created_at.strftime("%B %d, %Y"),
            "transaction_type": txn.get_transaction_type_display(), 
            "flow": flow,
            "sender": transfer.from_user.first_name if transfer else "N/A",  # ✅ Added sender column
            "receiver": transfer.to_user.first_name if transfer else "N/A",
            "amount": f"{txn.amount:.2f}",
            "previous_balance": f"{txn.previous_balance:.2f}",
            "available_balance": f"{txn.available_balance:.2f}",
        })

    transaction_list.sort(key=lambda x: x["date"], reverse=True)

    context = {"transactions": transaction_list}
    return render(request, "all_transactions.html", context)

def all_transactions(request):
    """Displays all transactions for the logged-in user."""
    
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/bank_login/")

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("/bank_details/")

    transaction_list = []

    transactions = Transaction.objects.filter(user=user).order_by("-created_at")

    for txn in transactions:
        transfer = txn.transfer  # ✅ Access the transfer field directly

        if transfer:
            if transfer.from_user == user:
                flow = "Outgoing"
                receiver = transfer.to_user.first_name if transfer.to_user else "Unknown"
            else:
                flow = "Incoming"
                receiver = transfer.from_user.first_name if transfer.from_user else "Unknown"
        else:
            if txn.transaction_type == TransactionType.DEPOSIT:
                flow = "N/A"
                receiver = "Bank"
            elif txn.transaction_type == TransactionType.WITHDRAWAL:
                flow = "N/A"
                receiver = "ATM/Bank"
            else:
                flow = "N/A"
                receiver = "Unknown"

        transaction_list.append({
            "date": txn.created_at.strftime("%B %d, %Y"),
            "transaction_type": txn.get_transaction_type_display(), 
            "flow": flow,
            "sender": transfer.from_user.first_name if transfer else "N/A",  # ✅ Added sender column
            "receiver": transfer.to_user.first_name if transfer else "N/A",
            "amount": f"{txn.amount:.2f}",
            "previous_balance": f"{txn.previous_balance:.2f}",
            "available_balance": f"{txn.available_balance:.2f}",
        })

    transaction_list.sort(key=lambda x: x["date"], reverse=True)

    context = {"transactions": transaction_list}
    return render(request, "all_transactions.html", context)

def Messages(request):
    if not request.user.is_authenticated:
        return render(request, 'Messages.html', {'messages': []})  
    
    user = request.user
    messages = BankingMessage.objects.filter(user=user).order_by('-date')[:5]  
    return render(request, 'Messages.html', {'messages': messages})

def get_messages(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

    user = request.user
    messages = BankingMessage.objects.filter(user=user).order_by('-date')[:5]  
    message_list = [{"date": msg.date.strftime("%Y-%m-%d %H:%M"), "content": msg.content} for msg in messages]
    return JsonResponse(message_list, safe=False)

def dashboard_logout(req):
    req.session.flush()
    return redirect("/")

def acc_logout(req):
    req.session.flush()
    return redirect("/bank_login/")



