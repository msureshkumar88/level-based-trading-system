from django import template
from currency_converter import CurrencyConverter

register = template.Library()
import string


@register.simple_tag(name='convert_currency')
def convert_currency(amount, trade_currency, user_currency):
    c = CurrencyConverter()
    amount = float(c.convert(amount, trade_currency.upper(), user_currency.upper()))
    return "%.2f" % round(amount, 2)



# @register.simple_tag(name='add_text')
# def add_text(text1, text2):
#     return text1 + text2 + "it works"