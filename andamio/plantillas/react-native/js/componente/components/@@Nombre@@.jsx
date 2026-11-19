import { StyleSheet, View } from 'react-native';

/**
 * @typedef {Object} @@Nombre@@Props
 * @property {import('react').ReactNode} [children] Lo que va adentro: <@@Nombre@@>contenido</@@Nombre@@>
 */

/** @param {@@Nombre@@Props} props */
export function @@Nombre@@({ children }) {
  return <View style={styles.contenedor}>{children}</View>;
}

// Los estilos van al final, en un StyleSheet: React Native no usa CSS.
const styles = StyleSheet.create({
  contenedor: {
    padding: 16,
  },
});
