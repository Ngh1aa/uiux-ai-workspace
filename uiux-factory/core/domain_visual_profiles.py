from __future__ import annotations

from copy import deepcopy


_DEFAULT_THRESHOLDS = {
    "domain_fit_min": 65,
    "page_role_fit_min": 65,
    "decision_object_min": 55,
    "media_relevance_min": 55,
    "distinctiveness_min": 55,
    "generic_ai_block": 45,
    "cross_route_variety_min": 60,
    "brand_distinctiveness_min": 55,
}

_GENERIC = {
    "id": "generic-web",
    "decision_model": "Make the primary user task and evidence object visibly dominant.",
    "first_viewport_job": "Make the page purpose, primary decision object and next action legible before decorative storytelling.",
    "expectations": [
        "Different page roles should not collapse into one repeated hero/card/CTA template.",
        "Visual hierarchy must reflect the user's decision, not component-library convenience.",
        "Media, typography and structural devices should have a reason traceable to the brief.",
    ],
    "anti_patterns": [
        "interchangeable rounded-card grids with equal hierarchy",
        "template chrome repeated regardless of page role",
        "decorative stock media unrelated to the decision task",
        "generic AI polish that could be relabelled for another industry",
    ],
    "thresholds": _DEFAULT_THRESHOLDS,
}

_WEBSITE_PROFILES = {
    "ecommerce": {
        "id": "ecommerce",
        "decision_model": "Help people discover, compare, trust and choose products with category-appropriate evidence.",
        "first_viewport_job": "Expose the relevant product/category decision object and useful browsing or buying action quickly.",
        "expectations": [
            "Product/category evidence should dominate decorative containers.",
            "Listing, detail, cart and checkout roles must have materially different hierarchy.",
            "Product media and category-specific attributes should support comparison and confidence.",
        ],
        "anti_patterns": [
            "SaaS dashboard cards used as a universal product-listing grammar",
            "tiny product media subordinated to badges, borders and copy",
            "PDP rendered as another listing card instead of a buying/evaluation workspace",
        ],
        "thresholds": {
            "domain_fit_min": 68,
            "page_role_fit_min": 68,
            "decision_object_min": 62,
            "media_relevance_min": 60,
        },
    },
    "saas": {
        "id": "saas",
        "decision_model": "Explain the product outcome, show credible product proof and make key workflows understandable.",
        "first_viewport_job": "Make the product's value and credible product evidence understandable without generic growth-template filler.",
        "expectations": [
            "Product UI, workflow evidence or concrete outcomes should carry more weight than decorative gradients.",
            "Marketing, pricing, docs and application/dashboard roles should not share one identical composition.",
        ],
        "anti_patterns": [
            "feature-card soup with no product proof",
            "gradient blobs and metric tiles that do not explain the product",
        ],
        "thresholds": {
            "decision_object_min": 60,
            "media_relevance_min": 50,
            "distinctiveness_min": 58,
        },
    },
    "hospitality": {
        "id": "hospitality",
        "decision_model": "Help guests imagine the stay, understand the property and confidently choose or book.",
        "first_viewport_job": "Establish place/property character with credible imagery and a clear booking or exploration path.",
        "expectations": [
            "Property, room, food or destination imagery should be materially prominent when relevant.",
            "Room discovery, property story and booking flows need different visual jobs.",
        ],
        "anti_patterns": [
            "generic corporate cards replacing sense-of-place evidence",
            "stock travel imagery that is not credible for the property",
        ],
        "thresholds": {
            "media_relevance_min": 72,
            "decision_object_min": 62,
            "domain_fit_min": 70,
        },
    },
    "news": {
        "id": "news-media",
        "decision_model": "Help readers identify what is important, recent and relevant, then read with clear editorial hierarchy.",
        "first_viewport_job": "Establish editorial priority and recency/topic context without flattening every story into equal cards.",
        "expectations": [
            "Headline hierarchy and editorial priority should be visually legible.",
            "Home/category/article roles should have distinct reading and discovery structures.",
        ],
        "anti_patterns": [
            "equal-weight story card grids that erase editorial priority",
            "marketing-style CTA sections inserted into article reading flow",
        ],
        "thresholds": {
            "decision_object_min": 65,
            "page_role_fit_min": 70,
            "media_relevance_min": 50,
        },
    },
    "education": {
        "id": "education",
        "decision_model": "Help prospective learners understand programmes, fit, outcomes and admissions pathways.",
        "first_viewport_job": "Make the relevant programme/institution decision and next admissions or exploration step clear.",
        "expectations": [
            "Programme, outcome, cost/admissions and campus evidence should serve actual learner questions.",
            "Programme detail and admissions tasks should not look like generic campaign landing pages.",
        ],
        "anti_patterns": [
            "generic inspirational copy with no programme or admissions evidence",
            "identical promotional cards for unrelated student tasks",
        ],
        "thresholds": {
            "page_role_fit_min": 70,
            "decision_object_min": 60,
            "media_relevance_min": 45,
        },
    },
    "government": {
        "id": "government-service",
        "decision_model": "Help people complete public-service tasks with clarity, trust and low cognitive overhead.",
        "first_viewport_job": "Make the service/task, eligibility or next step obvious before institutional decoration.",
        "expectations": [
            "Task clarity and trustworthy service information outrank novelty or decorative media.",
            "Forms, guidance and service status need explicit state and progression hierarchy.",
        ],
        "anti_patterns": [
            "marketing hero sections obscuring the public task",
            "decorative card grids that fragment one service journey",
        ],
        "thresholds": {
            "page_role_fit_min": 72,
            "decision_object_min": 68,
            "media_relevance_min": 30,
            "distinctiveness_min": 40,
            "generic_ai_block": 55,
            "brand_distinctiveness_min": 35,
        },
    },
    "portfolio": {
        "id": "portfolio",
        "decision_model": "Make the creator's work, point of view and evidence of craft memorable and easy to inspect.",
        "first_viewport_job": "Show a distinctive work/identity signal rather than a generic agency introduction.",
        "expectations": [
            "Work/case-study evidence should be visually primary.",
            "Project detail pages should reveal process/outcome rather than repeat gallery cards.",
        ],
        "anti_patterns": [
            "generic creative-agency hero plus identical project cards",
            "decorative mockups with no legible work evidence",
        ],
        "thresholds": {
            "media_relevance_min": 70,
            "distinctiveness_min": 68,
            "brand_distinctiveness_min": 65,
        },
    },
}

