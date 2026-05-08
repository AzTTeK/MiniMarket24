import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://tcipntcugipkxguxnodr.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjaXBudGN1Z2lwa3hndXhub2RyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNzM1NDAsImV4cCI6MjA5Mzg0OTU0MH0.66DK6hs1f_2Wuje-pcqpCvIGDIeHajSzUDuXuEXF8zM';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
