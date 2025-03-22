from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from .models import Customer, Product, Order, OrderItem
from django.db.models import F, Sum
from decimal import Decimal

def is_admin_or_operator(user):
    return user.is_staff or user.is_superuser

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        dni = request.POST.get('dni')
        try:
            user = Customer.objects.get(email=email, dni=dni)
            if user is not None:
                login(request, user)
                return redirect('home')
        except Customer.DoesNotExist:
            messages.error(request, 'Credenciales inválidas')
    return render(request, 'store/login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        dni = request.POST.get('dni')
        if not Customer.objects.filter(email=email).exists():
            user = Customer.objects.create_user(
                username=email,
                email=email,
                dni=dni,
                password=dni  # Using DNI as password
            )
            login(request, user)
            return redirect('home')
        messages.error(request, 'El email ya está registrado')
    return render(request, 'store/register.html')

@login_required
def home(request):
    products = Product.objects.filter(active=True)
    return render(request, 'store/home.html', {'products': products})

@login_required
def product_list(request):
    products = Product.objects.filter(active=True)
    return render(request, 'store/product_list.html', {'products': products})

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0')
    
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * Decimal(quantity)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')

@login_required
def create_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'El carrito está vacío')
        return redirect('cart')
    
    order = Order.objects.create(customer=request.user)
    total = Decimal('0')
    
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        total += product.price * Decimal(quantity)
    
    order.total = total
    order.save()
    request.session['cart'] = {}
    
    return redirect('order_pdf', order_id=order.id)

@login_required
def order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Encabezado
    p.drawString(100, 750, f"Orden #{order.id}")
    p.drawString(100, 730, f"Cliente: {order.customer.email}")
    p.drawString(100, 710, f"Fecha: {order.created_at.strftime('%d/%m/%Y')}")
    
    # Detalles de items
    y = 670
    for item in order.items.all():
        p.drawString(100, y, f"{item.product.name} - Cantidad: {item.quantity} - Precio: ${item.price}")
        y -= 20
    
    p.drawString(100, y-20, f"Total: ${order.total}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@user_passes_test(is_admin_or_operator)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/admin/orders.html', {'orders': orders})

@user_passes_test(is_admin_or_operator)
def admin_update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
    return redirect('admin_orders')
