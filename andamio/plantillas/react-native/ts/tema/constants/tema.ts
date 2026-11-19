import { useColorScheme } from 'react-native';

/**
 * Tema de la app (lo generó: python -m andamio nuevo tema @@nombre@@ --modo @@modo@@).
 * React Native no usa CSS: los colores se usan en los StyleSheet o en style={...}.
 * Para cambiarlo: borrá este archivo y generalo de nuevo con otro color o modo.
 */
export const COLORES = {
  claro: {
    @@colores_claro@@
  },
  oscuro: {
    @@colores_oscuro@@
  },
};

export type Colores = typeof COLORES.claro;

/** auto sigue al celular (claro u oscuro); claro u oscuro lo fijan. */
const MODO = '@@modo@@' as 'auto' | 'claro' | 'oscuro';

export const RADIO = 10;
export const ESPACIO = 16;

/**
 * Los colores del modo actual. Uso, dentro de un componente:
 *   const tema = useTema();
 *   <View style={[estilos.tarjeta, { backgroundColor: tema.superficie }]}>
 */
export function useTema(): Colores & { modo: 'claro' | 'oscuro'; radio: number; espacio: number } {
  const sistema = useColorScheme();
  const modo = MODO === 'auto' ? (sistema === 'dark' ? 'oscuro' : 'claro') : MODO;
  return { ...COLORES[modo], modo, radio: RADIO, espacio: ESPACIO };
}
