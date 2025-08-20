# Email Verification and Password Reset API Documentation

## Overview

The DisplayAds API now includes comprehensive email verification and password reset functionality to enhance security and user experience.

## New Features

### 1. Email Verification on Registration
- All new users must verify their email address before they can log in
- Users receive a professional HTML email with a verification link
- Email verification tokens expire after 24 hours for security

### 2. Password Reset Functionality  
- Users can request a password reset via email
- Secure tokens are generated and sent via email
- Password reset tokens expire after 1 hour for security

## API Endpoints

### Registration (Modified)
```bash
POST /api/v1/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe", 
  "account_type": "personal"
}
```

**Response (Changed):**
```json
{
  "message": "Registration successful! Please check your email to verify your account before logging in.",
  "email": "user@example.com",
  "verification_required": true
}
```

### Email Verification
```bash
POST /api/v1/auth/verify-email/
Content-Type: application/json

{
  "token": "verification_token_from_email"
}
```

**Response:**
```json
{
  "message": "Email verified successfully. Your account is now active.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true
  }
}
```

### Resend Verification Email
```bash
POST /api/v1/auth/resend-verification/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Password Reset Request
```bash
POST /api/v1/auth/password-reset-request/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If an account with that email exists, we have sent a password reset link."
}
```

### Password Reset Confirmation
```bash
POST /api/v1/auth/password-reset-confirm/
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "newSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully. You can now log in with your new password."
}
```

### Login (Modified Behavior)
```bash
POST /api/v1/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response for Unverified Users:**
```json
{
  "detail": "Please verify your email address before logging in.",
  "email_verification_required": true,
  "email": "user@example.com"
}
```

## User Flow Examples

### Complete Registration Flow
1. User registers via `POST /api/v1/register/`
2. User receives verification email
3. User clicks verification link or uses token with `POST /api/v1/auth/verify-email/`
4. User can now login via `POST /api/v1/login/`

### Password Reset Flow
1. User requests reset via `POST /api/v1/auth/password-reset-request/`
2. User receives password reset email (if account exists)
3. User clicks reset link or uses token with `POST /api/v1/auth/password-reset-confirm/`
4. User can login with new password

## Security Features

- **Token Expiration**: Email verification tokens expire in 24 hours, password reset tokens in 1 hour
- **Secure Token Generation**: Uses cryptographically secure random tokens
- **Privacy Protection**: Password reset doesn't reveal if email exists
- **Token Invalidation**: Old tokens are invalidated when new ones are generated
- **Account Protection**: Inactive users cannot login until verified

## Email Configuration

### Development
- Emails are printed to console for development/testing
- No SMTP configuration required

### Production
Update `settings.py` email configuration:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # your SMTP provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Frontend Integration

### Registration Page Changes
- Remove immediate login after registration
- Show message about email verification requirement
- Provide link to resend verification if needed

### Login Page Changes  
- Handle `email_verification_required` response
- Show verification message with option to resend email
- Provide "Forgot Password" link

### New Pages Needed
- Email verification page (handles token from email links)
- Password reset request page
- Password reset confirmation page

## Error Handling

### Common Error Responses
```json
// Invalid/expired token
{
  "token": ["Token is invalid or expired."]
}

// Weak password
{
  "new_password": ["Password must be at least 6 characters long."]
}

// Already verified user
{
  "email": ["User account is already verified."]
}
```

## Testing

Run the comprehensive test suite:
```bash
python manage.py test test_email_auth
```

All 15 tests cover:
- User registration with email verification
- Email verification process
- Password reset functionality  
- Token expiration and security
- Complete user flows
- Error conditions

## Migration Notes

### Database Changes
- New tables: `EmailVerificationTokens`, `PasswordResetTokens`
- Migration applied: `0013_emailverificationtoken_passwordresettoken`

### Backward Compatibility
- Existing users remain active and can login normally
- New registration flow only affects new users
- All existing API endpoints unchanged except registration response format

This implementation provides a secure, user-friendly authentication system that follows modern security best practices while maintaining a smooth user experience.