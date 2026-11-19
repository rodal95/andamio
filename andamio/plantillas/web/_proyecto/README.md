# @@proyectoTitulo@@

Página web con HTML, CSS y JavaScript, sin instalar nada (ni Node ni npm).

## Ver la página

Los archivos `.js` usan `import`, y el navegador no lo permite abriendo el HTML con
doble clic: hay que servir la carpeta. Desde la carpeta del proyecto:

```
python -m http.server 5173
```

y abrí http://localhost:5173 (con la extensión Live Server de VS Code también funciona).
Se usa el puerto 5173 porque las APIs de andamio ya aceptan pedidos desde ahí.

## Agregar piezas

```
python -m andamio nuevo pagina Contacto
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

`servicio` y `crud` usan una API hecha con andamio (Django, FastAPI, Express o Next.js
full stack). Su dirección está en `js/config.js`.

## Estructura

```
index.html          página de inicio (una .html por página)
css/estilos.css     estilos de todo el sitio (+ css/componentes/)
js/menu.js          el menú de todas las páginas (ENLACES)
js/config.js        dirección de la API
js/http.js          pedir(): fetch a la API, con errores en español y el token del login
js/paginas/         el código de cada página
js/componentes/     funciones que crean partes de la página (crearTarjeta)
js/servicios/       funciones para usar un recurso de la API
```
