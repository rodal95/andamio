# @@proyectoTitulo@@

API REST con Express, Prisma (SQLite) y Zod.

## Primera vez

Necesitás Node.js 22.12 o más nuevo (`node --version`).

```
npm install
npm run dev
```

La API queda en http://localhost:8000/api/ y la documentación interactiva en
http://localhost:8000/docs (funciona sin internet).

## Agregar un recurso

```
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int
npx prisma migrate dev --name productos
```

El recurso queda en `/api/productos/`, con la misma forma que las APIs de Django y
FastAPI: los servicios y el CRUD de React y React Native funcionan igual. Tipos de
campo: `str`, `text`, `int`, `decimal`, `float`, `bool`, `date`, `datetime`, `email`.

**Cada vez que cambies `prisma/schema.prisma`** (por ejemplo, le agregás un campo a un
modelo), creá una migración: `npx prisma migrate dev --name <qué cambió>`. Las
migraciones quedan en `prisma/migrations/` y se suben a git.

## Comandos

```
npm run dev       la API, que se reinicia sola cuando guardás un cambio
npm test          los tests de todos los recursos (usan otra base: test.db)
npm run tipos     revisa los tipos de TypeScript
npx prisma studio una página para ver y editar los datos de la base
```

## Estructura

```
src/servidor.ts        arranca la API (npm run dev)
src/app.ts             la aplicación: CORS, rutas de cada recurso, /docs y errores
src/config.ts          configuración leída del .env (puerto, base, CORS, zona horaria)
src/db.ts              conexión a la base de datos (Prisma)
src/validacion.ts      funciones para validar los datos, con mensajes en español
src/errores.ts         errores con el formato de Django REST: 400 {campo: [mensaje]}, 404
src/fechas.ts          cómo salen las fechas en el JSON
src/docs.ts            la documentación de Swagger
src/<recurso>/         esquema.ts (validación y JSON) y router.ts (las rutas de la API)
prisma/schema.prisma   las tablas de la base de datos
tests/                 tests de cada recurso
```