_VERTICAL_OVERRIDES = {
    "luxury-fragrance": {
        "id": "luxury-fragrance",
        "decision_model": "Support a sensory, visual and trust-based fragrance decision: discover, understand scent character, sample/evaluate and purchase.",
        "first_viewport_job": "Make fragrance identity unmistakable and let perfume/product/media lead before generic ecommerce chrome.",
        "expectations": [
            "Fragrance/product imagery must be a primary decision object on discovery and listing routes, not a thumbnail inside card chrome.",
            "PDP hierarchy should foreground bottle/gallery, scent character/notes and buying or sampling confidence before long generic copy.",
            "Home/discovery should establish fragrance category and sensory world within the first viewport or immediate scroll cadence.",
            "Different routes should alternate editorial, discovery, catalogue and buying structures instead of repeating one card family.",
        ],
        "anti_patterns": [
            "rounded SaaS-card soup with small perfume imagery",
            "long text-first stretches with weak fragrance media",
            "generic stock lifestyle imagery that does not reinforce scent/product identity",
            "the same hero plus three-card grid grammar across home, PLP and PDP",
        ],
        "thresholds": {
            "domain_fit_min": 72,
            "page_role_fit_min": 70,
            "decision_object_min": 68,
            "media_relevance_min": 72,
            "distinctiveness_min": 65,
            "generic_ai_block": 35,
            "cross_route_variety_min": 68,
            "brand_distinctiveness_min": 62,
        },
    },
    "fashion": {
        "id": "fashion",
        "decision_model": "Help people judge silhouette, styling, material, colour and fit through strong garment/model evidence.",
        "first_viewport_job": "Make garment/look imagery dominant while keeping collection and shopping actions legible.",
        "expectations": [
            "Model/product imagery should carry the browse decision.",
            "PDP should support fit, material, colour and alternate-view confidence.",
        ],
        "anti_patterns": ["small garment thumbnails buried in generic cards"],
        "thresholds": {"media_relevance_min": 72, "decision_object_min": 68},
    },
    "electronics": {
        "id": "electronics",
        "decision_model": "Help people compare models, specifications, compatibility, performance and value.",
        "first_viewport_job": "Expose the product/model and comparison-relevant evidence instead of lifestyle decoration alone.",
        "expectations": [
            "Specification and comparison hierarchy may be denser than fashion/luxury retail and should remain scannable.",
            "Product media should support recognition without displacing critical compatibility/spec evidence.",
        ],
        "anti_patterns": ["editorial minimalism that hides comparison-critical specifications"],
        "thresholds": {"decision_object_min": 65, "media_relevance_min": 55},
    },
    "hotel-resort": {
        "id": "hotel-resort",
        "decision_model": "Help guests understand place, room experience, amenities and booking confidence.",
        "first_viewport_job": "Make the actual property/destination atmosphere credible and immediately explorable.",
        "expectations": ["Property and room imagery should be visually dominant on discovery/story routes."],
        "anti_patterns": ["generic luxury typography substituting for property evidence"],
        "thresholds": {"media_relevance_min": 78, "domain_fit_min": 72},
    },
    "developer-tools": {
        "id": "developer-tools",
        "decision_model": "Help technical users understand capability, integration path and credible product/code evidence.",
        "first_viewport_job": "Show what the tool does and enough authentic product/code proof to validate the claim.",
        "expectations": ["Code/product evidence should be real and task-relevant rather than decorative terminal chrome."],
        "anti_patterns": ["fake terminal panels and monospace labels used only as tech decoration"],
        "thresholds": {"decision_object_min": 62, "media_relevance_min": 45},
    },
}


def _merge_profile(base: dict, override: dict | None) -> dict:
    result = deepcopy(base)
    if not override:
        return result

    result["id"] = f"{base['id']}+{override['id']}"
    for key in ("decision_model", "first_viewport_job"):
        if override.get(key):
            result[key] = override[key]
    result["expectations"] = list(dict.fromkeys(base.get("expectations", []) + override.get("expectations", [])))
    result["anti_patterns"] = list(dict.fromkeys(base.get("anti_patterns", []) + override.get("anti_patterns", [])))
    result["thresholds"] = {**base.get("thresholds", {}), **override.get("thresholds", {})}
    return result


def resolve_visual_profile(website_type: str, vertical: str) -> dict:
    generic = deepcopy(_GENERIC)
    website = _WEBSITE_PROFILES.get((website_type or "").strip().lower())
    if website:
        generic = _merge_profile(generic, website)
    vertical_override = _VERTICAL_OVERRIDES.get((vertical or "").strip().lower())
    return _merge_profile(generic, vertical_override)
