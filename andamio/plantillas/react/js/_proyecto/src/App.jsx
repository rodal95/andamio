import { BrowserRouter, Route, Routes } from 'react-router';
import { Layout } from './components';
import { InicioPage } from './pages/InicioPage';
// --- andamio:imports (no borrar esta línea) ---

/**
 * Componente principal: las rutas, o sea, qué página se ve en cada dirección
 * (/, /productos, /productos/3...). andamio agrega acá las páginas que generes.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* guía: Las páginas de adentro se ven con el menú (Navbar) y el pie (Footer): ver components/Layout. */}
        <Route element={<Layout />}>
          <Route path="/" element={<InicioPage />} />
          {/* --- andamio:rutas (no borrar esta línea) --- */}
        </Route>
        {/* guía: Las páginas sin menú ni pie (ej.: /ingresar, si el login es obligatorio para toda la app). */}
        {/* --- andamio:rutas_sin_layout (no borrar esta línea) --- */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
