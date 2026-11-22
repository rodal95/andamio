# @@proyectoTitulo@@

Aplicación web con React, Vite y JavaScript.

## Primera vez

Necesitás Node.js 20.19 o más nuevo (`node --version`).

```
npm install
npm run dev
```

Abrí http://localhost:5173

## Generar código

```
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo pagina Contacto
python -m andamio nuevo hook contador
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

`pagina` y `crud` agregan su ruta en `src/App` y su enlace en el menú (`Navbar`). El servicio
y el CRUD usan la API (Django, FastAPI o Express) definida en `VITE_API_URL` (archivo `.env`).

## Estructura

```
src/components/   componentes reutilizables: el menú (Navbar), el pie (Footer) y el Layout
                  que los muestra en todas las páginas
src/App           las rutas (react-router)
src/pages/        páginas
src/hooks/        hooks (use...)
src/services/     acceso a la API
```
