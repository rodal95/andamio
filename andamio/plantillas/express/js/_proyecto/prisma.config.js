// Configuración de Prisma: la usan los comandos "npx prisma ...".
import { defineConfig } from 'prisma/config';

try {
  process.loadEnvFile(); // lee DATABASE_URL del archivo .env
} catch {
  // Sin .env: se usa la base por defecto (datos.db).
}

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: { path: 'prisma/migrations' },
  datasource: { url: process.env.DATABASE_URL ?? 'file:./datos.db' },
});
