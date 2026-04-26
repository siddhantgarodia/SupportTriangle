# Partial Refunds

## Overview
Partial refunds apply when a customer is in the 14-30 day window, or when they are requesting a refund for only part of a charge (e.g., an incorrect add-on or overage fee). This document explains the calculation, process, and communication approach.

## Details

### When partial refunds apply
- Purchase was made 14-30 days ago (not within full refund window).
- Customer is on an annual plan and cancelling after the 14-day full refund window but within 30 days.
- Customer was overcharged for a specific line item (e.g., added 5 seats but only 3 were intended).
- Add-on or overage charge where only a portion was consumed.

### Calculating a partial refund — monthly plan
- Formula: (days remaining in billing cycle / total days in cycle) × monthly price
- Example: Pro plan ($99/mo), 10 days remaining in a 30-day cycle → (10/30) × $99 = $33.00 refund.

### Calculating a partial refund — annual plan
- Formula: (months fully unused / 12) × annual price
- Example: Annual Pro ($948/yr = $79/mo effective), cancelled after 3 months → 9 months × $79 = $711 refund.
- Note: months partially used are not counted — only full unused months qualify.

### Partial refund for add-ons
- API call packs and storage add-ons: refund the unused percentage.
- Example: Purchased a 100K API call pack for $50. Used 20K calls → 80% unused → $40 refund.
- If usage is above 50%, standard policy is to deny — these packs are meant to be consumed.

## Process Steps
1. Pull the invoice details and usage data.
2. Apply the appropriate formula.
3. Get manager approval for refunds over $200.
4. Process the partial refund in the billing system, specifying the amount.
5. Email the customer with a breakdown of the calculation.

## Edge Cases
- Currency fluctuations: if the customer paid in EUR and the original USD amount was $100, refund in the original currency at the original rate — do not use today's rate.
- Promotional discounts: if a promo reduced the price, calculate the partial refund based on the discounted price paid, not the list price.
- Multiple active subscriptions: calculate each subscription independently; do not cross-apply credits.
