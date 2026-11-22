// Prueba en el navegador de nuevo login --obligatorio (React) contra la API de Django: sin
// sesión no se ve nada de la app (ni el menú, ni el pie); con sesión, todo.
// La ejecuta tests/integracion/test_login_navegador.py: node login_obligatorio_navegador.js http://127.0.0.1:PUERTO
const { chromium } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('FALLÓ: ' + m); console.log('ok -', m); };
let p;
const errores = [];
(async () => {
  const b = await chromium.launch();
  p = await b.newPage();
  p.on('pageerror', (e) => errores.push(e.message));
  const base = process.argv[2];

  // Sin sesión, cualquier página lleva a /ingresar, sin menú ni pie.
  await p.goto(base + '/nosotros');
  await p.waitForURL(/\/ingresar(\?.*)?$/);
  await p.getByRole('heading', { name: 'Ingresar' }).waitFor();
  ok(await p.locator('nav').count() === 0 && await p.locator('footer').count() === 0, 'sin sesión: /ingresar, sin menú ni pie');

  // Crear una cuenta: vuelve a /nosotros, ahora con el menú y el pie.
  await p.getByRole('link', { name: 'Registrate' }).click();
  await p.getByRole('heading', { name: 'Crear una cuenta' }).waitFor();
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Email').fill('ana@ejemplo.com');
  await p.getByLabel('Contraseña', { exact: true }).fill('una-clave-larga-123');
  await p.getByLabel('Repetí la contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.waitForURL(/\/nosotros$/);
  await p.locator('nav').getByText('ana').waitFor();
  ok(await p.locator('footer').isVisible(), 'con sesión: la página, el menú y el pie');

  // La página --protegido tiene su enlace solo en el menú de la sesión.
  await p.locator('nav').getByRole('link', { name: 'Perfil' }).click();
  await p.waitForURL(/\/perfil$/);
  ok(true, 'el enlace a la página protegida está en el menú de la sesión');

  // Salir: de vuelta a /ingresar, sin menú ni pie.
  await p.locator('nav').getByRole('button', { name: 'Salir' }).click();
  await p.waitForURL(/\/ingresar(\?.*)?$/);
  ok(await p.locator('nav').count() === 0, 'salir lleva a /ingresar y oculta el menú');

  ok(errores.length === 0, 'sin errores de JavaScript: ' + errores.join(' | '));
  await b.close();
})().catch(async (e) => {
  if (p) console.error('en', p.url(), '\n', await p.locator('body').innerText().catch(() => ''), '\nerrores:', errores.join(' | '));
  console.error(e);
  process.exit(1);
});
