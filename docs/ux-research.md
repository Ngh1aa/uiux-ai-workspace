# InstaCard — UX Research Document

## 1. Project Overview

**Product:** InstaCard  
**Category:** Digital Business Card Platform  
**Tagline:** "Your digital identity, one tap away"  
**Target launch:** Early Access (waitlist model)

### Product Description
InstaCard là platform cho phép người dùng tạo và chia sẻ digital business card trên nền tảng số. Ngoài ra, InstaCard cho phép chia sẻ link dẫn tới các kênh mạng xã hội và ứng dụng liên lạc như Facebook, Instagram, WhatsApp, LinkedIn...

---

## 2. Competitor Analysis

### Direct Competitors

| Competitor | Thế mạnh | Điểm yếu | InstaCard's Edge |
|:---|:---|:---|:---|
| **Linktree** | Bio-link ecosystem lớn, brand recognition cao | Không tập trung vào business card, thiếu tính năng contact management | InstaCard chuyên biệt cho business card + social linking |
| **Bizz Card** | Giao diện đơn giản, tích hợp CRM | UI cũ, yêu cầu download app, ít templates | No-download, modern UI, nhiều templates |
| **WorldCard Mobile** | OCR scan danh thiếp giấy mạnh | Tập trung scan giấy hơn tạo digital card, UX phức tạp | Digital-first approach, UX đơn giản hơn |
| **HiHello** | UX tốt, sharing nhanh | Premium pricing cao, limited free tier | Affordable, generous free tier |
| **Popl** | NFC hardware integration, event focus | Cần mua phần cứng, B2B focused | Browser-only, no hardware needed |

### Market Positioning

```
                  HIGH CUSTOMIZATION
                        │
          Popl ●        │        ● InstaCard
                        │          (Target)
    ────────────────────┼────────────────────
    COMPLEX             │            SIMPLE
                        │
          WorldCard ●   │   ● Linktree
                        │
          Bizz Card ●   │
                        │
                  LOW CUSTOMIZATION
```

InstaCard nhắm tới góc phần tư **High Customization + Simple UX** — cho phép tùy chỉnh sâu nhưng UX cực kỳ đơn giản.

---

## 3. Pain Points Analysis

### Pain Point 1: Danh thiếp giấy bị lãng quên
- **Data:** 88% danh thiếp giấy bị vứt trong 1 tuần (Forbes)
- **Impact:** Mất cơ hội kết nối kinh doanh
- **Solution:** Digital card lưu vĩnh viễn, có thể truy cập mọi lúc

### Pain Point 2: Sai sót khi nhập thông tin thủ công
- **Data:** 30% contacts nhập tay có ít nhất 1 lỗi (HubSpot Research)
- **Impact:** Gọi sai số, gửi email sai → mất lead
- **Solution:** Chia sẻ link — thông tin chính xác 100%

### Pain Point 3: Rào cản ngôn ngữ trong networking quốc tế
- **Scenario:** Bạn nhận danh thiếp tiếng Nhật nhưng không biết gõ kanji
- **Impact:** Không thể lưu đúng tên/địa chỉ → mất kết nối
- **Solution:** Multilingual support, lưu đúng ngôn ngữ gốc

### Pain Point 4: Chi phí in ấn liên tục
- **Data:** Trung bình ~$50-200/lần in 500 card, mỗi lần đổi thông tin phải in lại
- **Impact:** Tốn tiền + thời gian, đặc biệt với freelancer/startup
- **Solution:** Cập nhật real-time, $0 chi phí in

### Pain Point 5: Thông tin phân tán trên nhiều nền tảng
- **Scenario:** Đối tác phải tự tìm bạn trên LinkedIn, Instagram, WhatsApp...
- **Impact:** Friction cao → ít người thực sự kết nối
- **Solution:** 1 link duy nhất = tất cả channels

### Pain Point 6: Tác động môi trường
- **Data:** 7.2 tỷ danh thiếp/năm = 9 triệu cây bị chặt
- **Impact:** Lãng phí tài nguyên cho thứ 88% bị vứt
- **Solution:** 100% digital = 0 waste

---

## 4. Consumer Insights

### Insight #1: "Tôi muốn được nhớ đến, không chỉ được trao danh thiếp"

**Context:** Người dùng tham gia networking events muốn tạo ấn tượng lâu dài. Danh thiếp giấy kết thúc tại thời điểm trao đổi, nhưng digital card cho phép tiếp tục engagement thông qua social links.

**Implication cho design:** CTA "Get Early Access" phải truyền tải cảm giác "early adopter" và "professional edge" — không phải chỉ là tool, mà là competitive advantage.

### Insight #2: "Đừng bắt tôi download thêm app nào nữa"

**Context:** App fatigue là vấn đề thực tế — trung bình người dùng chỉ dùng 9 apps/ngày (App Annie). Yêu cầu download app để xem 1 danh thiếp = friction quá lớn.

**Implication cho design:** "No app download required" phải là benefit #1 được highlight — đây là USP lớn nhất so với Bizz Card và WorldCard.

### Insight #3: "Tôi là freelancer/solopreneur — tôi cần trông chuyên nghiệp với chi phí tối thiểu"

**Context:** 36% workforce là freelancer (Upwork Report). Họ cần business card đẹp nhưng không có budget thuê designer. InstaCard templates giải quyết nhu cầu này.

**Implication cho design:** Showcase templates trong App Preview section, dùng messaging "professional" thay vì "cheap/free".

