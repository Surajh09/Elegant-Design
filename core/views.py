from urllib import request
from django.shortcuts import *
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
from .utils import *
import datetime
# from django.contrib.auth.decorator import login_required

# Create your views here.
def home_view(request,*args,**kwargs):
    items = Product.objects.filter(is_sold = False)
    categories = category.objects.all()
    return render(request,"index.html", {
        'categories': categories,
        'items': items,
    })


def contact_view(request,*args,**kwargs):
    
    return render(request,"contact.html", {})


def store(request):
    items = Product.objects.filter(is_sold = False)
    categories = category.objects.all()
    return render(request,"store.html", {
        'categories': categories,
        'items': items,
    })


def detail(request, slug):
    item = get_object_or_404(Product, slug=slug)
    related_items = Product.objects.filter(category=item.category, is_sold=False).exclude(slug=slug)[0:3]

    return render(request, 'product_details.html', {
        'items': item,
        'related_items': related_items
    })


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'cart.html', context)


def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)


# User Handleing
def log_in_view(request,*args,**kwargs):
    
    if request.method == 'POST':
        
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(email,",", password)
        
        user_obj = User.objects.filter(username = email)
        
        if not user_obj.exists():
            messages.warning(request, "Account Not Found")
            print(user_obj,"Failure")
            return HttpResponseRedirect(request.path_info)
        
        user_obj=authenticate(username = email, password= password)
        print(user_obj)
        
        if not user_obj.customer.is_email_varified:
            print("email not verified")
            messages.warning(request, "Account Not Verfied")
            return HttpResponseRedirect(request.path_info)
        
        if user_obj:
            print(user_obj,"Success")
            login(request, user_obj)
            return redirect('/')
        
        else:
            messages.warning(request, "Invalpk Credentials")
        return HttpResponseRedirect(request.path_info)
    
    
    return render(request,"login.html", {})


def sign_in_view(request,*args,**kwargs):
    if request.method=="POST":
        first_name = request.POST.get("firstname")
        last_name = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password1")
        phone_number = request.POST.get("phone_number")
        
        user_obj = User.objects.filter(username=email)
        
        if user_obj.exists():
            messages.warning(request, "User Already Exists.")
            return HttpResponseRedirect(request.path_info)
        
        else :
            user_obj = User.objects.create(first_name = first_name, last_name = last_name, email = email, username = email)
            user_obj.set_password(password)
            contact_obj = contact.objects.create(user = user_obj, phone_number=phone_number)
            print('success')
            contact_obj.save()
            user_obj.save()
            messages.success(request, 'Verification Email Has Been Sent. Please Check Your Mail')
            return HttpResponseRedirect(request.path_info)
            
        
    return render(request,"sign_in.html", {})


def activate_email(request, email_token):

    try:
        user = Customer.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
     
    except Exception as e:
        print(e)
        return HttpResponse("Invalpk Email Token")
    
    return redirect('/')