"""Vistas del proyecto que no pertenecen a ninguna app."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from productos.models import Producto


def registro(request):
    """Crea un usuario con el formulario de Django y deja la sesión iniciada."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f"¡Bienvenido/a, {usuario.username}!")
            return redirect("inicio")
    else:
        form = UserCreationForm()
    return render(request, "registration/registro.html", {"form": form})


def catalogo(request):
    """El catálogo: los productos con stock, del más barato al más caro."""
    productos = Producto.objects.filter(stock__gt=0).order_by("precio")
    # Lo que va en el diccionario es lo que la plantilla puede usar: {{ productos }}.
    return render(request, "paginas/catalogo.html", {"productos": productos})
