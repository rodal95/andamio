# @@proyectoTitulo@@

Aplicación full stack con Next.js (App Router), en JavaScript: las páginas y la API en el mismo
proyecto, con una base de datos SQLite (Prisma) y validación con Zod.

## Primera vez

Necesitás Node.js 22.12 o más nuevo (`node --version`).

```
npm install
npm run dev
```

Abrí http://localhost:3000

## Agregar un recurso (API + páginas)

```
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int --migrar
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

`recurso` crea la API en `app/api/productos/` (con su tabla en `prisma/schema.prisma`) y
`crud` las páginas que la usan: `/productos`, `/productos/nuevo`, `/productos/3` y
`/productos/3/editar`. Usá los mismos campos en los dos. `--migrar` crea la tabla; sin
esa opción: `npx prisma migrate dev --name productos`.

La API tiene la misma forma que las de Django, FastAPI y Express (`/api/productos/`,
errores 400 en español por campo), así que también la puede usar una app de React o de
React Native: http://IP-DE-TU-PC:3000/api

Tipos de campo: `str`, `text`, `int`, `decimal`, `float`, `bool`, `date`, `datetime`, `email`.

**Cada vez que cambies `prisma/schema.prisma`**, creá una migración:
`npx prisma migrate dev --name <qué cambió>`.

## Más piezas

```
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo pagina Contacto
python -m andamio nuevo hook contador
```

## Comandos

```
npm run dev       la aplicación, que se actualiza sola cuando guardás un cambio
npm test          los tests de la API (usan otra base: test.db)
npm run build     la versión para publicar (después: npm start)
npx prisma studio una página para ver y editar los datos de la base
```

## Estructura

```
app/                  las páginas: app/productos/page es /productos
app/layout            el menú y lo que rodea a todas las páginas
app/api/<recurso>/    la API: route (listar y crear) y [id]/route (ver, modificar, eliminar)
components/           componentes reutilizables
hooks/                hooks (use...)
services/             funciones que usan las páginas para hablar con la API
lib/                  base de datos, validación, errores y fechas (los usa la API)
prisma/schema.prisma  las tablas de la base de datos
proxy.ts              qué otras páginas pueden usar la API (CORS)
tests/                tests de la API
```
