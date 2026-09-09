from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DomainProfile:
    website_type: str
    vertical: str
    confidence: float
    evidence: tuple[str, ...]


class DomainInterpreter:
    """Infer a vertical below the broad website archetype.

    This layer intentionally stays separate from GoalInterpreter so existing
    orchestration contracts remain backward compatible while research gains
    category-specific intelligence.
    """

    VERTICALS = (
        ("luxury-fragrance", ("perfume", "fragrance", "parfum", "niche scent", "nước hoa", "nuoc hoa")),
        ("fashion", ("fashion", "clothing", "apparel", "streetwear", "quần áo", "thời trang")),
        ("beauty-skincare", ("beauty", "skincare", "cosmetics", "mỹ phẩm", "chăm sóc da")),
        ("electronics", ("electronics", "smartphone", "laptop", "computer store", "điện tử", "điện thoại", "máy tính")),
        ("furniture-home", ("furniture", "home decor", "interior", "nội thất", "trang trí nhà")),
        ("grocery-food", ("grocery", "food store", "supermarket", "thực phẩm", "siêu thị")),
        ("jewelry-luxury", ("jewelry", "jewellery", "watch store", "trang sức", "đồng hồ")),
        ("hotel-resort", ("hotel", "resort", "khách sạn", "khu nghỉ dưỡng")),
        ("restaurant", ("restaurant", "cafe", "dining", "nhà hàng", "quán cà phê")),
        ("higher-education", ("university", "college", "higher education", "đại học", "cao đẳng")),
        ("school-k12", ("k-12", "international school", "school", "trường quốc tế", "trường học")),
        ("fintech", ("fintech", "banking", "payments", "payment platform", "ngân hàng", "thanh toán")),
        ("developer-tools", ("developer tools", "devtool", "api platform", "developer platform")),
        ("news-publication", ("newspaper", "magazine", "publication", "báo điện tử", "tạp chí")),
    )

    @staticmethod
    def _contains(text: str, terms: tuple[str, ...]) -> bool:
        return any(term in text for term in terms)

    def interpret(self, goal: str, website_type: str) -> DomainProfile:
        text = re.sub(r"\s+", " ", goal.strip().lower())
        for vertical, terms in self.VERTICALS:
            if self._contains(text, terms):
                return DomainProfile(
                    website_type=website_type,
                    vertical=vertical,
                    confidence=0.92,
                    evidence=(f"website_type:{website_type}", f"vertical:{vertical}"),
                )

        return DomainProfile(
            website_type=website_type,
            vertical="generic",
            confidence=0.55,
            evidence=(f"website_type:{website_type}", "vertical:generic"),
        )
