# Login Issues & Authentication Troubleshooting

## Overview
Login problems are the most common technical support request. This guide covers password resets, MFA failures, SSO errors, and account lockouts. Follow these steps in order before escalating.

## Details

### Standard password reset issues
- If a user cannot log in after a password reset, instruct them to clear browser cache or try incognito mode. Old session tokens can interfere with new credentials.
- Password reset emails occasionally land in spam or promotional folders. Ask the customer to check all folders and add our domain to their safe sender list.
- Password reset links expire after 24 hours. If expired, the customer must request a new reset.

### MFA (Multi-Factor Authentication) failures
- If MFA fails, the most common cause is a time drift on the customer's device. The TOTP algorithm requires device time to be within 30 seconds of server time.
- Fix: verify the time on their device is synced (Settings → Date & Time → Sync Now on mobile).
- If using an authenticator app, try generating the code in airplane mode to rule out network interference.
- Backup codes: if the customer can't access their authenticator, they should use a backup code generated during MFA setup. If backup codes are lost, identity verification is required before MFA reset.

### SSO (Single Sign-On) errors
- For SSO errors, check the SAML response in browser developer tools (Network tab → look for the SAML response POST).
- Common errors: attribute mapping mismatch (email claim not configured), certificate expiration, or ACS URL mismatch.
- The SAML configuration guide is available at Settings → Security → SSO Configuration.
- SSO issues on the IdP (Identity Provider) side must be resolved by the customer's IT team.

## Process Steps
1. Ask the customer what exact error message they see.
2. Have them try incognito/private browsing first.
3. If MFA issue: guide through time sync.
4. If SSO issue: request the SAML error XML.
5. If account locked: verify identity, then unlock in admin panel.

## Edge Cases
- Accounts are locked after 10 consecutive failed login attempts. Lock duration: 15 minutes (auto-unlock) or manual unlock by support.
- If a user's email was changed by an admin and they're trying the old email, the login will silently fail with "user not found."
- Safari browser users may encounter cookie issues with third-party SSO providers. Recommend Chrome or Firefox.
