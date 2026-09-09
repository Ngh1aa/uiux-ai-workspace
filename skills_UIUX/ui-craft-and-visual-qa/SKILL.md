---
name: ui-craft-and-visual-qa
description: |
  Review và polish UI ở mức craft: hierarchy, spacing, alignment, density, typography,
  imagery, states, responsive consistency và visual regression. Dùng trước khi gọi giao diện
  hoàn tất hoặc khi UI “đúng chức năng nhưng chưa chuyên nghiệp / trông như AI template”.
---

# UI Craft & Visual QA

## Goal

Biến UI từ “đã code” thành **coherent, intentional, production-grade**.

## Non-negotiable evidence rule

Với substantial UI/redesign work, **source code + build success không phải visual QA**.

Muốn kết luận `PASS` phải có actual rendered evidence của implementation và phải **mở/inspect bằng mắt** evidence đó. Evidence phù hợp có thể là live/local browser, screenshots hoặc equivalent render capture.

Nếu không thể render/capture/inspect implementation:

- ghi `VISUAL QA: BLOCKED` hoặc `UNVERIFIED`;
- nêu blocker cụ thể;
- không gọi UI `finished`, `polished`, `visually verified` hoặc `production-grade`;
- không dùng static assertions/CSS grep thay cho nhìn giao diện thật.

## Mandatory elementary visual sanity gate

Trước khi chấm craft/aesthetic sâu hơn, chạy [Elementary Visual Sanity Gate](checklists/elementary-visual-sanity-gate.md) khi task là substantial visual work, multi-page/whole-site, production-candidate/release, hoặc remediation của một lỗi obvious mà QA trước đã bỏ lọt.

Các failure sau là **hard blockers** dù build/CI/screenshot generation xanh:

- important text chỉ nhìn thấy khi bôi đen/select;
- foreground và rendered surface gần như cùng màu (`1:1` hoặc visually equivalent);
- button/CTA label biến mất ở hover/focus/active/disabled;
- shared surface đổi light↔dark nhưng descendant foreground/link/icon/button không được audit lại;
- CSS intended color đúng nhưng computed color bị selector/cascade layer khác override;
- hero/feature media cắt mất face/head/focal subject một cách không có chủ đích.

Deep review có thể dùng representative routes, nhưng **shared-owner elementary sanity không được chỉ sample**. Nếu header/footer/nav/button token/theme/shared surface bị đổi, phải smoke/check mọi route/template mà owner đó render.

## Review order

Không bắt đầu bằng shadow/radius. Review từ macro đến micro:

1. Elementary visual sanity: visibility, state contrast, cascade/specificity, focal crop.
2. Page purpose và visual hierarchy.
3. Cross-page composition / template monotony.
4. Section rhythm và density.
5. Grid/alignment.
6. Typography/readability.
7. Components/states.
8. Imagery/icon consistency + native asset quality.
9. Text-on-image legibility.
10. Micro-details/motion.

## Mandatory cross-page review

Với multi-page website, capture representative **top-of-page screenshots side-by-side** trước khi soi micro-detail.

Review ít nhất các primary page roles khác nhau và hỏi:

- first visual anchor có phản ánh đúng page task không?
- hero/top-of-page có bị copy cùng shell rồi thay copy/image không?
- page nào cần map, floor plan, product object, evidence, form, data, timeline... nhưng lại bị ép thành image banner?
- hierarchy giữa các page có đủ khác để người dùng hiểu “mình đang ở page loại gì”, nhưng vẫn cùng brand system?
- navigation/tokens/signature motif tạo consistency hay toàn layout đang tạo monotony?

Với site có 5+ materially different primary page roles, nếu gần như toàn bộ top-of-page dùng một composition family mà không có documented rationale, mặc định là **P1 design-system/composition issue**.

## Anti-generic UI checks

Cảnh báo nếu xuất hiện hàng loạt pattern thiếu rationale:

- Mọi section đều là card bo tròn.
- Gradient/glass/shadow dùng khắp nơi.
- Mọi title đều centered.
- Icon nằm trong badge tròn chỉ để trang trí.
- Section lặp `heading + 3 cards` liên tục.
- Nhiều màu accent cạnh tranh.
- Hero quá nhiều label/badge/CTA.
- Nhiều primary page dùng cùng `copy + image` hero chỉ đổi text/asset.
- Domain-native decision objects bị đẩy xuống dưới để nhường hero cho ảnh trang trí.

Nếu brand yêu cầu minimal, editorial, institutional, luxury... phải để visual grammar phản ánh đúng personality, không dùng default SaaS template.

## 5-second first-impression test

Cho mỗi primary page screenshot, trong 5 giây phải trả lời được:

