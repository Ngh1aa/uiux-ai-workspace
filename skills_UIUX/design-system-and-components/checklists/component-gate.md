# Design System / Component Gate

- [ ] Existing system inventoried trước khi thêm mới.
- [ ] Primitive và semantic tokens phân vai rõ.
- [ ] Semantic surface/foreground pairs rõ; shared surface không đổi background một mình rồi phụ thuộc accidental inheritance cho text/link/icon.
- [ ] P0 components có purpose/anatomy/API rõ.
- [ ] Variants có semantic reason.
- [ ] Hover/focus/active/disabled/loading/error states theo scope.
- [ ] Mọi visible state giữ label/icon perceptible trên actual rendered surface; hover/focus/disabled không tạo white-on-white / dark-on-dark / effectively invisible control.
- [ ] Component có surface riêng own foreground/icon/border/focus state thay vì kế thừa màu parent một cách ngẫu nhiên.
- [ ] Selector/cascade specificity được kiểm khi computed style khác intended component contract.
- [ ] Responsive behavior documented.
- [ ] Accessibility contract documented.
- [ ] Parent/child composition spacing rõ.
- [ ] Không duplicate component gần giống.
- [ ] Representative real content tested, không chỉ lorem ipsum.
- [ ] Representative component được render trên các materially different surface contexts (light, inverse/dark, media overlay...) khi applicable.
- [ ] Long text/empty image/missing data states được xem xét.
