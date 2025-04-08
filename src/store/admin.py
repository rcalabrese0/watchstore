from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Product, Order, OrderItem, Brand, Category

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'dni', 'is_staff')
    search_fields = ('username', 'email', 'dni')
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

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name',)
    list_filter = ('active',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'parent', 'active')
    list_filter = ('brand', 'active', 'parent')
    search_fields = ('name', 'brand__name')
    autocomplete_fields = ['parent', 'brand']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            if request.resolver_match.kwargs.get('object_id'):
                # Excluir la categoría actual y sus descendientes al editar
                category = Category.objects.get(pk=request.resolver_match.kwargs['object_id'])
                kwargs["queryset"] = Category.objects.exclude(
                    pk__in=[category.pk] + list(category.children.values_list('pk', flat=True))
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'display_order', 'active', 'show_image')
    list_filter = ('brand', 'category', 'active')
    search_fields = ('name', 'sku', 'brand__name', 'category__name')
    autocomplete_fields = ['brand', 'category']
    list_editable = ('price', 'display_order', 'stock', 'active')
    ordering = ('display_order', 'name')
    list_per_page = 50
    save_as = True
    save_on_top = True
    
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
    list_display = ('id', 'customer', 'status', 'total', 'created_at', 'show_pdf')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__email', 'customer__username')
    readonly_fields = ('created_at', 'total')
    inlines = [OrderItemInline]
    
    def show_pdf(self, obj):
        return format_html('<a class="button" href="{}">Ver PDF</a>', 
                         f'/order/{obj.id}/pdf/')
    show_pdf.short_description = 'PDF'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    autocomplete_fields = ['order', 'product']
