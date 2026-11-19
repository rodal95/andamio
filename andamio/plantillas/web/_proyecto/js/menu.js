// El menú de todas las páginas. andamio agrega acá un enlace por cada página que generes.
export const ENLACES = [
  { href: 'index.html', texto: 'Inicio' },
  // --- andamio:enlaces (no borrar esta línea) ---
];

/** Dibuja el menú en el elemento con el atributo data-menu y marca la página actual. */
export function dibujarMenu() {
  const barra = document.querySelector('[data-menu]');
  if (!barra) return;
  const actual = location.pathname.split('/').pop() || 'index.html';
  const nav = document.createElement('nav');
  for (const enlace of ENLACES) {
    const a = document.createElement('a');
    a.href = enlace.href;
    a.textContent = enlace.texto;
    if (enlace.href === actual) a.setAttribute('aria-current', 'page');
    nav.append(a);
  }
  barra.replaceChildren(nav);
}
