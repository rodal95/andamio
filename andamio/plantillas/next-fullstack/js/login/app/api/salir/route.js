// guía: Salir (POST /api/salir/): borra la cookie de la sesión. La página no la puede borrar
// guía: sola, porque es httpOnly (su JavaScript no la ve).
import { cookieBorrada } from '@/lib/tokens';

export async function POST() {
  return new Response(null, { status: 204, headers: { 'Set-Cookie': cookieBorrada() } });
}
