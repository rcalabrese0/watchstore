def cart_processor(request):
    if not request.user.is_authenticated:
        return {'cart_count': 0}
    
    cart = request.session.get('cart', {})
    cart_count = sum(quantity for quantity in cart.values())
    return {'cart_count': cart_count}
