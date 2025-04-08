from django.apps import AppConfig

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = "Comercial La Plata Admin"
        admin.site.site_title = "Comercial La Plata Admin Portal"
        admin.site.index_title = "Welcome to Comercial La Plata Admin"
