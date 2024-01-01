from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from core.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    path('activate/<email_token>', activate_email),
    path('contact/', contact_view),
	path('store/', store, name="store"),
	path('store/<slug>', detail),
	path('cart/', cart, name="cart"),
	path('checkout/', checkout, name="checkout"),
	path('update_item/', updateItem, name="update_item"),
	path('process_order/', processOrder, name="process_order"),
    path('login/', log_in_view),
    path('signin/', sign_in_view),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
