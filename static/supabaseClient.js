
const { createClient } = window.supabase;

const supabaseUrl = 'https://nedhesgsfywpsbhrwnak.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lZGhlc2dzZnl3cHNiaHJ3bmFrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg5MTA1NDEsImV4cCI6MjA0NDQ4NjU0MX0.8KahX7pzXlZw0bVaX4nYeOTkJEYTIm71nyhv5z4Vs4c';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);