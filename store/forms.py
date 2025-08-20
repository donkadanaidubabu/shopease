from django import forms

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your shipping address'}),
        label="Shipping Address"
    )
