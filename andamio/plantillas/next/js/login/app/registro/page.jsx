import { FormularioRegistro } from './FormularioRegistro';

/** Crear una cuenta: la ruta /registro. ?desde= es la página a la que vuelve después.
 * @param {{ searchParams: Promise<{ desde?: string | string[] }> }} props
 */
export default async function RegistroPage({ searchParams }) {
  const { desde } = await searchParams;
  return <FormularioRegistro desde={desde} />;
}
