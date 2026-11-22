import { FormularioIngreso } from './FormularioIngreso';

// guía: La página es del servidor: lee ?desde= de la dirección y se lo pasa al formulario,
// guía: que es del navegador ('use client') porque tiene estado y eventos.
interface Props {
  searchParams: Promise<{ desde?: string | string[] }>;
}

/** Ingresar: la ruta /ingresar. ?desde= es la página a la que vuelve después. */
export default async function IngresarPage({ searchParams }: Props) {
  const { desde } = await searchParams;
  return <FormularioIngreso desde={desde} />;
}
