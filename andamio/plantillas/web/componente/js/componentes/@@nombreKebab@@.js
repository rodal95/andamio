/**
 * Crea un elemento @@nombreTitulo@@. Sus estilos están en css/componentes/@@nombreKebab@@.css.
 * Uso:
 *   import { crear@@Nombre@@ } from '../componentes/@@nombreKebab@@.js';
 *   lista.append(crear@@Nombre@@({ titulo: 'Yerba', texto: '$ 1500' }));
 * @param {{ titulo: string, texto?: string }} datos
 * @returns {HTMLElement}
 */
export function crear@@Nombre@@({ titulo, texto = '' }) {
  const elemento = document.createElement('article');
  elemento.className = '@@nombreKebab@@';

  const h3 = document.createElement('h3');
  h3.textContent = titulo; // textContent (no innerHTML): así un dato nunca se ejecuta como HTML.
  const p = document.createElement('p');
  p.textContent = texto;

  elemento.append(h3, p);
  return elemento;
}
