-- Run this in your Supabase SQL Editor to fix the "Upload error: new row violates row-level security policy"

-- 1. Enable RLS on storage.objects (just in case)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 2. Allow users to upload files to their own folder in 'user-files' bucket
-- This policy ensures users can only upload to a folder that matches their User ID
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'user-files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 3. Allow users to update/delete their own files
CREATE POLICY "Allow authenticated update/delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'user-files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 4. Allow users to view their own files (already seems to work, but good to double check)
CREATE POLICY "Allow authenticated select"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'user-files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
