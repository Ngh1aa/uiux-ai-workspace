---
name: omnichannel-experience-continuity
description: Ensures a user's journey remains coherent when moving between website, email, phone, messaging, sales/admissions staff, physical locations and follow-up systems. Use when digital actions lead to human or offline service delivery, lead handling, visits, applications, bookings or support.
---

# Omnichannel Experience Continuity

## Principle
The website is often one segment of a larger service. A successful screen that hands users into a broken offline process is not a successful journey.

## Workflow
1. Map all meaningful channels in the target journey.
2. Identify handoff moments: form → email, site → call, booking → venue, application → staff review, ecommerce → delivery/support.
3. Define what context must travel across the handoff.
4. Define what the user expects to happen next and when.
5. Design confirmation, status and recovery states.
6. Ensure users know how to get human help when self-service fails.
7. Check terminology, identity, data and promises stay consistent across channels.

## Handoff contract
For each handoff specify:
- trigger;
- user expectation;
- data/context transferred;
- owner/team/system receiving it;
- confirmation shown/sent;
- expected next step/timeframe if known;
- fallback/help path;
- privacy/consent implications.

## Common continuity checks
- Does a submitted form explain what happens next?
- Can staff see enough context to avoid making the user repeat everything?
- Does email/message language match the website?
- Does a booked physical visit include location/preparation details?
- Can users recover if the handoff fails?

## Required artifact
`docs/omnichannel-journey.md` for multi-channel services.

## Anti-patterns
- Treating `form submitted` as the end of the journey.
- Asking users to repeat data that should already be available.
- Different naming/instructions across web and staff channels.
- No owner or fallback for failed handoffs.
- Making promises on the website operational teams cannot keep.
