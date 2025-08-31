from django import forms
from .models import CustomerAddress,OrderComplain,PlacedOder
from Vendors.models import WithdrawRequest

class WithdrawRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawRequest
        fields = ["amount"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount"}),
        }
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = PlacedOder
        fields = ['payment_method', 'transaction_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_id'].required = False


class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerAddress
        fields = ['state','city','zip_code','street_address','mobile']
        widgets = {
            'state': forms.TextInput(attrs={'class':'form-control'}),
            'city': forms.TextInput(attrs={'class':'form-control'}),
            'zip_code': forms.NumberInput(attrs={'class':'form-control'}),
            'street_address': forms.Textarea(attrs={'class':'form-control','rows':5,'cols':50}),
            'mobile': forms.NumberInput(attrs={'class':'form-control'}),
        }



class OrderComplainForm(forms.ModelForm):
    class Meta:
        model = OrderComplain
        fields = ['order_number', 'message']