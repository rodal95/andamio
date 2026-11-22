"""Vistas del proyecto que no pertenecen a ninguna app."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


# Abierta aunque todo el sitio pida login (nuevo login --obligatorio): si no, nadie podría
# crear su usuario.
@login_not_required
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
