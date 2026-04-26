# Chargeback Guide

## Overview
Chargebacks occur when a cardholder disputes a charge directly with their bank, bypassing the merchant. This guide covers chargeback prevention, the formal response process, and how to minimize financial exposure.

## Details

### What triggers a chargeback?
- Customer claims they didn't authorize the charge ("unauthorized transaction").
- Customer says they didn't receive the service or it wasn't as described.
- Friendly fraud: customer received service but disputes to get a free refund.
- Subscription not recognized: customer forgot they signed up or doesn't recognize the billing descriptor.

### Chargeback reason codes and our response strategy
| Reason Code | Meaning | Our Response |
|-------------|---------|--------------|
| 4853 | Service not as described | Show feature usage logs + ToS |
| 4854 | Cardholder dispute | Show sign-up records + usage |
| 4863 | Cardholder not recognized | Show IP login logs + confirmation email |
| 10.4 (Visa) | Consumer dispute | Show subscription agreement |
| UA02 (Amex) | Fraud | Escalate to fraud team |

### Evidence package contents
A strong chargeback response includes:
1. Signed terms of service or subscription agreement with timestamp.
2. Login history showing the customer used the service.
3. Email correspondence confirming the subscription.
4. Screenshot of the plan the customer was on.
5. Billing descriptor explanation (why it appears as it does on statements).
6. Any prior communication about the charge in question.

### Chargeback fee impact
- Each chargeback costs us a processing fee ($15-$50 depending on card network).
- High chargeback ratios (>1% of transactions) trigger warnings from card networks.
- Chronic chargeback customers should be flagged and may have future purchases blocked.

## Process Steps
1. Receive chargeback notification from payment processor.
2. Check if the customer has an open ticket — link them.
3. Compile evidence package within 24 hours.
4. Submit through payment processor portal (note: this is time-sensitive — deadlines vary).
5. Log the chargeback in the internal tracker for ratio monitoring.
6. Follow up with the customer if not already in contact.

## Edge Cases
- Pre-arbitration: if we win the initial dispute but the customer escalates to arbitration, costs increase significantly. Evaluate the chargeback amount vs. arbitration cost before fighting.
- Friendly fraud repeat offenders: block from future purchases after 2 confirmed friendly fraud incidents.
- Crypto payment chargebacks: technically impossible — escalate to legal if a customer claims one.
