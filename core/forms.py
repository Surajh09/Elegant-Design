import email
from django import forms
from django.contrib.auth.models import User

class UserForm(forms.Form):
    class Meta:
        model = User
        fields= ('email', 'phone_number', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'password1':forms.PasswordInput(),
        }
        
    def save(self, commit=True):
        
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
        return User