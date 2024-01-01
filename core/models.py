from tkinter import CASCADE
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .emails import send_account_activation_email
from elegent_design.models import *
from django.utils.text import slugify

# Create your models here.
class category(BaseModel):
    name = models.CharField(max_length=250)
    
    class Meta:
        ordering = ('name', )
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
    

class Customer(BaseModel):
	name = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	is_email_varified = models.BooleanField(default=False)
	email_token = models.CharField(max_length=100, null=True, blank=True)

@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    
    try:
        if created:
            email_token = str(uuid.uuid4())
            Customer.objects.create(user = instance, email_token=email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
            
            
    except Exception as e:
        print(e)

class Product(BaseModel):
    category = models.ForeignKey(category, related_name='items', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True , null=True , blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def save(self , *args , **kwargs):
        self.slug = slugify(self.name)
        super(Product ,self).save(*args , **kwargs)


class contact(BaseModel):
    user = models.OneToOneField( User , on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    
    
class Order(BaseModel):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(BaseModel):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(BaseModel):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address

