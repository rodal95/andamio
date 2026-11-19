import { useState } from 'react';

/**
 * use@@Nombre@@: agrupa estado y lógica para reutilizarlos en varios componentes.
 *
 * Uso:
 *   const { valor, setValor, reiniciar } = use@@Nombre@@(0);
 */
export function use@@Nombre@@<T>(valorInicial: T) {
  const [valor, setValor] = useState<T>(valorInicial);

  function reiniciar() {
    setValor(valorInicial);
  }

  return { valor, setValor, reiniciar };
}
