# Bốn ví dụ: cùng phương pháp, khác quyết định thiết kế

**SYNTHETIC WORKED EXAMPLES — không phải user findings, live benchmark, screenshots hay case study thành công.** Brief và observation cards dưới đây là đầu vào giả lập cố định để thực hành. Mỗi case có nguồn fixture ngay tại anchor để không gắn một website thật vào quan sát chưa kiểm tra. Khi dùng cho project, phải thay bằng nguồn thực. Không có participants; human preference, task success và impact đều UNKNOWN.

## Corporate

Phạm vi dịch vụ.

**Brief/nguồn fixture C0:** buyer là engineering/procurement, cần quyết định mời tư vấn; một service có inputs, outputs và exclusions. Prototype chưa có commercial proof.

**C1 — observation fixture:** nội dung đầu vào có hai phương án cùng các thuộc tính input/output/out-of-scope. **C2 — phản chứng fixture:** scope cuối cùng còn phụ thuộc khảo sát, không có giá/gói tiêu chuẩn. C1/C2 không phải quan sát người dùng.

**Câu hỏi:** người đọc phân biệt được fit ban đầu với cam kết phạm vi chưa? Reference cần tìm thật: service detail, sample scope document và RFQ, không chỉ homepage nhà máy.

**Transfer:** ADOPT nguyên tắc căn các thuộc tính tương ứng để đọc đối chiếu; ADAPT thành scope preview với điều kiện khảo sát từ C2; REJECT pricing-card cố định vì nó ngụ ý scope đã chốt.

**D-C (hypothesis):** Home có một đoạn định hướng và sơ đồ phạm vi; service detail dùng nhãn/giá trị + sample deliverable. Sans sentence case cho giải thích; mono chỉ cho document ID/revision. Mật độ vừa ở detail, thấp ở mở đầu; hình chính là scope sheet có chú thích, không phải ảnh máy móc bất kỳ. Mobile nhóm input/output/exclusion theo nhiệm vụ, tránh buộc so hai cột nhỏ.

**Alternative:** A = technical scope record; B = editorial case narrative với title serif/sans tương phản, khoảng nghỉ lớn và một diagram giải thích. Cùng claim/CTA; khác type/density/object. Chọn A làm giả thuyết ban đầu vì fixture cần đối chiếu, chưa gọi là winner.

**Kiểm:** tìm một exclusion, chọn service fit, giải thích bước nào còn cần khảo sát; kiểm bản RFQ giữ dữ liệu khi Back. Không đặt tỷ lệ thành công bịa.

## Ecommerce

Độ phù hợp sản phẩm.

**Brief/nguồn fixture E0:** khách mua một món đồ có kích thước, chất liệu và biến thể; cần biết có vừa không trước khi mua.

**E1 — observation fixture:** bảng nội dung có kích thước theo variant và ảnh silhouette. **E2 — phản chứng fixture:** số đo giống nhau không bảo đảm cảm nhận chất liệu hay fit thực tế.

**Câu hỏi:** khách có tìm đúng variant, điều kiện fit và giới hạn ảnh không? Reference cần tìm thật: product detail, size guide, variant unavailable và return policy.

**Transfer:** ADOPT nhóm ảnh/variant/size ở gần quyết định; ADAPT comparison theo thuộc tính quan trọng, bổ sung ảnh scale và chú thích giới hạn E2; REJECT hero chỉ đẹp nhưng che lựa chọn hoặc crop mất đặc điểm sản phẩm.

**D-E (hypothesis):** display có bản sắc brand nhưng body/UI trung tính dễ đọc; tên variant và giá rõ cấp bậc, không mono hóa toàn trang. Media chiếm ưu tiên; bảng thông số ngắn hơn gallery, CTA sau lựa chọn đủ điều kiện. Mobile giữ thứ tự ảnh → variant → fit/availability → action, size guide mở mà không mất lựa chọn. Đừng đem density của RFQ B2B sang product detail.

**Alternative:** A = gallery dẫn dắt, display giàu biểu cảm và nhịp thoáng; B = comparison/spec dẫn dắt, type gọn hơn và bảng dense với ảnh crop chi tiết. Cùng giá/variant/policy/CTA.

