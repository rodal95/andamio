# Sitio con Django y plantillas (monolito), paso a paso

Django se puede usar de dos formas:

| | API REST (`crear django`) | Con plantillas (`crear django-web`) |
|---|---|---|
| Qué devuelve | JSON | Páginas HTML ya armadas |
| La interfaz | Otro proyecto (web, Vue, React, celular) | Las plantillas de este mismo proyecto |
| Formularios y validación | Serializers | Formularios (`forms.py`) |
| Login | Tokens JWT (`nuevo login`) | Sesión de Django (ya viene) |
| Cuándo conviene | Varias interfaces, o una app de celular | Un sitio web, todo en Python, sin JavaScript |

Esta guía es la segunda forma: un solo proyecto (un *monolito*) donde el servidor
arma cada página con los datos de la base.

## 1. Crear el proyecto

```
python -m andamio crear django-web mi-sitio
cd mi-sitio
python -m venv .venv
.venv\Scripts\activate                 (Linux o Mac: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrí http://127.0.0.1:8000. Ya funciona:

| Dirección | Qué es |
|---|---|
| `/` | Inicio (`templates/inicio.html`) |
| `/cuentas/login/` y el botón Salir | Iniciar y cerrar sesión (las vistas las trae Django) |
| `/cuentas/registro/` | Crear un usuario (`config/views.py`) |
| `/admin/` | Panel de administración |

Lo importante del proyecto:

```
config/settings.py      TEMPLATES (busca en templates/), STATICFILES_DIRS (static/), LOGIN_URL
config/urls.py          las rutas; andamio agrega una línea por cada crud y página
templates/base.html     el menú, el usuario y los mensajes: todas las páginas heredan de acá
templates/formulario.html   dibuja cualquier formulario con sus errores
static/css/estilos.css  los estilos
```

## 2. Cómo responde Django: modelo, vista y plantilla

```
navegador ── GET /productos/ ──> config/urls.py ──> productos/urls.py ──> la vista
                                                                            │
                     página HTML <── la plantilla <── los datos <── el modelo (la base)
```

1. **La ruta** (`urls.py`) dice qué vista atiende cada dirección.
2. **La vista** (`views.py`) pide los datos al **modelo** y elige una **plantilla**.
3. **La plantilla** (`.html`) muestra los datos con `{{ variable }}` y `{% for %}`.

## 3. Un CRUD completo con vistas y plantillas

```
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int --migrar
```

Crea la app `productos/`, la registra en `LOCAL_APPS`, agrega `/productos/` a
`config/urls.py` y el enlace al menú de `base.html`, y crea la tabla (`--migrar`).

**`productos/models.py`**: la tabla (igual que en la API).

**`productos/forms.py`**: el formulario. Un `ModelForm` lo arma a partir del modelo y
valida los datos (un número que no es número, un campo vacío...).

```python
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "precio", "stock"]
```

Los campos `date` y `datetime` usan el calendario del navegador (`widgets`).

**`productos/views.py`**: cinco vistas genéricas. Cada una ya sabe hacer su trabajo;
solo se les dice qué modelo, qué formulario y qué plantilla usar.

```python
class ProductoListaView(ListView):          # /productos/            (con ?q= para buscar, de a 10)
    model = Producto
    template_name = "productos/producto_lista.html"
    context_object_name = "productos"
    paginate_by = 10

class ProductoDetalleView(DetailView): ...   # /productos/3/
class ProductoCrearView(SuccessMessageMixin, CreateView): ...    # /productos/nuevo/
class ProductoEditarView(SuccessMessageMixin, UpdateView): ...   # /productos/3/editar/
class ProductoEliminarView(DeleteView): ...  # /productos/3/eliminar/  (confirma y elimina con POST)
```

Crear y editar usan el mismo formulario y la misma plantilla. Al guardar, vuelven a la
lista con un mensaje ("Se agregó «Yerba».").

**`productos/urls.py`**: rutas con nombre, dentro del espacio `productos`:

```python
app_name = "productos"

urlpatterns = [
    path("", views.ProductoListaView.as_view(), name="lista"),
    path("nuevo/", views.ProductoCrearView.as_view(), name="crear"),
    path("<int:pk>/", views.ProductoDetalleView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.ProductoEditarView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.ProductoEliminarView.as_view(), name="eliminar"),
]
```

**`productos/templates/productos/`**: las cuatro plantillas (`producto_lista.html`,
`producto_detalle.html`, `producto_form.html`, `producto_confirmar_eliminar.html`).
Por ejemplo, el detalle:

```html
{% extends "base.html" %}

{% block titulo %}{{ producto }}{% endblock %}

