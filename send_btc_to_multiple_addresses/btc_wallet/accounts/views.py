from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .utils import create_legacy_wallet , send_btc ,get_wallet_balances
from .models import CustomUser , BitcoinTransaction
from django.shortcuts import render
from django.contrib import messages
from .forms import SendBtcForm
from decimal import Decimal, InvalidOperation
import uuid

@login_required
def wallet_balances_view(request):
    wallet_name=request.user.wallet_name
    balances = get_wallet_balances(wallet_name)
    if balances is None:
        balances = {
            'available_balance': 0.0,
            'pending_balance': 0.0,
            'immature_balance': 0.0
        }
    return render(request, 'accounts/wallet_balances.html', balances)

@login_required
def home(request):
    has_wallet = request.user.wallet_name is not None and request.user.wallet_name != ''
    return render(request, 'accounts/home.html', {'has_wallet': has_wallet})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def create_wallet(request):
    if request.method == 'POST':
        # Generate a random wallet name
        wallet_name = str(uuid.uuid4())  # or any other method to generate a unique name

        # Create wallet and get address and private key
        address, private_key = create_legacy_wallet(wallet_name)

        if address and private_key:
            user = request.user
            user.wallet_name = wallet_name
            user.bitcoin_address = address
            user.private_key = private_key
            user.save()
            return redirect('wallet_details')
        else:
            # Handle the case where wallet creation fails
            return render(request, 'accounts/home.html', {'error': 'Failed to create wallet'})
    return render(request, 'accounts/home.html')
@login_required
def wallet_details(request):
    return render(request, 'accounts/wallet_details.html', {
        'address': request.user.bitcoin_address,
        'private_key': request.user.private_key,
    })

def send_btc_view(request):
    if request.method == 'POST':
        form = SendBtcForm(request.POST)
        if form.is_valid():
            recipients_input = form.cleaned_data['recipients']

            # Parse recipients input
            recipients = {}
            try:
                for entry in recipients_input.split(','):
                    address, amount = entry.split(':')
                    recipients[address.strip()] = Decimal(amount.strip())  # Convert to Decimal
            except (ValueError, InvalidOperation) as e:
                messages.error(request, f"Invalid input format or value: {e}")
                return redirect('send_btc')

            # Get sender's private key from the profile
            try:
                private_key = request.user.private_key  # Replace with actual private key retrieval
                wallet_name = request.user.wallet_name  # Replace with actual private key retrieval
                if not private_key:
                    raise ValueError("Private key is missing.")
            except AttributeError:
                messages.error(request, "User profile is not set up correctly.")
                return redirect('send_btc')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('send_btc')

            # Call the send_btc function
            try:
                tx_id = send_btc(wallet_name,private_key, recipients, fee_rate_satoshi_per_byte=1000)
                if tx_id:
                    messages.success(request, f"Transaction sent successfully. TX ID: {tx_id}")
                else:
                    messages.error(request, "Transaction failed.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

            return redirect('send_btc')
    else:
        form = SendBtcForm()

    return render(request, 'accounts/send_btc.html', {'form': form})





@login_required
def transaction_success(request):
    return render(request, 'accounts/transaction_success.html')