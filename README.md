# Watch Store - Sistema de Gestión de Pedidos

Este proyecto es una aplicación web desarrollada con Django para gestionar una tienda de relojes, incluyendo funcionalidades de carrito de compras, gestión de pedidos y panel de administración.

## Estructura del Proyecto

```
watchstore/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   ├── watchstore/          # Configuración principal del proyecto
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── store/              # Aplicación principal
│   │   ├── models.py       # Modelos de datos
│   │   ├── views.py        # Lógica de la aplicación
│   │   ├── urls.py         # Rutas de la aplicación
│   │   ├── admin.py        # Configuración del panel admin
│   │   └── templates/      # Plantillas HTML
│   │       └── store/
│   │           ├── base.html
│   │           ├── home.html
│   │           ├── login.html
│   │           ├── register.html
│   │           ├── product_list.html
│   │           ├── cart.html
│   │           └── admin/
│   │               ├── orders.html
│   │               └── update_order.html
│   ├── manage.py
│   └── requirements.txt
└── README.md
```

## Modelos de Datos

### Customer (Cliente)
- Extiende de AbstractUser
- Campos adicionales:
  - `dni`: Número de identificación
  - `phone`: Teléfono
  - `address`: Dirección

### Product (Producto)
- `name`: Nombre del producto
- `description`: Descripción
- `price`: Precio
- `image`: Imagen del producto
- `active`: Estado del producto

### Order (Pedido)
- `customer`: Relación con Cliente
- `created_at`: Fecha de creación
- `status`: Estado del pedido (pendiente, confirmado, en proceso, listo, completado, cancelado)
- `total`: Monto total
- `notes`: Notas internas
- `last_updated`: Última actualización

### OrderItem (Item de Pedido)
- `order`: Relación con Pedido
- `product`: Relación con Producto
- `quantity`: Cantidad
- `price`: Precio al momento de la compra

## Funcionalidades Principales

1. **Gestión de Usuarios**
   - Registro de clientes
   - Login/Logout
   - Perfiles de usuario

2. **Catálogo de Productos**
   - Listado de productos
   - Detalles de producto
   - Gestión de stock

3. **Carrito de Compras**
   - Agregar/quitar productos
   - Actualizar cantidades
   - Calcular totales

4. **Gestión de Pedidos**
   - Crear pedidos
   - Actualizar estados
   - Generar PDF de pedido
   - Panel de administración

## Requisitos

- Docker
- Docker Compose

## Configuración del Entorno

1. **Clonar el repositorio**
```bash
git clone <repositorio>
cd watchstore
```

2. **Variables de entorno**
Crear archivo `.env` en la raíz del proyecto:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=watchstore
DB_USER=watchstore
DB_PASSWORD=watchstore123
DB_HOST=db
DB_PORT=5432
```

## Iniciar el Proyecto

1. **Construir y levantar los contenedores**
```bash
docker compose up -d --build
```

2. **Ejecutar migraciones**
```bash
docker compose exec web python manage.py migrate
```

3. **Crear superusuario (opcional)**
```bash
docker compose exec web python manage.py createsuperuser
```

4. **Cargar datos de ejemplo (opcional)**
```bash
docker compose exec web python manage.py loaddata initial_data
```

La aplicación estará disponible en: http://localhost:8000

## Acceso al Panel de Administración

- URL: http://localhost:8000/admin
- Usuario: (email del superusuario)
- Contraseña: (contraseña del superusuario)

## Estados de Pedidos

1. **Pendiente**: Pedido recién creado
2. **Confirmado**: Pedido verificado y aceptado
3. **En Proceso**: Pedido en preparación
4. **Listo para Entregar**: Pedido preparado
5. **Completado**: Pedido entregado
6. **Cancelado**: Pedido cancelado

## Desarrollo

Para ejecutar los tests:
```bash
docker compose exec web python manage.py test
```

Para ver los logs:
```bash
docker compose logs -f web
```

## Seguridad

- Todas las rutas requieren autenticación excepto login y registro
- Los estados de pedidos solo pueden ser modificados por staff
- Las contraseñas se almacenan hasheadas
- CSRF protection habilitado
- Debug mode debe desactivarse en producción

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.
