from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from shoppinglyx.settings import RAZORPAY_ID, RAZORPAY_SECRET_KEY
from .models import *
from .forms import *
from django.contrib import messages
from django_email_verification import send_email
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import razorpay

shipping_amount = 70.0
total_items = 0

class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        if request.user.is_authenticated:
            total_items = len(Cart.objects.filter(user=request.user))
        else:
            total_items = 0
        return render(request, 'app/home.html', {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles, 'laptops':laptops, 'total_items':total_items})

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        is_item_already_present = False
        if request.user.is_authenticated:
            total_items = len(Cart.objects.filter(user=request.user))
            is_item_already_present = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        else:
            total_items = 0
        return render(request, 'app/productdetail.html', {'product':product, 'is_item_already_present':is_item_already_present, 'total_items':total_items})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart/')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        total_amt = 0.0
        total_items = len(Cart.objects.filter(user=request.user))
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                amt = (p.quantity * p.product.discounted_price)
                amount += amt
                total_amt = amount + shipping_amount
            return render(request, 'app/showcart.html', {'cart':cart, 'total_amt':total_amt, 'amount':amount, 'shipping':shipping_amount, 'total_items':total_items})
        else:
            return render(request, 'app/emptycart.html', {'total_items':total_items})

@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        ct = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        ct.quantity += 1
        ct.save()
        amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            amt = (p.quantity * p.product.discounted_price)
            amount += amt
            data = {
                'quantity': ct.quantity,
                'amount': amount,
                'total_amount':amount + shipping_amount,
            }
        return JsonResponse(data)

@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        ct = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        ct.quantity -= 1
        ct.save()
        amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            amt = (p.quantity * p.product.discounted_price)
            amount += amt
            data = {
                'quantity': ct.quantity,
                'amount': amount,
                'total_amount':amount + shipping_amount,
            }
        return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        ct = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        ct.delete()
        amount = 0.0
        itm = 0
        total_items = len(Cart.objects.filter(user=request.user))
        data = {
            'amount': amount,
            'total_amount':amount + shipping_amount,
            'total_items': total_items,
        }
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            amt = (p.quantity * p.product.discounted_price)
            amount += amt
            itm += p.quantity
            data = {
                'amount': amount,
                'total_amount':amount + shipping_amount,
                'total_items': total_items + itm -1,
            }
        return JsonResponse(data)

@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        if request.user.is_authenticated:
            total_items = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'total_items':total_items})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            total_items = len(Cart.objects.filter(user=request.user))
            messages.success(request, 'Address added successfully !')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'total_items':total_items})

@login_required
def address(request):
    addr = Customer.objects.filter(user=request.user)
    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html', {'addr':addr, 'active':'btn-primary', 'total_items':total_items})

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html', {'op':op, 'total_items':total_items})

def mobile(request, data=None):
    if data == None:
        mob = Product.objects.filter(category='M')
    elif data == 'Samsung' or data == 'LG' or data == 'Apple':
        mob = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mob = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mob = Product.objects.filter(category='M').filter(discounted_price__gte=10000)

    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    else:
        total_items = 0

    return render(request, 'app/mobile.html', {'mob':mob, 'total_items':total_items})

def laptop(request, data=None):
    if data == None:
        lap = Product.objects.filter(category='L')
    elif data == 'DELL' or data == 'HP' or data == 'Lenovo':
        lap = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        lap = Product.objects.filter(category='L').filter(discounted_price__lt=25000)
    elif data == 'above':
        lap = Product.objects.filter(category='L').filter(discounted_price__gte=25000)

    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    else:
        total_items = 0
    return render(request, 'app/laptop.html', {'lap':lap, 'total_items':total_items})

def top_wear(request, data=None):
    if data == None:
        tp = Product.objects.filter(category='TW')
    elif data == 'POLO' or data == 'FaShIoN':
        tp = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'below':
        tp = Product.objects.filter(category='TW').filter(discounted_price__lt=700)
    elif data == 'above':
        tp = Product.objects.filter(category='TW').filter(discounted_price__gte=700)

    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    else:
        total_items = 0
    return render(request, 'app/top_wear.html', {'tp':tp, 'total_items':total_items})

def bottom_wear(request, data=None):
    if data == None:
        bt = Product.objects.filter(category='BW')
    elif data == 'POLO' or data == 'Levis':
        bt = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'below':
        bt = Product.objects.filter(category='BW').filter(discounted_price__lt=1000)
    elif data == 'above':
        bt = Product.objects.filter(category='BW').filter(discounted_price__gte=1000)

    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    else:
        total_items = 0
    return render(request, 'app/bottom_wear.html', {'bt':bt, 'total_items':total_items})

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()    
        return render(request, 'app/customerregistration.html', {'form':form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        msg = None
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data.get('email')).exists():
                msg = "This Email already exists!"
            else:
                user = form.save()
                send_email(user)
                return redirect('email_sent')
        return render(request, 'app/customerregistration.html', {'form':form, 'msg':msg})

@login_required
def checkout(request):
    user = request.user
    addr = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            amt = (p.quantity * p.product.discounted_price)
            amount += amt
        total_amount = amount + shipping_amount
    if request.user.is_authenticated:
        total_items = len(Cart.objects.filter(user=request.user))
    tot_amt = int(total_amount)*100
    client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET_KEY))
    DATA = {
        "amount": tot_amt,
        "currency": "INR",
        "payment_capture": "1",
    }
    payment = client.order.create(data=DATA)

    return render(request, 'app/checkout.html', {'addr':addr, 'shipping_amount':shipping_amount, 'total_amount':total_amount, 'cart_items':cart_items, 'total_items':total_items, 'tot_amt':tot_amt, 'rp_id':RAZORPAY_ID})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

def email_sent(request):
    return render(request, 'app/email_sent.html')

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def refund_policy(request):
    return render(request, 'app/refund_policy.html')

def t_and_c(request):
    return render(request, 'app/t_and_c.html')

def contact_us(request):
    return render(request, 'app/contact.html')

def about_us(request):
    return render(request, 'app/about.html')
