from django import forms
from django.core.validators import RegexValidator

trades_url_validator = RegexValidator(
    r'^https:\/\/www\.reddit\.com\/r\/hardwareswap\/comments\/[a-z0-9]{6}\/[a-z-_]+\/$',
    'Invalid r/hardwareswap monthly trades URL'
)

class UpdateTradesForm(forms.Form):
    trades_url = forms.CharField(
        label='r/hardwareswap Monthly Trades URL', 
        max_length=200,
        required=True,
        validators=[trades_url_validator]
    )