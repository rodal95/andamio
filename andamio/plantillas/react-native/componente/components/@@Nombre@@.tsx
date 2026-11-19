import type { ReactNode } from 'react';
import { StyleSheet, View } from 'react-native';

export interface @@Nombre@@Props {
  /** Lo que va adentro del componente: <@@Nombre@@>contenido</@@Nombre@@> */
  children?: ReactNode;
}

export function @@Nombre@@({ children }: @@Nombre@@Props) {
  return <View style={styles.contenedor}>{children}</View>;
}

// Los estilos van al final, en un StyleSheet: React Native no usa CSS.
const styles = StyleSheet.create({
  contenedor: {
    padding: 16,
  },
});
