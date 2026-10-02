# Cultural objects: presentation metadata, attribution and rights

Source basis: IIIF Presentation API 3.0.

## Reusable reference

IIIF Presentation API 3.0 models a digital cultural object separately from the UI that displays it. A Manifest typically represents one object and may carry human-readable descriptive information plus rights/linking information and one or more Canvases representing views or time-based parts of the object.

Useful presentation fields have distinct roles:

```text
label
    human-readable name/title

summary
    short descriptive text

metadata
    ordered human-readable label/value context

requiredStatement
    publisher-defined statement that clients must make available/render
    commonly used for attribution/ownership acknowledgements

rights
    URI identifying an applicable license or rights statement

provider
    structured organization/person that provided the resource
```

Do not collapse creator/context, required attribution, rights status and provider identity into one decorative caption when the underlying collection distinguishes them. A cultural-object detail experience can preserve these meanings while still using its own visual hierarchy.

## Scope boundary

This record does not require a project to implement IIIF. It is a reference model for cultural-object presentation and provenance. Project truth must determine whether actual source data exposes these fields and what rights statements must be shown.

## Why this belongs in Knowledge OS

IIIF defines reusable cultural-collection concepts and semantics. Visual composition, art direction, asset choice and responsive media behavior remain owned by routed design/media skills.
