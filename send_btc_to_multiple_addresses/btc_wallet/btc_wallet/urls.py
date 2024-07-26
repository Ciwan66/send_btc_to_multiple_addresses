from django.contrib import admin
from django.urls import path
from accounts.views import register,wallet_balances_view, user_login, create_wallet, wallet_details, home ,send_btc_view, transaction_success
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Home page
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login'), name='logout'),

    path('create_wallet/', create_wallet, name='create_wallet'),
    path('wallet_details/', wallet_details, name='wallet_details'),
    path('send-btc/', send_btc_view, name='send_btc'),
    path('transaction_success/', transaction_success, name='transaction_success'),
    path('wallet_balances/', wallet_balances_view, name='wallet_balances'),

]