1. Đây là page về việc gì?
2. Thứ quan trọng nhất user nên nhìn thấy là gì?
3. Primary action là gì?
4. Visual này có thuộc brand/domain này không, hay có thể đổi logo cho project khác?

Nếu không trả lời được, chưa xuống micro-polish; quay lại hierarchy/composition owner.

## Spacing audit

- Kiểm vertical rhythm giữa section, heading, paragraph, controls.
- Chỉ dùng spacing scale; exception phải có lý do.
- Parent dùng `gap`; tránh margin ngẫu nhiên giữa siblings.
- Cùng một relationship phải có cùng khoảng cách.

## Typography audit

- H1/H2/H3 khác nhau đủ rõ nhưng không nhảy scale vô lý.
- Body line-height và line length dễ đọc.
- Button/nav text không quá nhỏ.
- Font weight không dùng thay cho hierarchy duy nhất.
- Vietnamese diacritics và font fallback phải render tốt nếu site tiếng Việt.
- Large display text phải được inspect tại narrow/mobile widths; `clamp()` tồn tại không chứng minh chữ không overlap/clip.

## Alignment audit

- Text, image, card, CTA bám cùng grid line.
- Optical alignment được phép nhưng phải có chủ đích.
- Không để container widths thay đổi tùy page vô lý.

## Color/contrast and brand-role audit

Không chỉ check palette tồn tại. Kiểm actual rendered states:

- logo trên mọi nav/background state;
- CTA text/icon trên default/hover/focus;
- active nav/link states;
- text trên image/gradient/overlay;
- muted/meta text readability;
- accent color có semantic/brand role hay bị rải ngẫu nhiên.

Một logo hoặc CTA biến mất vì white-on-white / low contrast là P0/P1 visual defect tùy mức ảnh hưởng và phải chặn handoff.

### Surface-pair integrity

`background/surface` và `foreground/content` là **một contract**, không phải hai chỉnh sửa độc lập.

Khi một shared surface đổi màu/theme:

- audit computed text/link/icon/divider/control colors trong cùng commit/change set;
- kiểm cascade layer và specificity thắng thật trong browser;
- không coi source declaration là evidence nếu computed style khác;
- nếu shared owner xuất hiện trên nhiều route, elementary visibility scan phải phủ mọi affected route/template.

Một fix đổi `background` nhưng không xét foreground descendants là incomplete và phải FAIL gate.

## Text-on-image legibility gate — hard gate

Text đặt trên photography/video/variable imagery phải được kiểm ở **actual crop hiện tại**, không dựa trên average image brightness hay một screenshot đẹp duy nhất.

Kiểm:

- vùng sáng nhất và tối nhất phía sau text;
- crop desktop/tablet/mobile;
- ảnh thay đổi theo CMS/content khi applicable;
- default/hover/focus nếu text là interactive;
- font weight/size thực tế;
- text color có bị cascade/specificity ghi đè không.

Nếu background luminance thay đổi và readability không ổn định, ưu tiên một trong:

1. **local contrast backplate/scrim** ngay sau text;
2. directional gradient chỉ ở vùng text;
3. reposition text vào safe area ổn định;
4. tách text khỏi ảnh.

Không làm tối toàn bộ ảnh quá mức chỉ để cứu chữ nếu local treatment giải quyết được.

Các anti-pattern phải FAIL:

- text màu tối nằm trực tiếp trên ảnh tối/chuyển động;
- white text trên vùng ảnh sáng mà không có stable contrast treatment;
- global overlay làm ảnh mất detail nhưng text vẫn khó đọc;
- CSS owner nói `color:#fff` nhưng selector tổng quát có specificity cao hơn khiến rendered text thành màu khác;
- text panel chạm/cắt nhau ở mobile;
- chỉ test một crop desktop.

Nếu nội dung quan trọng không đọc được ngay → P0/P1 tùy task impact.

## Human-subject / focal-crop gate — hard gate when applicable

Nếu hero/feature media có người hoặc focal subject rõ:

- inspect actual rendered crop ở mọi viewport/pressure point trong declared scope;
- `object-fit: cover` hoặc một giá trị `object-position` không phải evidence;
- face, eyes, top of head hoặc primary identifying feature không được bị cắt vô lý;
- kiểm overlay/panel có che subject không;
- nếu một asset không sống được qua các crop cần thiết, dùng responsive art direction/alternate crop/layout thay vì ép một `cover` crop.

Crop obvious sai ở primary hero/decision media là P1; nếu làm mất nội dung quyết định chính có thể P0.

## Raster native-resolution / media-quality gate — hard gate

Trước khi dùng raster asset làm hero, diagram, floor plan, map, card lớn hoặc full-width object:

