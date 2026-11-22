// El menú y el pie de todas las páginas. andamio agrega acá un enlace por cada página que generes.
// --- andamio:imports (no borrar esta línea) ---

export const ENLACES = [
  { href: 'index.html', texto: 'Inicio' },
  // --- andamio:enlaces (no borrar esta línea) ---
];

/**
 * Dibuja el menú en el elemento con el atributo data-menu (y marca la página actual) y el pie
 * en el elemento con data-pie. Todas las páginas lo llaman al empezar.
 */
export function dibujarMenu() {
  // --- andamio:menu (no borrar esta línea) ---
  const barra = document.querySelector('[data-menu]');
  if (barra) {
    const actual = location.pathname.split('/').pop() || 'index.html';
    const nav = document.createElement('nav');
    for (const enlace of ENLACES) {
      // Los enlaces soloConSesion (páginas --protegido) los agrega el menú de la sesión.
      if (enlace.soloConSesion) continue;
      const a = document.createElement('a');
      a.href = enlace.href;
      a.textContent = enlace.texto;
      if (enlace.href === actual) a.setAttribute('aria-current', 'page');
      nav.append(a);
    }
    // --- andamio:menu_sesion (no borrar esta línea) ---
    barra.replaceChildren(nav);
  }
  dibujarPie();
}

/** Dibuja el pie en el elemento con el atributo data-pie. */
function dibujarPie() {
  const pie = document.querySelector('[data-pie]');
  if (!pie) return;
  const texto = document.createElement('small');
  texto.textContent = `© ${new Date().getFullYear()} @@proyectoTitulo@@`;
  pie.replaceChildren(texto);
}
