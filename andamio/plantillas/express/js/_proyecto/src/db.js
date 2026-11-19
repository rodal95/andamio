/**
 * Conexión a la base de datos con Prisma (SQLite).
 *
 * Prisma genera el cliente a partir de prisma/schema.prisma, con una propiedad por
 * tabla: prisma.producto.findMany(), prisma.producto.create({ data }), ...
 * (npm install, npm run dev y npm test lo generan solos; a mano: npx prisma generate).
 * El cliente generado está en TypeScript: tsx (npm run dev) lo ejecuta igual.
 */
import { PrismaBetterSqlite3 } from '@prisma/adapter-better-sqlite3';
import { DATABASE_URL } from './config.js';
import { PrismaClient } from './generated/prisma/client.ts';

export const prisma = new PrismaClient({ adapter: new PrismaBetterSqlite3({ url: DATABASE_URL }) });
