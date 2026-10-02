# Financial amounts: locale- and currency-aware formatting

Source basis: Unicode CLDR / UTS #35 Part 3 — Numbers, stable released specification 48.2.

## Reusable reference

Currency and number presentation is locale data, not a universal punctuation template. CLDR separates number/currency patterns from the locale-specific symbols that replace their placeholders. Decimal/grouping separators, currency-symbol position and negative/accounting forms can vary by locale. Currency display may use a localized symbol or an international currency code depending on the application and locale context.

For financial-product interfaces, treat an amount as at least:

```text
numeric value + currency + locale/display context
```

Do not encode assumptions such as “comma always means thousands”, “period always means decimals”, “currency symbol always precedes the amount”, or “$ is unambiguous”. Use locale/currency-aware formatting data or APIs and verify representative positive, negative and multi-currency examples.

## Scope boundary

This record is formatting reference only. It does not define product pricing, accounting rules, exchange rates, rounding policy, tax treatment or regulatory requirements. Project truth must determine which locale/currency combinations are actually supported.

## Why this belongs in Knowledge OS

The locale/currency model is stable reusable reference data that can inform implementation and QA. The execution workflow for implementing/testing financial UI remains owned by routed skills and project code.
