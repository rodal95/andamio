import { FormularioRegistro } from './FormularioRegistro';

interface Props {
  searchParams: Promise<{ desde?: string | string[] }>;
}

/** Crear una cuenta: la ruta /registro. ?desde= es la página a la que vuelve después. */
export default async function RegistroPage({ searchParams }: Props) {
  const { desde } = await searchParams;
  return <FormularioRegistro desde={desde} />;
}