{% block contenido %}
  <h1>{{ producto }}</h1>
  <dl class="detalle">
    <dt>Nombre</dt>
    <dd>{{ producto.nombre }}</dd>
    <dt>Precio</dt>
    <dd>{{ producto.precio }}</dd>
  </dl>
  <a class="boton" href="{% url 'productos:editar' producto.pk %}">Editar</a>
{% endblock %}
```

**`productos/admin.py`** y **`productos/tests.py`**: el admin y 6 tests (lista, crear,
datos incompletos, detalle, editar y eliminar), que mandan el formulario como el
navegador.

```
python manage.py test
```

## 4. Las plantillas: herencia y enlaces

- `{% extends "base.html" %}` + `{% block contenido %}`: cada página escribe solo lo
  suyo; el menú y los estilos vienen de `base.html`.
- `{% url 'productos:detalle' producto.pk %}` arma la dirección por el **nombre** de la
  ruta: si la ruta cambia, los enlaces siguen funcionando. Nunca escribas
  `href="/productos/{{ producto.pk }}/"` a mano.
- `{% include "formulario.html" %}` dibuja el formulario `form` con sus errores.
- `{% csrf_token %}` va en todo formulario `POST` (Django rechaza el envío sin él).
- Filtros: `{{ producto.activo|yesno:"Sí,No" }}`, `{{ producto.vence|date:"d/m/Y" }}`.

## 5. Una página que muestra datos de la base

```
python -m andamio nuevo pagina Catalogo
```

Crea `templates/paginas/catalogo.html`, la ruta `/catalogo/` y su enlace. Esa ruta usa
un `TemplateView`: muestra la plantilla, sin datos. Para mostrar productos, se
cambia por una vista propia.

**`config/views.py`**, una función nueva:

```python
from productos.models import Producto


def catalogo(request):
    """El catálogo: los productos con stock, del más barato al más caro."""
    productos = Producto.objects.filter(stock__gt=0).order_by("precio")
    # Lo que va en el diccionario es lo que la plantilla puede usar: {{ productos }}.
    return render(request, "paginas/catalogo.html", {"productos": productos})
```

**`config/urls.py`**, la ruta apunta a esa vista (el `name` no cambia, así el menú
sigue andando):

```python
path("catalogo/", views.catalogo, name="catalogo"),
```

**`templates/paginas/catalogo.html`**:

```html
{% extends "base.html" %}

{% block contenido %}
  <h1>Catálogo</h1>
  {% for producto in productos %}
    <article class="tarjeta">
      <h3><a href="{% url 'productos:detalle' producto.pk %}">{{ producto.nombre }}</a></h3>
      <p>$ {{ producto.precio }} · {{ producto.stock }} en stock</p>
    </article>
  {% empty %}
    <p>No hay productos con stock.</p>
  {% endfor %}
{% endblock %}
```

## 6. Pedir iniciar sesión

```
python -m andamio nuevo crud pedido cliente:str total:decimal entregado:bool --protegido --migrar
```

Las vistas de crear, editar y eliminar llevan `LoginRequiredMixin`: sin sesión,
Django manda a `/cuentas/login/?next=/pedidos/nuevo/` y, al ingresar, vuelve.
La lista y el detalle siguen libres (para protegerlas, agregales el mismo mixin).

En una plantilla, para mostrar algo solo a quien ingresó:

```html
{% if user.is_authenticated %}
  <a class="boton" href="{% url 'pedidos:crear' %}">Nuevo pedido</a>
{% endif %}
```

En una vista de función, con el decorador:

```python
from django.contrib.auth.decorators import login_required

@login_required
def catalogo(request): ...
```

## 7. Una página propia con formulario

Para un formulario que no es de un modelo (por ejemplo, contacto):

```python
# config/views.py
from django import forms


class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    mensaje = forms.CharField(widget=forms.Textarea)


def contacto(request):
    form = ContactoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        messages.success(request, "¡Gracias! Te vamos a responder pronto.")
        return redirect("contacto")
    return render(request, "paginas/contacto.html", {"form": form})
```

```html
<form method="post" class="formulario">
  {% csrf_token %}
  {% include "formulario.html" %}
  <button type="submit" class="boton">Enviar</button>
</form>
```

y en `config/urls.py`: `path("contacto/", views.contacto, name="contacto")`.

## Problemas comunes

| Síntoma | Causa y solución |
|---|---|
| `TemplateDoesNotExist` | El nombre de la plantilla no coincide con el archivo. Las de una app van en `<app>/templates/<app>/`. |
| `NoReverseMatch` | El nombre en `{% url '...' %}` no existe, o falta el prefijo de la app (`productos:lista`, no `lista`). |
| 403 "CSRF verification failed" | Falta `{% csrf_token %}` dentro del `<form method="post">`. |
| `no such table: productos_producto` | Faltó la migración: `python manage.py makemigrations productos` y `python manage.py migrate`. |
| Agregué un campo al modelo y no aparece en el formulario | Sumalo a `fields` en `forms.py` (y migrá). |
| Los estilos no cargan | `{% load static %}` arriba de la plantilla y el archivo dentro de `static/`. |
