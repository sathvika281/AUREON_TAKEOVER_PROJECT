import { createClient } from "@supabase/supabase-js";

import { env } from "../config/env";

/** The one client-side Supabase client — used only for Auth (sign up/in/
 * out, session persistence/restore). The frontend never queries Supabase
 * tables directly; all data access still flows through the FastAPI
 * backend's own service-role client. */
export const supabase = createClient(env.supabaseUrl, env.supabaseAnonKey);
