import type { ReactNode } from 'react';
import styles from './@@Nombre@@.module.css';

export interface @@Nombre@@Props {
  /** Lo que va adentro del componente: <@@Nombre@@>contenido</@@Nombre@@> */
  children?: ReactNode;
}

export function @@Nombre@@({ children }: @@Nombre@@Props) {
  return <div className={styles.root}>{children}</div>;
}