---

## 5. Target Audience Segmentation

### Primary: Young Professionals (25-35)
- **Who:** Sales reps, BD managers, account executives
- **Behavior:** Attend 3-5 networking events/tháng
- **Need:** Trao đổi contact nhanh, sync với CRM
- **Motivation:** Efficiency, professional image

### Secondary: Freelancers & Solopreneurs (22-40)
- **Who:** Designers, developers, consultants, coaches
- **Behavior:** Networking online + offline, personal branding
- **Need:** Customizable card, multiple social links
- **Motivation:** Branding, affordability

### Tertiary: Students & Recent Graduates (20-25)
- **Who:** Sinh viên đi career fair, hackathon, internship
- **Behavior:** Lần đầu networking chuyên nghiệp
- **Need:** Trông chuyên nghiệp dù chưa có kinh nghiệm
- **Motivation:** Standing out, first impressions

---

## 6. Sitemap

```
Landing Page (Single Page Application)
├── Header
│   ├── Logo (InstaCard)
│   ├── Navigation (anchor links)
│   │   ├── Benefits
│   │   ├── How it Works
│   │   └── Preview
│   └── CTA: Get Early Access
│
├── Hero Banner
│   ├── Badge: "Now in Early Access"
│   ├── Title: "Say goodbye to business cards"
│   ├── Subtitle: "Effortless contact exchange"
│   ├── Description text
│   ├── Email Input + CTA Button
│   ├── Trust note: "Free forever. No credit card."
│   └── Visual: 3D Card Mockup
│
├── Social Proof Bar
│   ├── 10,000+ Professionals
│   ├── 50+ Countries
│   └── 99% Satisfaction
│
├── Benefits (6 cards)
│   ├── Simple — No app download
│   ├── Accurate — No typos/OCR errors
│   ├── Multilingual — Any language
│   ├── Integrated — Sync everywhere
│   ├── Green — Save 173 trees/day
│   └── Customized — Templates/custom design
│
├── How It Works (3 steps)
│   ├── Step 1: Create
│   ├── Step 2: Share
│   └── Step 3: Connect
│
├── App Preview
│   ├── Feature list
│   └── Phone mockup with app screenshot
│
└── Footer
    ├── CTA Section (Email + Button)
    ├── Footer Links
    │   ├── Product links
    │   └── Legal links
    ├── Social Media
    └── Copyright
```

---

## 7. User Flow

### Primary Flow: Email Signup

```
User Lands on Page
    │
    ├─── Reads Hero → Interested → Enters Email → Clicks CTA → ✅ Signed Up
    │
    └─── Not convinced yet → Scrolls Down
              │
              ├── Sees Social Proof (builds trust)
              │
              ├── Reads Benefits (solves objections)
              │
              ├── Sees How It Works (reduces friction)
              │
              ├── Views App Preview (visual proof)
              │
              └── Reaches Footer CTA → Enters Email → Clicks CTA → ✅ Signed Up
```

### Decision Points

| Point | User Question | Section Answers |
|:---|:---|:---|
| Hero | "What is this?" | Title + subtitle explain value |
| Social Proof | "Do others use it?" | Numbers + "trusted by" messaging |
| Benefits | "Why should I switch?" | 6 concrete benefits address objections |
| How It Works | "Is it complicated?" | 3 simple steps reduce friction |
| Preview | "Does it actually look good?" | Real app screenshots prove quality |
| Footer CTA | "OK, I'm in" | Final conversion opportunity |

---

## 8. Design Decisions & Rationale

### Color Choice: Sky Blue Gradient (#0EA5E9 → #6366F1)
- **Why:** Blue = trust, professionalism, technology. Gradient thêm tính hiện đại so với flat color. Phù hợp với brand identity hiện tại (theo app screenshots).

### Typography: Inter
- **Why:** Designed for screens, excellent readability, modern feel. Widely used by tech companies (GitHub, Figma). Weight range lớn cho phép tạo hierarchy rõ ràng.

### Single-page Landing Page vs Multi-page
- **Why single-page:** Landing page cho early access chỉ cần 1 conversion goal (email signup). Multi-page tạo drop-off. Single-page = message match rõ ràng, no navigation distraction.

### CTA Color: Gradient Blue
- **Why:** Von Restorff Effect — CTA nổi bật so với background trắng/xám. Gradient thêm visual interest so với flat button.

---

## 9. UX Laws Applied

| Law | Application |
|:---|:---|
| **Hick's Law** | Nav chỉ có 3 items + 1 CTA. Không quá tải lựa chọn. |
| **Fitts's Law** | CTA buttons lớn (48px height), spacing đủ rộng. Mobile touch targets ≥44px. |
| **Jakob's Law** | Logo trái, nav phải, CTA cuối nav — theo convention. |
| **Von Restorff Effect** | CTA gradient nổi bật trên nền trắng. Unique visual giữa các elements. |
| **Miller's Law** | Benefits = 6 items (trong 5-7 optimal). Steps = 3 items. |
| **Gestalt Proximity** | Benefits grouped 3×2 grid. Steps liên kết bằng connector arrows. |
| **Peak-End Rule** | Footer CTA section = "peak moment" cuối, thiết kế ấn tượng. |
| **Doherty Threshold** | Tất cả transitions < 400ms. Form feedback instant. |

---

*Document Version: 1.0*  
*Last Updated: September 2025*
