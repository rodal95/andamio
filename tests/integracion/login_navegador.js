// Prueba en el navegador del login de React generado por andamio contra la API de Django
// con nuevo login, y de las rutas protegidas (pagina y crud con --protegido).
// La ejecuta tests/integracion/test_login_navegador.py: node login_navegador.js http://127.0.0.1:PUERTO
const { chromium } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('FALLÓ: ' + m); console.log('ok -', m); };
let p;
const errores = [];
(async () => {
  const b = await chromium.launch();
  p = await b.newPage();
  p.on('pageerror', (e) => errores.push(e.message));
  const base = process.argv[2];
  const menu = p.locator('nav');

  // Una página protegida, sin haber ingresado: lleva a /ingresar.
  await p.goto(base + '/perfil');
  await p.waitForURL(/\/ingresar$/);
  ok(await menu.getByRole('link', { name: 'Ingresar' }).isVisible(), 'sin sesión, /perfil lleva a /ingresar');

  // Crear una cuenta: primero con las contraseñas distintas (control en la página).
  await p.getByRole('link', { name: 'Registrate' }).click();
  await p.waitForURL(/\/registro$/);
  // La URL cambia antes de que se dibuje la página nueva: se espera su título (si no, se
  // escribiría en el formulario de /ingresar, que todavía está).
  await p.getByRole('heading', { name: 'Crear una cuenta' }).waitFor();
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Email').fill('ana@ejemplo.com');
  await p.getByLabel('Contraseña', { exact: true }).fill('una-clave-larga-123');
  await p.getByLabel('Repetí la contraseña').fill('otra-clave');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.getByText('Las contraseñas no coinciden.').waitFor();
  ok(true, 'las contraseñas distintas se avisan antes de enviar');

  // Bien: crea la cuenta, ingresa y vuelve a /perfil (de donde venía).
  await p.getByLabel('Repetí la contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.waitForURL(/\/perfil$/);
  await menu.getByText('ana').waitFor();
  ok(await menu.getByRole('button', { name: 'Salir' }).isVisible(), 'registrarse ingresa y vuelve a la página protegida');

  // El crud --protegido: crear con el token (la API lo pide: recurso --protegido).
  await p.goto(base + '/pedidos/nuevo');
  await p.getByLabel('Cliente').fill('Juan');
  await p.getByLabel('Total').fill('1500');
  await p.getByRole('button', { name: 'Guardar' }).click();
  await p.waitForURL(/\/pedidos\/\d+$/);
  await p.getByText('Juan').waitFor();
  ok(true, 'con sesión, el formulario protegido crea en la API protegida');

  // Recargar: la sesión sigue (el token guardado se valida con /api/yo/).
  await p.reload();
  await menu.getByText('ana').waitFor();
  ok(true, 'al recargar, la sesión sigue');

  // Salir: la página protegida vuelve a pedir ingresar; la lista del crud es libre.
  await menu.getByRole('button', { name: 'Salir' }).click();
  await menu.getByRole('link', { name: 'Ingresar' }).waitFor();
  await p.goto(base + '/pedidos');
  await p.getByText('Juan').waitFor();
  ok(true, 'sin sesión, la lista del crud protegido se ve');
  await p.goto(base + '/pedidos/nuevo');
  await p.waitForURL(/\/ingresar$/);
  ok(true, 'sin sesión, el formulario del crud protegido lleva a /ingresar');

  // Ingresar con la contraseña mal: el error de la API (401), en general.
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Contraseña').fill('mal');
  await p.getByRole('button', { name: 'Ingresar' }).click();
  await p.locator('p', { hasText: /credenciales|cuenta/i }).waitFor();
  ok(p.url().endsWith('/ingresar'), 'la contraseña incorrecta muestra el error de la API');

  // Bien: vuelve a /pedidos/nuevo (de donde venía).
  await p.getByLabel('Contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Ingresar' }).click();
  await p.waitForURL(/\/pedidos\/nuevo$/);
  ok(true, 'ingresar vuelve a la página protegida de la que venía');

  // Un token vencido (o inválido): al abrir la app, la sesión se cierra.
  await p.evaluate(() => localStorage.setItem('token', 'vencido'));
  await p.goto(base + '/perfil');
  await p.waitForURL(/\/ingresar$/);
  ok(await p.evaluate(() => localStorage.getItem('token')) === null, 'un token vencido cierra la sesión y lleva a /ingresar');

  ok(errores.length === 0, 'sin errores de JavaScript: ' + errores.join(' | '));
  await b.close();
})().catch(async (e) => {
  // Para entender un fallo: dónde estaba y qué se veía.
  if (p) console.error('en', p.url(), '\n', await p.locator('body').innerText().catch(() => ''), '\nerrores:', errores.join(' | '));
  console.error(e);
  process.exit(1);
});