- inspect intrinsic pixel dimensions khi tooling cho phép;
- inspect file quality/compression và source provenance;
- so intrinsic size với rendered CSS box + target DPR;
- kiểm `object-fit`, crop và scaling;
- ưu tiên SVG/PDF/vector hoặc higher-resolution first-party asset cho diagrams khi có;
- nếu chỉ có thumbnail/low-resolution raster, **không phóng thành hero**.

Decision rule:

```text
low-resolution raster + large rendered box
→ replace with higher-resolution/vector source
OR
→ reduce rendered size and label it as preview
OR
→ choose another verified high-resolution decision object
```

Không dùng CSS filter/contrast/sharpen như cách “sửa” một asset thiếu resolution.

Blur/pixelation obvious ở target viewport là P1 visual-quality defect; nếu diagram cần đọc để user quyết định mà unreadable thì có thể P0.

## State audit

Mọi interactive component kiểm: default, hover, focus-visible, active, disabled, loading, error và selected/expanded nếu có.

Không chỉ nhìn xem state “có CSS”. Kiểm label/icon thực tế vẫn nhìn thấy được trên rendered surface và selector winning state đúng như intended contract.

## Responsive visual QA

Tại mobile/tablet/desktop kiểm riêng theo declared scope:

- Reading order.
- Crop ảnh.
- Line wrapping ở title/button/nav.
- Touch target.
- Overflow.
- Sticky/fixed elements che content.
- Density và white space.
- Hero/page composition có được **recomposed** hay chỉ stack/shrink desktop.
- Overlay labels/pseudo-elements có va chạm, clip hoặc chồng chữ không.
- Text-on-image safe zone còn tồn tại sau crop không.
- Raster/diagram có bị phóng lớn hơn mức source chịu được không.

## Evidence set

Trước done, với substantial multi-page website nên có tối thiểu:

- desktop representative captures theo project target;
- mobile representative captures khi mobile nằm trong scope;
- tablet/intermediate width khi layout có risk và nằm trong scope;
- cross-page top-of-page montage/contact sheet;
- changed interactive state capture nếu state visual quan trọng;
- text-on-image examples có actual crop;
- large media/diagram examples đủ để đánh giá sharpness;
- all-affected-route elementary sanity scan khi shared owner thay đổi.

Không bắt buộc một viewport cố định cho mọi project; chọn theo audience/device evidence. Nhưng không được inspect ngoài declared scope rồi suy ra `fully responsive`.

Ghi issue severity P0/P1/P2 và phân biệt:

- `[product]` actual rendered UI sai;
- `[evidence]` screenshot/capture/render artifact không đủ để kết luận.

## Fix loop

`capture → inspect elementary sanity → inspect macro → log P0/P1/P2 → fix owning component/token/composition/media source → recapture → compare`

- P0/P1 phải được xử lý hoặc ghi rõ blocker trước handoff.
- Không sửa micro-detail P2 trong khi composition/hierarchy P1 còn sai.
- Nếu user phải chỉ ra một lỗi obvious mà rendered evidence lẽ ra đã phát hiện, thêm lỗi đó thành regression check/checklist cho **project và owning skill/eval** thay vì chỉ vá project.
- Nếu defect do media source không đủ chất lượng, sửa source/media strategy trước khi thêm visual effect để che lỗi.

## Acceptance criteria

- [ ] Actual rendered implementation đã được mở/inspect; nếu không thì status là BLOCKED/UNVERIFIED, không PASS.
- [ ] Elementary Visual Sanity Gate đã chạy khi applicable và không còn DUE-NOW P0/P1.
- [ ] Shared surface/background changes có matched foreground/state audit và không còn cascade/specificity mismatch.
- [ ] Shared owner change có all-affected-route sanity coverage.
- [ ] Không có spacing/alignment inconsistency rõ ràng.
- [ ] Không có component variant trùng chức năng.
- [ ] Visual hierarchy đọc được trong 5–10 giây.
- [ ] Cross-page composition không rơi vào template monotony vô lý.
- [ ] Primary page roles có first visual anchor phù hợp user task.
- [ ] Responsive claims đúng declared scope; mobile không bị “compressed desktop” khi mobile in-scope.
- [ ] Focus/error/loading states nhìn thấy được.
- [ ] Logo/nav/CTA vẫn rõ ở các background/state thực tế.
- [ ] Text-on-image có stable local contrast ở representative crops/viewports.
- [ ] Human/focal-subject media không bị crop vô lý ở declared viewports.
- [ ] Large raster/media không bị obvious upscaling blur ở target viewport.
- [ ] Overlay/pseudo labels không overlap/clip ở mobile/intermediate widths khi in-scope.
- [ ] UI phản ánh brand/domain thay vì generic template.
