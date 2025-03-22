from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Product, Order, OrderItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'dni', 'phone', 'date_joined', 'is_staff')
    search_fields = ('email', 'dni', 'phone')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('-date_joined',)
    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'dni', 'phone', 'address')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active', 'show_image')
    list_filter = ('active',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'active')
    
    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50"/>', obj.image.url)
        return "Sin imagen"
    show_image.short_description = 'Imagen'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'status', 'total', 'show_pdf')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__email', 'customer__dni')
    readonly_fields = ('created_at', 'total')
    inlines = [OrderItemInline]
    
    def show_pdf(self, obj):
        return format_html('<a class="button" href="{}">Ver PDF</a>', 
                         f'/order/{obj.id}/pdf/')
    show_pdf.short_description = 'PDF'
