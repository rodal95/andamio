/**
 * Conexión a la base de datos con Prisma (SQLite).
 *
 * Prisma genera el cliente a partir de prisma/schema.prisma, con una propiedad por
 * tabla: prisma.producto.findMany(), prisma.producto.create({ data }), ...
 * (npm install, npm run dev y npm test lo generan solos; a mano: npx prisma generate).
 */
import { PrismaBetterSqlite3 } from '@prisma/adapter-better-sqlite3';
import { PrismaClient } from '@/generated/prisma/client';

function conectar() {
  return new PrismaClient({ adapter: new PrismaBetterSqlite3({ url: process.env.DATABASE_URL || 'file:./datos.db' }) });
}

// npm run dev recarga el código con cada cambio: se guarda la conexión en globalThis
// para no abrir una nueva cada vez.
const global = globalThis as unknown as { prisma?: ReturnType<typeof conectar> };
export const prisma = global.prisma ?? conectar();
if (process.env.NODE_ENV !== 'production') global.prisma = prisma;
