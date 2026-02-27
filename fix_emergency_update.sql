-- FIX: Add UPDATE policy for emergencies table
-- This allows the dashboard to update emergency status to "resolved"

-- Drop existing update policy if it exists
DROP POLICY IF EXISTS "Allow public updates" ON emergencies;

-- Create UPDATE policy for emergencies
CREATE POLICY "Allow public updates" ON emergencies
  FOR UPDATE
  USING (true);

-- Verify the policy was created
SELECT schemaname, tablename, policyname, permissive, roles, cmd 
FROM pg_policies 
WHERE tablename = 'emergencies';
