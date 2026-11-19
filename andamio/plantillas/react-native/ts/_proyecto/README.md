# @@proyectoTitulo@@

Aplicación móvil con Expo, Expo Router y TypeScript.

## Primera vez

Necesitás Node.js 22.13 o más nuevo (`node --version`).

```
npm install
npx expo start
```

Apretá `a` para abrirla en el emulador de Android, `w` para abrirla en el navegador,
o escaneá el código QR con la app Expo Go.

## Generar código

```
python -m andamio nuevo pantalla detalle-producto
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo hook contador
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

El servicio usa la API (Django, FastAPI o Express) definida en `EXPO_PUBLIC_API_URL` (archivo `.env`).

## Estructura

```
app/          pantallas (cada archivo es una ruta)
components/   componentes reutilizables
hooks/        hooks (use...)
services/     acceso a la API
constants/    datos generales
```
