# Database Changes Documentation

This document records the changes made to the database schema for the Everesting CMS.

## 1. New Field: `tagline` in `challenges` Table

A new column `tagline` has been added to the `challenges` table to provide a short, catchy description for each challenge.

- **Column Name:** `tagline`
- **Data Type:** `VARCHAR` (String in SQLAlchemy)
- **Purpose:** To store a brief summary or slogan for the challenge that appears below the title.
- **Implementation:** Added to `models.py` and applied to the database via `ALTER TABLE challenges ADD COLUMN tagline VARCHAR;`.

## 2. Header Image Storage Improvements

The `foto` column in the `challenges` table is now used to store URLs of header images, which can be either external links or images uploaded directly through the CMS.

- **Column Name:** `foto` (existing)
- **Storage Strategy:** 
    - When a user uploads an image file (JPG, PNG, WebP) through the CMS, the file is uploaded to a Supabase Storage bucket named `challenge_headers`.
    - The public URL of the uploaded file is then stored in the `foto` column.
    - Alternatively, users can still provide a direct external URL which will also be stored in the same column.
- **Requirements:**
    - The Supabase project must have a storage bucket named `challenge_headers` with appropriate public access policies.
    - The CMS requires `SUPABASE_URL` and `SUPABASE_SECRET` (or `SUPABASE_ANON_PUBLIC`) to be configured in the `.env` file.