**Kiểm:** chọn đúng variant theo kích thước cho trước, tìm chính sách trả, xử lý variant hết hàng; hỏi lý do chọn để biết ảnh có gây hiểu sai. Purchase conversion vẫn UNKNOWN nếu chưa có hành vi thật.

## SaaS

Cơ chế và giới hạn.

**Brief/nguồn fixture S0:** website giới thiệu công cụ phê duyệt và thực thi yêu cầu; mọi demo synthetic.

**S1 — observation fixture:** mô hình có decision và execution tách nhau. **S2 — phản chứng fixture:** người mới chưa biết các từ provisioning/reconciliation; record đầy đủ có thể quá tải lần đọc đầu.

**Câu hỏi:** người xem hiểu sản phẩm làm gì và approval có bảo đảm execution thành công không? Reference thật cần Home, workflow detail, integration limitations và tour.

**Transfer:** ADOPT việc đặt lời giải thích cạnh trạng thái cụ thể; ADAPT record thành phần cốt lõi trên Home rồi mở history ở detail theo S2; REJECT ảnh hardware nếu không phải sản phẩm phần cứng, và không mượn badge/customer từ hãng khác.

**D-S (hypothesis):** Home sans sentence case với một statement ngắn và record có chú thích; UI/meta nhỏ hơn nhưng vẫn đọc được; mono cho ID/time. Density tăng từ Home sang record; diagram diễn tả hai lớp trạng thái thay vì một đường tuyến tính giả. Mobile đọc actor → scope → decision → execution → next action. Không thu dashboard desktop thành thumbnail.

**Alternative:** A = record gọn/neo-grotesk/density vừa; B = typographic statement lớn/giải thích serif/density thấp, lifecycle diagram là object chính. Giữ cùng facts/state/CTA; không kết luận font nào gây hiệu quả nếu đổi cả ba trục.

**Kiểm:** người xem diễn giải sản phẩm, tìm xác nhận thực thi và một integration limit; sau tác vụ xen kẽ hỏi họ nhớ gì. Demo completion nói rõ không gửi request thật.

## Dashboard

Quyết định của operator.

**Brief/nguồn fixture D0:** operator xử lý queue sự cố; cần severity, owner, freshness và thao tác phục hồi.

**D1 — observation fixture:** queue có items cần đối chiếu theo severity/age. **D2 — phản chứng fixture:** mobile dùng khi đang di chuyển; một số item thiếu dữ liệu cập nhật, không thể xếp “safe” từ giá trị trống.

**Câu hỏi:** operator nhận diện việc tiếp theo và dữ liệu stale/unknown đúng không? Reference thật cần queue, detail, loading/error/retry và audit history, không chỉ dashboard overview.

**Transfer:** ADOPT hàng/cột đối chiếu với row labels; ADAPT responsive bằng priority fields + detail disclosure theo D2; REJECT đổi mọi dòng thành card khiến không so được cột, và reject màu như tín hiệu duy nhất.

**D-D (hypothesis):** body/UI sans gọn, tabular figures cho so số, title vừa phải; density cao ở desktop queue, khoảng nghỉ quanh task actions. Object chính là queue và event history, không illustration. Mobile ưu tiên severity/owner/age, ghi Unknown/last confirmed; bảng hai chiều chỉ dùng khi cần so cột và có label/focus rõ.

**Alternative:** A = compact table/nhãn chữ + biểu tượng/row actions; B = prioritized case stream, type lớn hơn, density thấp hơn, timeline là object. Cùng incident facts/actions; B có thể mất so sánh đồng thời nên chưa chọn theo cảm giác đẹp.

**Kiểm:** chọn item cần xử lý, phân biệt stale với healthy, retry không duplicate, giữ focus khi thông báo cập nhật. Không gọi expert walkthrough là nghiên cứu operator thực tế.

## Cách dùng để đánh giá kiến thức

Giữ nguyên các brief và observation cards trước/sau thay đổi skill. Đánh giá reasoning có giữ phản chứng, phân lớp bằng chứng và dẫn đến page/state/property cụ thể không. Các câu trả lời mẫu trên không là đáp án duy nhất, không là target để regex chấm điểm. Routing tests chỉ chứng minh context tới đúng stage; nghiên cứu đẹp hơn/hiệu quả hơn cần bằng chứng khác.
