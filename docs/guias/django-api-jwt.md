# API REST con Django + login JWT, paso a paso

Al terminar vas a tener una API con un CRUD completo de productos (modelo,
serializer, vista, rutas, admin y tests), registro de usuarios y login con tokens
JWT, y recursos que solo se pueden modificar con login.

## 1. Crear el proyecto

```
python -m andamio crear django mi-api
cd mi-api
python -m venv .venv
.venv\Scripts\activate                 (Linux o Mac: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrí http://127.0.0.1:8000/api/docs/ : la documentación interactiva (Swagger).

El proyecto ya trae la configuración para funcionar como API REST
(`config/settings.py`):

| Configuración | Para qué |
|---|---|
| `rest_framework`, `django_filters`, `corsheaders`, `drf_spectacular` en `THIRD_PARTY_APPS` | La API, los filtros, CORS y Swagger. |
| `LOCAL_APPS` | Tus apps: andamio agrega cada recurso acá. |
| `REST_FRAMEWORK` | Filtros, búsqueda y orden por defecto; listas sin paginar; decimales como número. |
| `CORS_ALLOWED_ORIGINS` (del `.env`) | Qué páginas web pueden usar la API (React, Vue, la web HTML, Next.js, Expo). |
| `SECRET_KEY`, `DEBUG`, `DATABASE_URL` (del `.env`) | Lo que cambia entre tu PC y un servidor. |

## 2. Un CRUD completo con un comando

```
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int --migrar
```

andamio crea la app `productos/`, la registra en `LOCAL_APPS` y en `config/urls.py`,
y con `--migrar` crea la tabla (`makemigrations` y `migrate`). Cada archivo:

**`productos/models.py`**: la tabla.

```python
class Producto(models.Model):
    nombre = models.CharField("Nombre", max_length=200)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    stock = models.IntegerField("Stock")
    # Fechas que Django completa solo: al crear y en cada modificación.
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["id"]

    def __str__(self):
        return self.nombre
```

**`productos/serializers.py`**: convierte un producto a JSON y valida lo que llega.

```python
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        # Lista explícita: si agregás un campo al modelo, sumalo acá para que la API lo muestre.
        fields = ["id", "nombre", "precio", "stock", "creado", "actualizado"]
        read_only_fields = ["id", "creado", "actualizado"]
```

**`productos/views.py`**: el CRUD. Un `ModelViewSet` ya sabe listar, crear, ver,
modificar y eliminar.

```python
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filterset_fields = ["nombre", "precio", "stock"]   # ?stock=10
    search_fields = ["nombre"]                          # ?search=yerba
    ordering_fields = ["id", "nombre", "precio", "stock", "creado", "actualizado"]  # ?ordering=-precio
```

**`productos/urls.py`**: las rutas, armadas por un router.

```python
router = SimpleRouter()
router.register("productos", ProductoViewSet, basename="producto")
urlpatterns = router.urls
```

**`config/urls.py`**: junta todo debajo de `/api/` (andamio agregó la línea).

```python
path("api/", include("productos.urls")),
```

**`productos/admin.py`**: el producto en el panel `/admin/`, con columnas y búsqueda.

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "precio", "stock"]
    search_fields = ["nombre"]
```

**`productos/tests.py`**: 5 tests (listar, crear, ver, modificar, eliminar).

```
python manage.py test
python manage.py createsuperuser       (para entrar a /admin/)
```

El resultado:

```
GET    /api/productos/          lista (un array JSON)
POST   /api/productos/          crea          {"nombre": "Yerba", "precio": 1500, "stock": 10}
GET    /api/productos/1/        ve uno
PUT    /api/productos/1/        reemplaza     PATCH  /api/productos/1/   modifica algunos campos
DELETE /api/productos/1/        elimina (204)
```

Si un dato está mal, la API responde **400** con los errores por campo, en español:
`{"nombre": ["Este campo es requerido."]}`.

## 3. Login con JWT (SimpleJWT)

```
python -m andamio nuevo login
pip install -r requirements.txt
```

`nuevo login` no lleva nombre: crea la app `cuentas/` una vez por proyecto. Agrega:

- `djangorestframework-simplejwt` a `requirements.txt` (por eso el `pip install`).
- Al final de `config/settings.py`:

  ```python
  INSTALLED_APPS += ["rest_framework_simplejwt"]   # sus mensajes, en español

  REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
      "rest_framework_simplejwt.authentication.JWTAuthentication",
      "rest_framework.authentication.SessionAuthentication",
  ]

  SIMPLE_JWT = {
      "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
      "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
      "AUTH_HEADER_TYPES": ("Bearer",),
  }
  ```

