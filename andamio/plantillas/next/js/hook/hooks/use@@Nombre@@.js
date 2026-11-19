import { useState } from 'react';

/**
 * use@@Nombre@@: agrupa estado y lógica para reutilizarlos en varios componentes.
 *
 * Uso:
 *   const { valor, setValor, reiniciar } = use@@Nombre@@(0);
 *
 * @template T
 * @param {T} valorInicial
 */
export function use@@Nombre@@(valorInicial) {
  const [valor, setValor] = useState(valorInicial);

  function reiniciar() {
    setValor(valorInicial);
  }

  return { valor, setValor, reiniciar };
}
