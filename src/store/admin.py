from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Customer, Product, Order, OrderItem, Brand, Category

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'role', 'has_discount')
    list_filter = ('role', 'has_discount', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone', 'dni')
    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'password', 'first_name', 'last_name', 'dni', 'phone', 'address')
        }),
        ('Configuración', {
            'fields': ('role', 'has_discount', 'is_active')
        }),
        ('Permisos', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:  # Si es un nuevo usuario
            fieldsets = (
                ('Información Personal', {
                    'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'dni', 'phone', 'address')
                }),
                ('Configuración', {
                    'fields': ('role', 'has_discount', 'is_active')
                }),
            )
        return fieldsets

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

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        import_id_fields = ['id']
        fields = ('id', 'name', 'brand', 'category', 'price', 'stock', 'display_order')

class OrderItemResource(resources.ModelResource):
    class Meta:
        model = OrderItem
        import_id_fields = ['id']
        fields = ('id', 'order', 'product', 'quantity', 'price')

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        import_id_fields = ['id']
        fields = ('id', 'customer', 'created_at', 'status', 'total')

class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
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

class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = ('id', 'customer', 'status', 'total', 'created_at', 'show_pdf')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__email', 'customer__username')
    readonly_fields = ('created_at', 'total')
    inlines = [OrderItemInline]
    
    def show_pdf(self, obj):
        return format_html('<a class="button" href="{}">Ver PDF</a>', 
                         f'/order/{obj.id}/pdf/')
    show_pdf.short_description = 'PDF'

class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    autocomplete_fields = ['order', 'product']

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
