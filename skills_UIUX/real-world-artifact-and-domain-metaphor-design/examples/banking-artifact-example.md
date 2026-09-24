# Example — Banking Artifact Research

## Problem
A banking homepage uses generic cards for `Mở tài khoản / Gửi tiết kiệm / Mở thẻ / Vay`, producing low domain distinctiveness.

## Candidate inventory

| Artifact | Familiarity | Task fit | Transfer |
|---|---:|---:|---|
| Bank card | High | High for card products | Form + information |
| Passbook/certificate | Medium | High for savings | Structural + information |
| Transaction receipt | High | Medium for transfers | Structural |
| Exchange board | High | High for rates | Structural + information |
| Branch signage | Medium | High for location/support | Cue + structural |

## Selected use — Card product

Artifact: current official bank card.

Problem solved: generic product tile does not communicate “this is a real card product” before reading.

Transfer:
- `L3 DIRECT_FORM` on desktop product showcase;
- physical card proportion;
- verified product art/network/tier;
- digital overlays only for comparison/CTA.

Do not copy:
- fake card number/name;
- decorative 3D plastic glare;
- unverified Visa/Mastercard/Napas mark;
- physical tiny typography if unreadable digitally.

Mobile adaptation:
- preserve card ratio for image/art;
- move product attributes/actions below as semantic content;
- avoid shrinking legal/product text into the card artwork.

## Selected use — Exchange rate

Artifact: exchange-rate board.

Transfer: `L2 STRUCTURAL`.

Use:
- tabular alignment;
- currency-first scanning;
- last-updated timestamp;
- selected/changed rate emphasis.

Do not copy:
- LED visual noise;
- terminal typography merely for nostalgia;
- yellow/red colors without semantic role.

## Resulting Design DNA

`banking objects + precise data hierarchy + official product truth + restrained brand cues`

This creates domain recognition without turning the website into a literal bank-counter simulation.
