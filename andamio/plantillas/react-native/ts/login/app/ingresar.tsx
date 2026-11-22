import { @@router_ingresar@@ } from 'expo-router';
import { useState } from 'react';
import { Button, StyleSheet, Text, TextInput, View } from 'react-native';
import type { Credenciales } from '@/services/authService';
import { ErrorApi } from '@/services/http';
import { ingresar } from '@/sesion';

const VACIO: Credenciales = { username: '', password: '' };

// Opciones de la barra superior.
const opciones = { title: 'Ingresar' };

/** Pantalla para ingresar (ruta /ingresar). */
export default function IngresarPantalla() {
  // guía: Si llegó desde una pantalla protegida, después de ingresar vuelve ahí (?desde=).
  const { desde } = useLocalSearchParams<{ desde?: string }>();
  @@a_registro@@
  const [datos, setDatos] = useState<Credenciales>(VACIO);
  const [errores, setErrores] = useState<Record<string, string[]>>({});
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    setErrores({});
    setEnviando(true);
    try {
      await ingresar(datos);
      router.replace((desde || '/') as Href);
    } catch (e) {
      // guía: Usuario o contraseña incorrectos: la API responde 401 y lo explica (va en general).
      if (e instanceof ErrorApi && e.estado === 400) {
        setErrores(e.detalle as Record<string, string[]>);
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
      <Text style={styles.etiqueta}>Contraseña</Text>
      <TextInput
        accessibilityLabel="Contraseña"
        style={styles.entrada}
        secureTextEntry
        autoComplete="password"
        value={datos.password}
        onChangeText={(texto) => setDatos({ ...datos, password: texto })}
      />
      {errores.password && <Text style={styles.error}>{errores.password.join(' ')}</Text>}
      {errores.general && <Text style={styles.error}>{errores.general.join(' ')}</Text>}
      <View style={styles.boton}>
        <Button title={enviando ? 'Ingresando…' : 'Ingresar'} disabled={enviando} onPress={() => void enviar()} />
      </View>
      @@pie_ingresar@@
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
