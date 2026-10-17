const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });
global.WebSocket = require('ws');
const sb = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_PUBLISHABLE_KEY);

async function run() {
  const email = `test_${Date.now()}@example.com`;
  const { data: authData, error: authError } = await sb.auth.signUp({ email, password: 'password123', options: { data: { full_name: 'Test' } } });
  if (authError) { console.error('Auth Error:', authError); return; }
  console.log('User ID:', authData.user.id);
  
  const { data: insertData, error: insertError } = await sb.from('projects').insert([{
    user_id: authData.user.id,
    name: 'Test 1',
  }]).select().single();
  
  if (insertError) { console.error('Insert Error:', insertError); return; }
  console.log('Inserted Project:', insertData);
  
  const { data: fetchData, error: fetchError } = await sb.from('projects').select('*').eq('user_id', authData.user.id);
  if (fetchError) { console.error('Fetch Error:', fetchError); return; }
  console.log('Fetched Projects:', fetchData);
}
run();
