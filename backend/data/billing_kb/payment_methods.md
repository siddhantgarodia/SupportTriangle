# Payment Methods

## Overview
We support multiple payment methods to accommodate global customers. This document describes accepted methods, how to update them, and how to handle payment failures.

## Details

### Accepted payment methods
- **Credit/Debit cards**: Visa, Mastercard, American Express, Discover. 3D Secure supported.
- **ACH bank transfer**: US bank accounts only. 3-5 business days processing time.
- **SEPA Direct Debit**: EU bank accounts. 2-3 business days processing time.
- **Wire transfer**: Available for annual plans above $5,000/year. Invoiced separately.
- **PayPal**: Available in 45+ countries. Currency is converted to USD at PayPal's rate.

### Updating payment method
1. Go to Settings → Billing → Payment Methods.
2. Click "Add Payment Method" and follow the prompts.
3. Set the new method as default.
4. The old method can be removed once the new one is verified.
5. Changes take effect on the next billing cycle.

### Payment failure handling
- When a payment fails, we attempt retry 3 times: 1 day, 3 days, and 7 days after the original due date.
- The customer receives an email notification after each failed attempt.
- If all 3 retries fail, the account is downgraded to a read-only state (data preserved, no new actions).
- Reactivation: update the payment method and pay the outstanding balance in the billing portal.

### Prepaid cards and virtual cards
- Prepaid cards are not supported due to recurring billing limitations.
- Virtual cards from corporate expense platforms (e.g., Brex, Ramp) are supported if they allow recurring charges.

## Edge Cases
- If a card is flagged as stolen/lost by the bank, the customer must add a new card — we cannot retry on a blocked card.
- Payment methods on free plans cannot be added until the customer starts a paid subscription.
- Multi-currency: invoices are always in USD unless the customer is on a EUR-denominated contract.
