// Prueba en el navegador del login de Next.js full stack (nuevo login): la API de este mismo
// proyecto deja la sesión en una cookie httpOnly y proxy.ts protege las páginas en el servidor.
// La ejecuta tests/integracion/test_login_navegador.py: node login_fullstack_navegador.js http://127.0.0.1:PUERTO
const { chromium, request } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('FALLÓ: ' + m); console.log('ok -', m); };
let p;
const errores = [];
(async () => {
  const b = await chromium.launch();
  p = await b.newPage();
  p.on('pageerror', (e) => errores.push(e.message));
  const base = process.argv[2];
  const menu = p.locator('nav');
  // Pedidos sin seguir redirecciones, con las cookies del navegador.
  const sinSeguir = (ruta) => p.context().request.get(base + ruta, { maxRedirects: 0 });

  // Sin sesión, el servidor (proxy.ts) responde con una redirección: la página no llega.
  const antes = await sinSeguir('/perfil/');
  ok(antes.status() === 307 && antes.headers().location.includes('/ingresar/?desde=%2Fperfil%2F'), 'sin sesión, el servidor manda a /ingresar');

  // Crear una cuenta (primero con las contraseñas distintas) y volver a /perfil/.
  await p.goto(base + '/perfil/');
  await p.waitForURL(/\/ingresar\/\?desde=/);
  await p.getByRole('link', { name: 'Registrate' }).click();
  await p.getByRole('heading', { name: 'Crear una cuenta' }).waitFor();
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Email').fill('ana@ejemplo.com');
  await p.getByLabel('Contraseña', { exact: true }).fill('una-clave-larga-123');
  await p.getByLabel('Repetí la contraseña').fill('otra-clave');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.getByText('Las contraseñas no coinciden.').waitFor();
  await p.getByLabel('Repetí la contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.waitForURL(/\/perfil\/$/);
  await menu.getByText('ana').waitFor();
  ok(await menu.getByRole('link', { name: 'Perfil' }).isVisible(), 'registrarse ingresa y vuelve a la página protegida');

  // La sesión está en una cookie httpOnly: el JavaScript de la página no la ve.
  const cookie = (await p.context().cookies()).find((c) => c.name === 'sesion');
  const visibles = await p.evaluate(() => document.cookie + '|' + localStorage.getItem('token'));
  ok(cookie?.httpOnly && !visibles.includes('sesion=') && visibles.endsWith('|null'), 'la sesión es una cookie httpOnly, sin token en localStorage');

  // El crud --protegido: crea en la API protegida (recurso --protegido) con la cookie.
  await p.goto(base + '/pedidos/nuevo/');
  await p.getByLabel('Cliente').fill('Juan');
  await p.getByLabel('Total').fill('1500');
  await p.getByRole('button', { name: 'Guardar' }).click();
  await p.waitForURL(/\/pedidos\/\d+\/$/);
  await p.getByText('Juan').waitFor();
  ok(true, 'con sesión, el formulario protegido crea en la API protegida');

  // Sin la cookie, la API protegida responde 401 (y ver es libre).
  const otro = await request.newContext({ baseURL: base });
  ok((await otro.post('/api/pedidos/', { data: { cliente: 'X', total: 1 } })).status() === 401 && (await otro.get('/api/pedidos/')).ok(), 'sin sesión, la API no deja crear');
  await otro.dispose();

  // Salir: la API borra la cookie y el servidor vuelve a pedir ingresar.
  await menu.getByRole('button', { name: 'Salir' }).click();
  await menu.getByRole('link', { name: 'Ingresar' }).waitFor();
  ok((await sinSeguir('/pedidos/nuevo/')).status() === 307, 'salir borra la cookie');

  // La lista es libre; el formulario pide ingresar, y con la contraseña mal, el error de la API.
  await p.goto(base + '/pedidos/');
  await p.getByText('Juan').waitFor();
  await p.goto(base + '/pedidos/nuevo/');
  await p.waitForURL(/\/ingresar\/\?desde=/);
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Contraseña').fill('mal');
  await p.getByRole('button', { name: 'Ingresar' }).click();
  await p.locator('p', { hasText: /credenciales|cuenta/i }).waitFor();
  await p.getByLabel('Contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Ingresar' }).click();
  await p.waitForURL(/\/pedidos\/nuevo\/$/);
  ok(true, 'la lista es libre; ingresar vuelve al formulario protegido');

  ok(errores.length === 0, 'sin errores de JavaScript: ' + errores.join(' | '));
  await b.close();
})().catch(async (e) => {
  if (p) console.error('en', p.url(), '\n', await p.locator('body').innerText().catch(() => ''), '\nerrores:', errores.join(' | '));
  console.error(e);
  process.exit(1);
});
