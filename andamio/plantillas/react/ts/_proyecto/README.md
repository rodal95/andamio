# @@proyectoTitulo@@

Aplicación web con React, Vite y TypeScript.

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
python -m andamio nuevo pagina Productos
python -m andamio nuevo hook contador
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

El servicio usa la API de Django definida en `VITE_API_URL` (archivo `.env`).

## Estructura

```
src/components/   componentes reutilizables
src/pages/        páginas
src/hooks/        hooks (use...)
src/services/     acceso a la API
```
