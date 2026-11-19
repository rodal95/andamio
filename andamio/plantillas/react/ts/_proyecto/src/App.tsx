import { BrowserRouter, Link, Route, Routes } from 'react-router';
import styles from './App.module.css';
import { InicioPage } from './pages/InicioPage';
// --- andamio:imports (no borrar esta línea) ---

/**
 * Componente principal: el menú de navegación y las rutas, o sea, qué página se ve
 * en cada dirección (/, /productos, /productos/3...). andamio agrega acá las páginas
 * que generes.
 */
function App() {
  return (
    <BrowserRouter>
      <nav className={styles.menu}>
        <Link to="/">Inicio</Link>
        {/* --- andamio:enlaces (no borrar esta línea) --- */}
      </nav>
      <div className={styles.root}>
        <Routes>
          <Route path="/" element={<InicioPage />} />
          {/* --- andamio:rutas (no borrar esta línea) --- */}
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
