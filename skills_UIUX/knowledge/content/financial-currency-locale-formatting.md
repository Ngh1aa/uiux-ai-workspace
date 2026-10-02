# Financial amounts: locale- and currency-aware formatting

Source basis: Unicode CLDR / UTS #35 Part 3 — Numbers, stable released specification 48.2.

## Reusable reference

Currency and number presentation is locale data, not a universal punctuation template. CLDR separates number/currency patterns from the locale-specific symbols that replace their placeholders. Decimal/grouping separators, currency-symbol position and negative/accounting forms can vary by locale. Currency display may use a localized symbol or an international currency code depending on the application and locale context.

For financial-product interfaces, treat an amount as at least:

```text
numeric value + currency + locale/display context
```

Do not encode assumptions such as “comma always means thousands”, “period always means decimals”, “currency symbol always precedes the amount”, or “$ is unambiguous”. Use locale/currency-aware formatting data or APIs. Multi-currency interfaces need the currency identity carried explicitly with the value rather than inferred from punctuation or a symbol alone.

## Product application guidance

Keep one shared amount-formatting boundary for equivalent money surfaces instead of allowing cards, tables and transaction rows to invent their own punctuation or symbol rules. The formatter should receive the numeric value and currency explicitly, then use the product's resolved display locale when one exists. If product truth does not define a locale-resolution rule, require an explicit project fallback rather than silently relying on browser-default punctuation.

A practical QA matrix for any supported locale/currency set should cover at least:

```text
positive amount
zero amount
negative amount
large grouped amount
representative decimal amount
non-default currency
same-symbol currency ambiguity when applicable
```

Verify that the same value/currency pair renders consistently across dashboard totals, transaction rows and other equivalent surfaces. Where a localized symbol would be ambiguous in the actual product context, use a project-approved disambiguation treatment such as an explicit currency code rather than guessing from the symbol alone.

These checks are presentation checks only. They must not silently redefine rounding, accounting, tax, exchange-rate or supported-locale policy.

## Scope boundary

This record is formatting reference and implementation/QA guidance only. It does not define product pricing, accounting rules, exchange rates, rounding policy, tax treatment or regulatory requirements. Project truth must determine which locale/currency combinations are actually supported and what fallback locale policy, if any, the product uses.

## Why this belongs in Knowledge OS

The locale/currency model and its direct presentation implications are stable reusable reference context that can inform implementation and QA. The broader execution workflow, code ownership, product-policy decisions and release approval remain owned by routed skills, project code and human authority.
