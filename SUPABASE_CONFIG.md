# Supabase Configuration Guide for HadithGPT

## Email Verification Setup

To ensure email verification works properly, you need to configure your Supabase project:

### 1. Disable Auto-Confirm (IMPORTANT!)

1. Go to your Supabase Dashboard
2. Navigate to **Authentication** > **Settings** > **Email Auth**
3. **DISABLE** "Enable email confirmations" if you want auto-confirm OFF
4. **OR** keep it enabled and configure email templates properly

### 2. Configure Email Templates

1. Go to **Authentication** > **Email Templates**
2. Update the following templates:

#### Confirm Signup Template:
```html
<h2>Confirm your signup for HadithGPT</h2>
<p>Follow this link to confirm your account:</p>
<p><a href="{{ .ConfirmationURL }}">Confirm your email</a></p>
<p>Or copy and paste this link: {{ .ConfirmationURL }}</p>
```

#### Reset Password Template:
```html
<h2>Reset your password for HadithGPT</h2>
<p>Follow this link to reset your password:</p>
<p><a href="{{ .ConfirmationURL }}">Reset your password</a></p>
<p>Or copy and paste this link: {{ .ConfirmationURL }}</p>
<p>If you didn't request this, you can safely ignore this email.</p>
```

### 3. Configure Redirect URLs

1. Go to **Authentication** > **URL Configuration**
2. Add your site URL to **Site URL**: `https://your-domain.com`
3. Add redirect URLs to **Redirect URLs**:
   - `http://localhost:3000/chat` (for development)
   - `https://your-domain.com/chat` (for production)
   - `http://localhost:3000/auth/reset-password`
   - `https://your-domain.com/auth/reset-password`

### 4. SMTP Settings (Email Provider)

#### Option 1: Use Supabase's Built-in Email (Limited)
- Works out of the box but has limits
- Not recommended for production

#### Option 2: Configure Custom SMTP (Recommended)
1. Go to **Project Settings** > **Auth** > **SMTP Settings**
2. Enable "Enable Custom SMTP"
3. Configure your email provider (Gmail, SendGrid, Mailgun, etc.):
   - **Host**: smtp.gmail.com (or your provider)
   - **Port**: 587 (TLS) or 465 (SSL)
   - **Username**: your-email@gmail.com
   - **Password**: your-app-password
   - **Sender email**: noreply@your-domain.com
   - **Sender name**: HadithGPT

#### Gmail Setup:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in SMTP settings

### 5. Email Confirmation Settings

In **Authentication** > **Settings**:

- **Email Confirmations**: Enable this
- **Secure email change**: Enable (requires re-verification on email change)
- **Double confirm email changes**: Enable (extra security)

### 6. Password Requirements

Configure minimum password requirements:
- **Minimum password length**: 6 characters (or higher for better security)

## Frontend Environment Variables

Make sure you have these in your `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your-project-url.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Testing the Auth Flow

### Test Email Verification:
1. Sign up with a new account
2. Check the email inbox (and spam folder)
3. Click the verification link
4. Should redirect to `/chat`

### Test Password Reset:
1. Go to `/auth/forgot-password`
2. Enter your email
3. Check email for reset link
4. Click link and set new password
5. Should redirect to `/chat`

### Test Login:
1. Go to `/auth/login`
2. Enter verified email and password
3. Should redirect to `/chat`

## Common Issues

### Email Not Sending:
- Check SMTP configuration
- Verify sender email is verified with your SMTP provider
- Check Supabase logs in Dashboard > Logs

### Email Going to Spam:
- Configure SPF, DKIM, and DMARC records for your domain
- Use a custom domain email instead of Gmail
- Use a transactional email service (SendGrid, Postmark, etc.)

### Auto-Confirm Still Happening:
- Make sure "Enable email confirmations" is checked
- Clear browser cache and try again
- Check if you're in development mode (some setups auto-confirm in dev)

### Password Autofill Issues:
- The `autoComplete` attributes are now properly set
- `email` fields use `autoComplete="email"`
- Login password uses `autoComplete="current-password"`
- Signup/reset passwords use `autoComplete="new-password"`

## Database Schema

Make sure you've run the `database/schema.sql` file in your Supabase SQL Editor to set up:
- `user_profiles` table with RLS policies
- `conversations` table for message history
- `messages` table for storing chat messages
- Automatic profile creation trigger on user signup

## Security Best Practices

1. ✅ Row Level Security (RLS) is enabled on all tables
2. ✅ Users can only access their own data
3. ✅ Email verification is enforced
4. ✅ Password reset requires email confirmation
5. ✅ Secure password requirements
6. ✅ Auto-logout on signout
7. ✅ Proper autocomplete attributes to prevent password managers from suggesting wrong passwords

## Next Steps

After configuring Supabase:
1. Test the complete auth flow
2. Monitor auth logs in Supabase Dashboard
3. Set up monitoring/alerting for auth failures
4. Configure rate limiting if needed
5. Implement conversation history saving (coming next)
