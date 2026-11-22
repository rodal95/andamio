// Prueba en el navegador del login de la web en HTML y JS (nuevo login) contra la API de
// Django, con una página --protegido. La ejecuta tests/integracion/test_login_navegador.py:
//   node login_web_navegador.js http://127.0.0.1:PUERTO
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

  // La página protegida, sin sesión: lleva a ingresar.html; el menú no muestra Perfil.
  await p.goto(base + '/perfil.html');
  await p.waitForURL(/\/ingresar\.html\?desde=perfil\.html$/);
  await menu.getByRole('link', { name: 'Ingresar' }).waitFor();
  ok(await menu.getByRole('link', { name: 'Perfil' }).count() === 0 && await p.locator('footer').isVisible(), 'sin sesión: ingresar.html, sin el enlace protegido y con el pie');

  // Crear una cuenta (primero con las contraseñas distintas) y volver a perfil.html.
  await p.getByRole('link', { name: 'Registrate' }).click();
  await p.waitForURL(/\/registro\.html\?desde=perfil\.html$/);
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Email').fill('ana@ejemplo.com');
  await p.getByLabel('Contraseña', { exact: true }).fill('una-clave-larga-123');
  await p.getByLabel('Repetí la contraseña').fill('otra');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.getByText('Las contraseñas no coinciden.').waitFor();
  await p.getByLabel('Repetí la contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Crear la cuenta' }).click();
  await p.waitForURL(/\/perfil\.html$/);
  await menu.getByText('ana').waitFor();
  ok(await menu.getByRole('link', { name: 'Perfil' }).isVisible(), 'registrarse ingresa, vuelve a la página protegida y el menú muestra Perfil');

  // Salir: a index.html, y el menú vuelve a Ingresar.
  await menu.getByRole('button', { name: 'Salir' }).click();
  await p.waitForURL(/\/index\.html$/);
  await menu.getByRole('link', { name: 'Ingresar' }).waitFor();
  ok(true, 'salir');

  // Ingresar con la contraseña mal y bien.
  await p.goto(base + '/perfil.html');
  await p.waitForURL(/\/ingresar\.html/);
  await p.getByLabel('Usuario').fill('ana');
  await p.getByLabel('Contraseña').fill('mal');
  await p.getByRole('button', { name: 'Ingresar' }).click();
  await p.locator('#error-general').filter({ hasText: /credenciales|cuenta/i }).waitFor();
  await p.getByLabel('Contraseña').fill('una-clave-larga-123');
  await p.getByRole('button', { name: 'Ingresar' }).click();
  await p.waitForURL(/\/perfil\.html$/);
  ok(true, 'la contraseña incorrecta muestra el error de la API; la correcta vuelve a la página');

  // Un token vencido: la página protegida vuelve a pedir ingresar.
  await p.evaluate(() => localStorage.setItem('token', 'vencido'));
  await p.goto(base + '/perfil.html');
  await p.waitForURL(/\/ingresar\.html/);
  ok(await p.evaluate(() => localStorage.getItem('token')) === null, 'un token vencido se borra y pide ingresar');

  ok(errores.length === 0, 'sin errores de JavaScript: ' + errores.join(' | '));
  await b.close();
})().catch(async (e) => {
  if (p) console.error('en', p.url(), '\n', await p.locator('body').innerText().catch(() => ''), '\nerrores:', errores.join(' | '));
  console.error(e);
  process.exit(1);
});
