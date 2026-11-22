import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// guía: Dónde queda guardado el token entre una vez y otra que se abre la app. En el celular,
// guía: SecureStore lo guarda cifrado (AsyncStorage no lo cifra); en la web no existe, así
// guía: que se usa localStorage.

const CLAVE = 'token';

/** @returns {Promise<string | null>} */
export async function leerTokenGuardado() {
  if (Platform.OS === 'web') return localStorage.getItem(CLAVE);
  return SecureStore.getItemAsync(CLAVE);
}

/** @param {string | null} token */
export async function guardarToken(token) {
  if (Platform.OS === 'web') {
    if (token) localStorage.setItem(CLAVE, token);
    else localStorage.removeItem(CLAVE);
  } else if (token) {
    await SecureStore.setItemAsync(CLAVE, token);
  } else {
    await SecureStore.deleteItemAsync(CLAVE);
  }
}
