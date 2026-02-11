import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Force Node.js runtime (required for pg/Kysely database adapter)
export const runtime = 'nodejs';

export const { GET, POST } = toNextJsHandler(auth);
