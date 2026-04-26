# Known Bugs & Active Incidents

## Overview
This document tracks currently known platform bugs, their impact, workarounds, and expected resolution dates. Updated weekly by the engineering team.

## Details

### Active Known Issues

#### BUG-1042: Dashboard chart flickers on Safari 17+
- **Impact**: Low — cosmetic only. Charts briefly flash white on Safari 17+ macOS Sonoma.
- **Workaround**: Use Chrome or Firefox. Or disable hardware acceleration in Safari → Preferences → Advanced.
- **ETA**: Fix in release v3.4.2, estimated next Tuesday.

#### BUG-1088: CSV export truncates rows at 50,000
- **Impact**: Medium — customers with large datasets missing rows in exports.
- **Workaround**: Use the API pagination endpoint to export in batches: `GET /v2/export?page=1&limit=10000`.
- **ETA**: Fix in release v3.5.0, estimated 2 weeks.

#### BUG-1101: Webhook events delayed during peak hours (9am-11am UTC)
- **Impact**: Medium — webhook delivery latency up to 8 minutes between 9-11am UTC.
- **Workaround**: If real-time delivery is critical, poll the API as a fallback during those hours.
- **ETA**: Infrastructure scaling in progress; fix expected this week.

#### BUG-1115: Password reset email not sent for SSO-provisioned accounts
- **Impact**: High — affects customers whose accounts were created via SSO who try to set a password.
- **Workaround**: Admin can manually set a temporary password in Settings → Users → [User] → Reset Password.
- **ETA**: Hotfix deployed to production, monitoring.

### Recently Resolved Bugs

#### BUG-1067: Two-factor authentication loop on mobile browsers — RESOLVED v3.3.8
- **Resolution**: Fixed by updating session token handling on mobile Safari.

#### BUG-1079: API 500 error on POST /v2/comments with emoji in body — RESOLVED v3.4.0
- **Resolution**: Updated text encoding to handle full Unicode range.

## Edge Cases
- If a customer reports a bug not listed here, collect: browser + version, OS, steps to reproduce, and the `X-Request-ID` from the failing API call.
- Bugs affecting Enterprise customers are prioritized — escalate immediately.
