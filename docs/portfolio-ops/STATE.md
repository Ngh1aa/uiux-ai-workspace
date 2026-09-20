# STATE.md

Cập nhật: 2026-09-21 | Trạng thái tổng: ĐANG NÂNG CẤP

| Thứ tự | Project | Tầng | Giai đoạn hiện tại | Bước tiếp theo | PR | Hướng | Ước lượng còn lại |
|---|---|---|---|---|---|---|---|
| 1 | Lumen | A | D | đề xuất 2–3 direction, AGENT-SELECTED rồi A1 | — | CHƯA CÓ | ~3 đêm INFERRED |
| 2 | Nova | A | queued | D | — | CHƯA CÓ | ~3 đêm INFERRED |
| 3 | Sentry | A | queued | D | — | CHƯA CÓ | ~3 đêm INFERRED |
| 4 | LuxRoom | A | queued | D | — | CHƯA CÓ | ~3 đêm INFERRED |
| 5 | Access | A | queued | D | — | CHƯA CÓ | ~3 đêm INFERRED |
| 6 | Atelier | B | queued | D/B1 | — | CHƯA CÓ | ~1 đêm INFERRED |
| 7 | Flux | B | queued | D/B1 | — | CHƯA CÓ | ~1 đêm INFERRED |
| 8 | CENNEXT | B | queued | map repo → D/B1 | — | CHƯA CÓ | ~1 đêm + mapping |
| 9 | VAS Education | B | queued | map repo → D/B1 | — | CHƯA CÓ | ~1 đêm + mapping |
| 10 | Portfolio site | PF | waiting | sau A/B đủ evidence | — | n/a | INFERRED |

## SCHEDULE
P0 inventory → Lumen D/A1/A2/A3 → Nova → Sentry → LuxRoom → Access → Tier B → PF.

Thứ tự có thể đổi khi OWNER ghi FEEDBACK hoặc khi evidence cho thấy một gap quan trọng hơn.

## Đang chờ OWNER
- Review tier proposal A/B/C; không bắt buộc để AUTO_WITH_REVIEW tiếp tục.
- Khi thấy direction AGENT-SELECTED: xác nhận hoặc yêu cầu đổi.
- Không merge PR chỉ vì CI xanh; dùng demo/evidence/reviewer verdict.

## Ghi chú kỹ thuật cho đêm sau
- `uiux-ai-workspace` là control plane; target implementation ở repo thật.
- Standalone `showcase/` đã removed, không tái tạo.
- Hai Draft PR legacy #30/#31 không phải lifecycle branch mới; tránh chồng thay đổi.
