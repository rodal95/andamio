// Prueba en el navegador de una página de CRUD de Reflex (crud o crud-api: tienen la misma
// interfaz). La ejecuta tests/integracion/test_reflex.py:
//   node crud_reflex.js http://localhost:3000/productos
// La página tiene que tener los campos de test_coherencia.CAMPOS.
const { chromium } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('FALLÓ: ' + m); console.log('ok -', m); };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  const errores = [];
  p.on('pageerror', (e) => errores.push(e.message));
  p.on('dialog', (d) => d.accept());
  await p.goto(process.argv[2], { waitUntil: 'networkidle' });
  await p.getByText('Todavía no hay registros.').waitFor({ timeout: 60000 });
  ok(true, 'lista vacía');

  const campos = { Nombre: 'Yerba mate', Descripcion: '1 kg', Precio: '123456789012', Stock: '24', Peso: '1', Vence: '2026-12-01', Publicado: '2026-11-19T10:30', Contacto: 'ventas@ejemplo.com' };
  for (const [etiqueta, valor] of Object.entries(campos)) await p.getByLabel(etiqueta, { exact: true }).fill(valor);
  await p.getByLabel('Activo', { exact: true }).click();
  await p.getByRole('button', { name: 'Guardar' }).click();
  await p.getByText(/dígitos/).waitFor({ timeout: 15000 });
  ok(true, 'error de validación debajo del campo: ' + (await p.getByText(/dígitos/).innerText()));

  await p.getByLabel('Precio', { exact: true }).fill('4850.5');
  await p.getByRole('button', { name: 'Guardar' }).click();
  await p.getByRole('cell', { name: 'Yerba mate' }).waitFor({ timeout: 15000 });
  const celdas = await p.locator('tbody tr').first().locator('td').allInnerTexts();
  ok(celdas.some((c) => c.startsWith('4850.5')), 'agregar y verlo en la tabla (precio ' + celdas[2] + ')');
  ok(celdas.includes('Sí'), 'booleano mostrado como Sí');

  await p.getByRole('button', { name: 'Editar' }).click();
  await p.waitForFunction(() => document.querySelector('#nombre')?.value === 'Yerba mate');
  ok((await p.getByLabel('Publicado', { exact: true }).inputValue()) === '2026-11-19T10:30', 'el formulario de edición trae los datos (fecha y hora incluida)');
  await p.getByLabel('Stock', { exact: true }).fill('7');
  await p.getByRole('button', { name: 'Guardar' }).click();
  await p.getByRole('cell', { name: '7', exact: true }).waitFor({ timeout: 15000 });
  ok((await p.locator('tbody tr').count()) === 1, 'editar (stock 24 → 7) sin duplicar');

  await p.getByRole('button', { name: 'Eliminar' }).click();
  await p.getByText('Todavía no hay registros.').waitFor({ timeout: 15000 });
  ok(true, 'eliminar');
  ok(errores.length === 0, 'sin errores de JavaScript ' + errores.join(' '));
  await b.close();
})().catch((e) => { console.error(e.message); process.exit(1); });