- Las rutas (`cuentas/urls.py`), en `/api/`:

  | Ruta | Qué hace |
  |---|---|
  | `POST /api/registro/` | Crea un usuario: `{"username", "email", "password"}` (valida la contraseña y la guarda encriptada). |
  | `POST /api/token/` | `{"username", "password"}` → `{"access", "refresh"}`. |
  | `POST /api/token/refresh/` | `{"refresh"}` → un `access` nuevo, sin volver a ingresar. |
  | `POST /api/token/verify/` | `{"token"}` → 200 si es válido. |
  | `GET /api/yo/` | El usuario dueño del token (sin token: 401). |

- 6 tests en `cuentas/tests.py`.

**Cómo funciona:** el usuario manda usuario y contraseña a `/api/token/` y recibe
dos tokens. El de **acceso** (`access`, dura 60 minutos) se manda en cada pedido:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

El de **refresco** (`refresh`, dura 7 días) sirve para pedir otro de acceso cuando
vence. La API no guarda sesiones: el token mismo dice quién sos (y está firmado con
la `SECRET_KEY`, así que no se puede falsificar).

## 4. Recursos protegidos

```
python -m andamio nuevo recurso pedido cliente:str total:decimal entregado:bool --protegido --migrar
```

`--protegido` agrega a la vista:

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class PedidoViewSet(viewsets.ModelViewSet):
    # Leer es libre; crear, modificar y eliminar necesitan login (token JWT o sesión).
    permission_classes = [IsAuthenticatedOrReadOnly]
```

y sus tests entran con un usuario (`force_authenticate`), más uno que comprueba que
sin login no se puede crear. Para que **todo** pida login, incluso leer, cambiá a
`IsAuthenticated`. Para proteger un recurso que ya existe, agregá esas dos líneas a
mano.

## 5. Probarlo

**Con Swagger** (http://127.0.0.1:8000/api/docs/): `POST /api/token/` → *Try it out* →
copiá el `access` → botón **Authorize** → pegalo. Desde ahí, cada prueba manda el token.

**Con curl** (respuestas reales):

```
curl -X POST http://127.0.0.1:8000/api/registro/ -H "Content-Type: application/json" \
     -d '{"username": "ana", "email": "ana@ejemplo.com", "password": "una-clave-larga-123"}'
{"id":1,"username":"ana","email":"ana@ejemplo.com","first_name":"","last_name":""}

curl -X POST http://127.0.0.1:8000/api/pedidos/ -H "Content-Type: application/json" \
     -d '{"cliente": "Juan", "total": 1500, "entregado": false}'
{"detail":"Las credenciales de autenticación no se proveyeron."}

curl -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" \
     -d '{"username": "ana", "password": "una-clave-larga-123"}'
{"refresh":"eyJhbGciOi...","access":"eyJhbGciOi..."}

curl -X POST http://127.0.0.1:8000/api/pedidos/ -H "Content-Type: application/json" \
     -H "Authorization: Bearer eyJhbGciOi..." -d '{"cliente": "Juan", "total": 1500, "entregado": false}'
{"id":1,"cliente":"Juan","total":1500.0,"entregado":false,"creado":"...","actualizado":"..."}
```

(En Windows CMD, usá comillas dobles afuera y `\"` adentro, o probalo en Swagger.)

**Con los tests:**

```
python manage.py test        6 del login + 6 del recurso protegido + 5 por cada recurso
```

## 6. Usarlo desde una web

Con `fetch`, el token va en el encabezado:

```js
const respuesta = await fetch('http://localhost:8000/api/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'ana', password: 'una-clave-larga-123' }),
});
const { access } = await respuesta.json();
localStorage.setItem('token', access);

await fetch('http://localhost:8000/api/pedidos/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
  body: JSON.stringify({ cliente: 'Juan', total: 1500, entregado: false }),
});
```

Las webs de andamio ya hacen la segunda parte solas: mandan el token guardado en
`localStorage` (clave `token`). En React, Vue y Next.js se guarda con
`guardarToken(tokens.access)` de `services/http`; en la web HTML, con
`localStorage.setItem('token', ...)`. Recetas con la página de ingreso:
[web HTML](combinaciones.md#login-con-jwt-desde-la-web-html) y
[React, Vue o Next.js](combinaciones.md#login-con-jwt-desde-react-vue-o-nextjs).

## Problemas comunes

| Síntoma | Causa y solución |
|---|---|
| `ModuleNotFoundError: rest_framework_simplejwt` | Faltó `pip install -r requirements.txt` después de `nuevo login`. |
| 401 "Las credenciales de autenticación no se proveyeron." | El recurso es `--protegido` y el pedido no mandó `Authorization: Bearer <token>`. |
| 401 "El token proporcionado no es válido..." | El token venció (60 minutos) o está mal copiado: pedí otro con `/api/token/refresh/` o `/api/token/`. |
| 401 "No se encontró una cuenta activa..." | Usuario o contraseña incorrectos. |
| 400 en `/api/registro/` con `password` | La contraseña no cumple `AUTH_PASSWORD_VALIDATORS` (muy corta, muy común o solo números). |
| La web dice "Failed to fetch" | La API no está andando, o la dirección de la web no está en `CORS_ALLOWED_ORIGINS` del `.env`. |
