# Estilos: tema, partes de interfaz y estilos propios

Tres piezas para que lo que generás se vea bien y se pueda cambiar desde un solo lugar.
Funcionan igual en la web HTML, Django con plantillas, Vue, React y Next.js (y el tema
también en React Native y Reflex).

```
python -m andamio nuevo tema [<color>] [--modo auto|claro|oscuro]   el look de todo el proyecto
python -m andamio nuevo ui <parte>                                   una parte de interfaz lista
python -m andamio nuevo estilo <nombre>                              el CSS de tu componente o página
```

Los comandos **agregan** archivos y los conectan: nunca reescriben el CSS que ya tenés.

## 1. El tema: `nuevo tema`

```
python -m andamio nuevo tema violeta --modo auto
```

| Opción | Valores |
|---|---|
| `<color>` | `azul` (si no ponés nada), `verde`, `violeta`, `naranja`, `rojo`, `turquesa`, `rosa`, `ambar`, `gris` |
| `--modo` (`--mode`) | `auto`: claro u oscuro según el sistema (si no ponés nada) · `claro` · `oscuro` |

Genera un archivo de **variables CSS** y lo carga en todo el proyecto:

| Tecnología | Archivo | Dónde se carga |
|---|---|---|
| Web HTML | `css/tema.css` | `@import` en `css/estilos.css` |
| Django con plantillas | `static/css/tema.css` | `<link>` en `templates/base.html` |
| Vue | `src/tema.css` | `import` en `src/main.js` |
| React | `src/tema.css` | `import` en `src/main` |
| Next.js | `app/tema.css` | `import` en `app/layout` |
| React Native | `constants/tema` | se usa con `useTema()` (no hay CSS) |
| Reflex | `mi_app/tema.py` | `app.theme = TEMA` en `mi_app/mi_app.py` |

Las variables:

| Variable | Para qué |
|---|---|
| `--acento` | el color principal: botones, enlaces, foco |
| `--acento-texto` | el texto sobre `--acento` (blanco en claro, oscuro en oscuro) |
| `--fondo`, `--superficie` | el fondo de la página y el de tarjetas, tablas y campos |
| `--texto`, `--suave` | el texto y el texto secundario |
| `--borde` | líneas y bordes |
| `--peligro`, `--exito`, `--aviso` | errores, confirmaciones y avisos |
| `--radio`, `--espacio` | el redondeo de los bordes y el espacio base |
| `--sombra`, `--sombra-alta` | sombras suave y fuerte |
| `--fuente`, `--fuente-mono` | la letra y la letra de código |

Además trae estilos base (botones, `.boton`, `.boton--borde`, `.boton--peligro`, campos,
tablas, `.error`), así lo que generaron `crud` y `pagina` cambia de look sin tocarlo.

**Usalas en tu CSS:**

```css
.destacado {
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: var(--radio);
  color: var(--acento);
}
```

**Modo claro u oscuro a mano** (por ejemplo, con un botón):

```js
document.documentElement.dataset.tema = 'oscuro';   // o 'claro'; borrar el dato vuelve a "auto"
```

**Cambiar de tema:** borrá el archivo del tema y generalo de nuevo
(`nuevo tema verde --modo oscuro`), o editá los valores a mano.

**React Native:**

```tsx
import { useTema } from '@/constants/tema';

const tema = useTema();   // los colores del modo actual
<View style={[estilos.tarjeta, { backgroundColor: tema.superficie }]}>
  <Text style={{ color: tema.acento }}>Hola</Text>
</View>
```

## 2. Partes de interfaz: `nuevo ui <parte>`

```
python -m andamio nuevo ui <parte>
```

| Parte | Qué trae |
|---|---|
| `tarjetas` | grilla que se acomoda sola, tarjeta con imagen, título, texto y botones |
| `alertas` | mensajes de éxito, error, aviso e información |
| `modal` | ventana modal con `<dialog>` (sin librerías) |
| `navbar` | barra de navegación que en el celular se pliega en ☰ (sin JavaScript) |
| `badges` | etiquetas chicas para estados o categorías |
| `tabs` | pestañas sin JavaScript |
| `paginacion` | números de página para listas largas |
| `cargando` | ruedita de carga y esqueletos animados |
| `responsive` | mejoras para el celular: tablas como tarjetas, formularios a todo el ancho |
| `accesible` | foco visible, texto para lectores de pantalla, saltar al contenido, menos movimiento |

Cada una queda en la carpeta de estilos (`css/ui/`, `static/css/ui/`, `src/ui/` o
`app/ui/`), se carga sola y **tiene el ejemplo de uso al principio del archivo**. Usan
las variables del tema, pero también funcionan sin tema.

Ejemplo, `nuevo ui tarjetas`:

```html
<div class="tarjetas">
  <article class="tarjeta">
    <h3 class="tarjeta__titulo">Yerba</h3>
    <p class="tarjeta__texto">$ 1500</p>
    <div class="tarjeta__pie"><a class="boton" href="#">Ver</a></div>
  </article>
</div>
```

En React y Next.js se escribe `className` en lugar de `class` (y `htmlFor` en lugar de
`for`, en `tabs`). En una plantilla de Django, `nuevo ui paginacion` va con `page_obj`:

```html
{% if is_paginated %}
  <nav class="paginacion" aria-label="Páginas">
    {% if page_obj.has_previous %}<a href="?page={{ page_obj.previous_page_number }}">Anterior</a>{% endif %}
    <span aria-current="page">{{ page_obj.number }}</span>
    {% if page_obj.has_next %}<a href="?page={{ page_obj.next_page_number }}">Siguiente</a>{% endif %}
  </nav>
{% endif %}
```

## 3. Tu propio estilo: `nuevo estilo <nombre>`

Para tu componente o tu página, con el nombre que quieras:

```
python -m andamio nuevo estilo <nombre>
```

Por ejemplo, `nuevo estilo catalogo` crea `estilos/catalogo.css` (en la carpeta de
estilos del proyecto) con la clase `.catalogo` y sus partes `.catalogo__titulo` y
`.catalogo__texto`, ya armadas con las variables del tema y con su versión para el
celular, y lo carga en el proyecto. Usá la clase:

```html
<section class="catalogo">
  <h2 class="catalogo__titulo">Catálogo</h2>
  <p class="catalogo__texto">Los productos del mes.</p>
</section>
```

En React y Next.js, si preferís estilos que solo afecten a un componente, seguí usando
el `.module.css` que trae cada `componente` y `pagina`: también puede usar
`var(--acento)` y las demás variables.

## Una receta: darle estilo a un crud

```
python -m andamio nuevo crud <nombre> <campo:tipo>...      (por ejemplo: producto nombre:str precio:decimal)
python -m andamio nuevo tema verde
python -m andamio nuevo ui alertas
python -m andamio nuevo ui responsive
```

- El tema cambia los botones, los campos y la tabla del crud.
- `alertas` sirve para los mensajes: `<p class="alerta alerta--error" role="alert">...`.
- `responsive` hace que la tabla se vea como tarjetas en el celular. Para que cada dato
  lleve su título, agregá `data-label` a las celdas: `<td data-label="Precio">`.
