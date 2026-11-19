from rest_framework.routers import SimpleRouter

from .views import @@Nombre@@ViewSet

# Genera /@@plural@@/ (listar y crear) y /@@plural@@/<id>/ (ver, modificar y eliminar).
# config/urls.py las incluye debajo de /api/.
router = SimpleRouter()
router.register("@@plural@@", @@Nombre@@ViewSet, basename="@@nombre@@")

urlpatterns = router.urls
