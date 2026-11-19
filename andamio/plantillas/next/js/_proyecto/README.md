# @@proyectoTitulo@@

Aplicación web con Next.js (App Router), en JavaScript, que usa una API: la que hiciste con andamio
en Django, FastAPI o Express.

## Primera vez

Necesitás Node.js 20.9 o más nuevo (`node --version`).

```
npm install
npm run dev
```

Abrí http://localhost:3000

## Generar piezas

```
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo pagina Contacto
python -m andamio nuevo hook contador
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

`pagina` y `crud` agregan su enlace en el menú (`app/layout`). Con Next.js no hace falta
registrar rutas: cada carpeta de `app/` con un `page` es una dirección. El servicio y el
CRUD usan la API definida en `NEXT_PUBLIC_API_URL` (archivo `.env`), con los mismos
campos que el recurso de la API.

## Estructura

```
app/              las páginas: app/contacto/page es /contacto
app/layout        el menú y lo que rodea a todas las páginas
components/       componentes reutilizables
hooks/            hooks (use...)
services/         funciones para usar la API
public/           archivos que se sirven tal cual (imágenes, íconos)
```
