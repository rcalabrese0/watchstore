from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Customer, Product, Order, OrderItem
from django.db.models import F, Sum, Q
from django.urls import reverse

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
                if user.is_staff:
                    return redirect('admin_orders')
                return redirect('product_list')
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
            return redirect('product_list')
        messages.error(request, 'El email ya está registrado')
    return render(request, 'store/register.html')

@login_required
def home(request):
    if request.user.is_staff:
        return redirect('admin_orders')
    return redirect('product_list')

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
    
    # Calcular descuento si el usuario lo tiene habilitado
    discount = Decimal('0')
    final_total = total
    if request.user.has_discount:
        discount = total * Decimal('0.10')  # 10% de descuento
        final_total = total - discount
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'discount': discount,
        'final_total': final_total
    })

@login_required
def add_to_cart(request, product_id):
    try:
        data = json.loads(request.body) if request.body else {}
        product = get_object_or_404(Product, id=product_id)
        quantity = int(data.get('quantity', 1))
        update = data.get('update', False)
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            })
        
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'error': f'No hay stock disponible'
            })
        
        cart = request.session.get('cart', {})
        
        if update:
            cart[str(product_id)] = quantity
        else:
            current_quantity = cart.get(str(product_id), 0)
            new_quantity = current_quantity + quantity
            
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'No hay suficiente stock disponible'
                })
            
            cart[str(product_id)] = new_quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
            'message': 'Producto agregado al carrito'
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def remove_from_cart(request, product_id):
    try:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({
                'success': True,
                'cart_count': sum(cart.values()),
                'message': 'Producto eliminado del carrito'
            })
        return JsonResponse({
            'success': False,
            'error': 'El producto no está en el carrito'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def checkout(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    data = json.loads(request.body)
    cart = request.session.get('cart', {})
    
    if not cart:
        return JsonResponse({'success': False, 'error': 'El carrito está vacío'})

    try:
        order = Order.objects.create(
            customer=request.user,  # El usuario ya es un Customer
            observations=data.get('observations', ''),
            shipping_method=data.get('shipping_method', ''),
            target_customer=data.get('target_customer', '') if request.user.is_staff or request.user.role == 'seller' else None
        )

        total = Decimal('0')
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            if product.stock < quantity:
                order.delete()
                return JsonResponse({
                    'success': False,
                    'error': 'No hay stock suficiente'
                })
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            
            product.stock -= quantity
            product.save()
            
            total += product.price * Decimal(str(quantity))

        # Aplicar descuento si el cliente lo tiene habilitado
        if request.user.has_discount:  # El usuario ya es un Customer
            discount = total * Decimal('0.10')  # 10% de descuento
            total = total - discount

        order.total = total
        order.save()
        
        # Limpiar el carrito
        request.session['cart'] = {}
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': 'Pedido creado correctamente'
        })

    except Exception as e:
        if 'order' in locals():
            order.delete()
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def create_order(request):
    try:
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({
                'success': False,
                'error': 'El carrito está vacío'
            })

        # Verificar stock antes de crear el pedido
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            if quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'No hay suficiente stock de {product.name}'
                })

        order = Order.objects.create(
            customer=request.user,
            status='pending'
        )

        total = Decimal('0')
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = product.price * Decimal(quantity)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            total += subtotal
            # Actualizar stock
            product.stock -= quantity
            product.save()

        order.total = total
        order.save()

        # Limpiar carrito
        request.session['cart'] = {}
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('admin_orders'),
            'message': 'Pedido creado exitosamente'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def order_pdf(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Configuración de fuentes
    p.setFont("Helvetica-Bold", 16)
    
    # Título
    p.drawString(250, 750, "COMERCIAL LA PLATA")
    p.setFont("Helvetica", 12)
    p.drawString(250, 730, "Remito de Compra")
    
    # Línea separadora
    p.line(50, 715, 550, 715)
    
    # Información del pedido
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 690, "INFORMACIÓN DEL PEDIDO")
    p.setFont("Helvetica", 10)
    p.drawString(50, 670, f"Número de Orden: #{order.id}")
    p.drawString(50, 655, f"Fecha: {order.created_at.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(50, 640, f"Cliente: {order.customer.email}")
    p.drawString(50, 625, f"Observaciones: {order.observations if order.observations else ''}")
    p.drawString(50, 610, f"Medio de transporte: {order.shipping_method if order.shipping_method else ''}")
    
    # Línea separadora
    p.line(50, 595, 550, 595)
    
    # Encabezados de la tabla
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, 580, "PRODUCTO")
    p.drawString(300, 580, "CANTIDAD")
    p.drawString(400, 580, "PRECIO UNIT.")
    p.drawString(500, 580, "SUBTOTAL")
    
    # Línea separadora
    p.line(50, 575, 550, 575)
    
    # Agrupar items por marca
    items_by_brand = {}
    for item in order.items.all():
        brand_name = item.product.brand.name if item.product.brand else " "
        if brand_name not in items_by_brand:
            items_by_brand[brand_name] = []
        items_by_brand[brand_name].append(item)
    
    # Contenido de la tabla agrupado por marca
    p.setFont("Helvetica", 10)
    y = 560
    order_total = 0
    
    for brand_name, items in items_by_brand.items():
        # Si no hay espacio suficiente para la marca y al menos un producto, nueva página
        if y < 70:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 750
            
            # Reimprime los encabezados en la nueva página
            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y-20, "PRODUCTO")
            p.drawString(300, y-20, "CANTIDAD")
            p.drawString(400, y-20, "PRECIO UNIT.")
            p.drawString(500, y-20, "SUBTOTAL")
            p.line(50, y-25, 550, y-25)
            y -= 45
        
        # Nombre de la marca
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, f"Marca: {brand_name}")
        y -= 20
        
        # Productos de la marca
        p.setFont("Helvetica", 10)
        brand_total = 0
        
        for item in items:
            if y < 50:  # Nueva página si no hay espacio
                p.showPage()
                p.setFont("Helvetica", 10)
                y = 750
                
                # Reimprime los encabezados en la nueva página
                p.setFont("Helvetica-Bold", 10)
                p.drawString(50, y-20, "PRODUCTO")
                p.drawString(300, y-20, "CANTIDAD")
                p.drawString(400, y-20, "PRECIO UNIT.")
                p.drawString(500, y-20, "SUBTOTAL")
                p.line(50, y-25, 550, y-25)
                y -= 45
            
            subtotal = item.price * item.quantity
            brand_total += subtotal
            order_total += subtotal
            
            p.drawString(70, y, item.product.name[:35])  # Indentado para mostrar que pertenece a la marca
            p.drawString(300, y, str(item.quantity))
            p.drawString(400, y, f"${item.price:.2f}")
            p.drawString(500, y, f"${subtotal:.2f}")
            y -= 20
        
        # Subtotal por marca
        p.setFont("Helvetica-Bold", 10)
        p.drawString(380, y, f"Subtotal {brand_name}:")
        p.drawString(500, y, f"${brand_total:.2f}")
        y -= 30  # Espacio extra entre marcas
    
    # Línea separadora antes del total
    p.line(50, y+5, 550, y+5)
    
    # Total final
    p.setFont("Helvetica-Bold", 12)
    
    # Si el cliente tiene descuento, mostrarlo
    if order.customer.has_discount:
        p.drawString(350, y-20, "SUBTOTAL:")
        p.drawString(500, y-20, f"${order_total:.2f}")
        
        # Calcular y mostrar el descuento
        discount = order_total * Decimal('0.1')
        final_total = order_total - discount
        
        p.drawString(350, y-40, "DESCUENTO (10%):")
        p.drawString(500, y-40, f"-${discount:.2f}")
        
        p.drawString(350, y-60, "TOTAL FINAL:")
        p.drawString(500, y-60, f"${final_total:.2f}")
        y -= 80  # Ajustar el espacio para el pie de página
    else:
        p.drawString(400, y-20, "TOTAL FINAL:")
        p.drawString(500, y-20, f"${order_total:.2f}")
        y -= 40  # Ajustar el espacio para el pie de página
    
    # Pie de página
    p.setFont("Helvetica", 8)
    p.drawString(50, 30, "Este documento sirve como comprobante de compra")
    p.drawString(50, 15, f"Generado el {order.created_at.strftime('%d/%m/%Y %H:%M')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="orden_{order.id}.pdf"'
    return response

@user_passes_test(is_admin_or_operator)
def admin_orders(request):
    orders = Order.objects.all()
    
    search_query = request.GET.get('q', '')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(total__icontains=search_query) |
            Q(created_at__icontains=search_query)
        )
    
    orders = orders.order_by('-created_at')
    return render(request, 'store/admin/orders.html', {
        'orders': orders,
        'search_query': search_query
    })

@user_passes_test(is_admin_or_operator)
def admin_update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
    return redirect('admin_orders')
