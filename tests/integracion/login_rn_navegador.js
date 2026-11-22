// Prueba del login de React Native (nuevo login) en su versión web (react-native-web,
// npx expo export --platform web) contra la API de Django, con una pantalla --protegido.
// La ejecuta tests/integracion/test_login_navegador.py:
//   node login_rn_navegador.js http://127.0.0.1:PUERTO
const { chromium } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('FALLÓ: ' + m); console.log('ok -', m); };
let p;
const errores = [];
(async () => {
  const b = await chromium.launch();
  p = await b.newPage();
  p.on('pageerror', (e) => errores.push(e.message));
  const base = process.argv[2];
  // El Stack deja montadas (ocultas) las pantallas anteriores: se usa la que se ve.
  const boton = (nombre) => p.getByRole('button', { name: nombre }).filter({ visible: true });
  const campo = (nombre, opciones) => p.getByLabel(nombre, opciones).filter({ visible: true });

  // La pantalla protegida, sin sesión: lleva a /ingresar (y después vuelve a /perfil).
  await p.goto(base + '/perfil');
  await p.waitForURL(/\/ingresar\?desde=%2Fperfil$/);
  await campo('Usuario').waitFor();
  ok(await p.getByText('Perfil', { exact: true }).filter({ visible: true }).count() === 0, 'sin sesión: /perfil lleva a /ingresar');

  // Crear una cuenta (primero con las contraseñas distintas) y volver a /perfil.
  await p.getByText('¿No tenés cuenta? Registrate').filter({ visible: true }).click();
  await p.waitForURL(/\/registro\?desde=%2Fperfil$/);
  await campo('Usuario').fill('ana');
  await campo('Email').fill('ana@ejemplo.com');
  await campo('Contraseña', { exact: true }).fill('una-clave-larga-123');
  await campo('Repetí la contraseña').fill('otra');
  await boton('Crear la cuenta').click();
  await p.getByText('Las contraseñas no coinciden.').filter({ visible: true }).waitFor();
  await campo('Repetí la contraseña').fill('una-clave-larga-123');
  await boton('Crear la cuenta').click();
  await p.waitForURL(/\/perfil$/);
  await boton('Salir (ana)').waitFor();
  ok(true, 'registrarse ingresa, vuelve a la pantalla protegida y la barra muestra Salir (ana)');

  // La sesión queda guardada: al recargar, sigue adentro.
  await p.reload();
  await boton('Salir (ana)').waitFor();
  ok(p.url().endsWith('/perfil'), 'al recargar, la sesión sigue (el token quedó guardado)');

  // Salir: a /, y la barra vuelve a Ingresar.
  await boton('Salir (ana)').click();
  await p.waitForURL(base + '/');
  await boton('Ingresar').waitFor();
  ok(true, 'salir');

  // Ingresar con la contraseña mal y bien (y volver a la pantalla con sus parámetros).
  await p.goto(base + '/perfil?pestana=datos');
  await p.waitForURL(/\/ingresar/);
  await campo('Usuario').fill('ana');
  await campo('Contraseña').fill('mal');
  await boton('Ingresar').last().click();
  await p.getByText(/credenciales/).filter({ visible: true }).waitFor();
  await campo('Contraseña').fill('una-clave-larga-123');
  await boton('Ingresar').last().click();
  await p.waitForURL(/\/perfil\?pestana=datos$/);
  ok(true, 'la contraseña incorrecta muestra el error de la API; la correcta vuelve a la pantalla');

  // Un token vencido: la pantalla protegida vuelve a pedir ingresar.
  await p.evaluate(() => localStorage.setItem('token', 'vencido'));
  await p.goto(base + '/perfil');
  await p.waitForURL(/\/ingresar/);
  ok(await p.evaluate(() => localStorage.getItem('token')) === null, 'un token vencido se borra y pide ingresar');

  // ?desde= con otro sitio: después de ingresar se queda en la app (no hay redirección abierta).
  await p.goto(base + '/ingresar?desde=' + encodeURIComponent('https://example.com/'));
  await campo('Usuario').fill('ana');
  await campo('Contraseña').fill('una-clave-larga-123');
  await boton('Ingresar').last().click();
  await p.waitForURL(base + '/');
  ok(true, '?desde= con otro sitio vuelve a /');

  ok(errores.length === 0, 'sin errores de JavaScript: ' + errores.join(' | '));
  await b.close();
})().catch(async (e) => {
  if (p) console.error('en', p.url(), '\n', await p.locator('body').innerText().catch(() => ''), '\nerrores:', errores.join(' | '));
  console.error(e);
  process.exit(1);
});
