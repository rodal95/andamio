import { Link, router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Button, StyleSheet, Text, TextInput, View } from 'react-native';
import { ErrorApi } from '@/services/http';
import { aDondeVolver, registrarse } from '@/sesion';

// guía: repetir no va a la API: es para controlar acá que la contraseña se escribió bien.
/** @type {import('@/services/authService').DatosRegistro & { repetir: string }} */
const VACIO = { username: '', email: '', password: '', repetir: '' };

// Opciones de la barra superior.
const opciones = { title: 'Crear una cuenta' };

/** Pantalla para crear una cuenta (ruta /registro). */
export default function RegistroPantalla() {
  const { desde } = useLocalSearchParams();
  // A /ingresar sin perder a dónde volver después.
  const aIngresar = { pathname: '/ingresar', params: { desde } };
  const [datos, setDatos] = useState(VACIO);
  const [errores, setErrores] = useState(/** @type {Record<string, string[]>} */ ({}));
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    // TODO(logica): más reglas antes de enviar (la API también valida: usuario repetido, contraseña corta o muy común).
    if (datos.password !== datos.repetir) {
      setErrores({ repetir: ['Las contraseñas no coinciden.'] });
      return;
    }
    setErrores({});
    setEnviando(true);
    try {
      // guía: registrarse() crea el usuario y también ingresa.
      await registrarse({ username: datos.username, email: datos.email, password: datos.password });
      router.replace(aDondeVolver(desde));
    } catch (e) {
      // guía: 400: la API dice qué está mal en cada campo (ej.: "Ya existe un usuario con este nombre.").
      if (e instanceof ErrorApi && e.estado === 400) {
        setErrores(/** @type {Record<string, string[]>} */ (e.detalle));
      } else {
        setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      }
    } finally {
      setEnviando(false);
    }
  }

  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      <Text style={styles.etiqueta}>Usuario</Text>
      <TextInput
        accessibilityLabel="Usuario"
        style={styles.entrada}
        autoCapitalize="none"
        autoComplete="username"
        value={datos.username}
        onChangeText={(texto) => setDatos({ ...datos, username: texto })}
      />
      {errores.username && <Text style={styles.error}>{errores.username.join(' ')}</Text>}
      <Text style={styles.etiqueta}>Email</Text>
      <TextInput
        accessibilityLabel="Email"
        style={styles.entrada}
        autoCapitalize="none"
        keyboardType="email-address"
        autoComplete="email"
        value={datos.email}
        onChangeText={(texto) => setDatos({ ...datos, email: texto })}
      />
      {errores.email && <Text style={styles.error}>{errores.email.join(' ')}</Text>}
      <Text style={styles.etiqueta}>Contraseña</Text>
      <TextInput
        accessibilityLabel="Contraseña"
        style={styles.entrada}
        secureTextEntry
        autoComplete="new-password"
        value={datos.password}
        onChangeText={(texto) => setDatos({ ...datos, password: texto })}
      />
      {errores.password && <Text style={styles.error}>{errores.password.join(' ')}</Text>}
      <Text style={styles.etiqueta}>Repetí la contraseña</Text>
      <TextInput
        accessibilityLabel="Repetí la contraseña"
        style={styles.entrada}
        secureTextEntry
        autoComplete="new-password"
        value={datos.repetir}
        onChangeText={(texto) => setDatos({ ...datos, repetir: texto })}
      />
      {errores.repetir && <Text style={styles.error}>{errores.repetir.join(' ')}</Text>}
      {errores.general && <Text style={styles.error}>{errores.general.join(' ')}</Text>}
      <View style={styles.boton}>
        <Button title={enviando ? 'Creando la cuenta…' : 'Crear la cuenta'} disabled={enviando} onPress={() => void enviar()} />
      </View>
      <Link href={aIngresar} style={styles.enlace}>
        ¿Ya tenés cuenta? Ingresá
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  contenedor: {
    flex: 1,
    padding: 16,
  },
  etiqueta: {
    fontWeight: 'bold',
    marginTop: 12,
  },
  entrada: {
    borderWidth: 1,
    borderColor: '#d0d5dd',
    borderRadius: 6,
    padding: 8,
    marginTop: 4,
  },
  error: {
    color: '#b91c1c',
    marginVertical: 8,
  },
  boton: {
    marginTop: 16,
  },
  enlace: {
    marginTop: 16,
    color: '#2563eb',
  },
});
