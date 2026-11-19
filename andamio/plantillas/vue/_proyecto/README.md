# @@proyectoTitulo@@

Aplicación web con Vue 3, Vite y Vue Router, en JavaScript.

## Primera vez

```
npm install
npm run dev
```

y abrí http://localhost:5173

## Agregar piezas

```
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo pagina Contacto
python -m andamio nuevo composable contador
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

`servicio` y `crud` usan una API hecha con andamio (Django, FastAPI, Express o
Next.js full stack). Su dirección está en `VITE_API_URL` (archivo `.env`).

## Estructura

```
src/main.js         crea la aplicación
src/App.vue         el menú y el lugar donde se muestra cada página (<RouterView />)
src/router.js       las rutas: qué página va en cada dirección
src/pages/          las páginas
src/components/     componentes reutilizables (.vue)
src/composables/    funciones use... para reutilizar estado y lógica
src/services/       funciones para usar la API
```
