# Fintech: cho vay, trả góp, chuyển tiền

> Hướng dẫn con của skill `industry-playbooks`. Dùng khi sản phẩm (app hoặc web app) cho người dùng vay,
> trả góp, chuyển tiền hoặc ký một cam kết tài chính, kể cả màn vận hành của người duyệt.
> Không phải tư vấn pháp lý: cách công bố lãi suất, phí và hợp đồng phải được pháp chế kiểm theo quy định hiện hành.

## Câu hỏi người dùng trước mọi quyết định tiền

1. Tôi nhận về bao nhiêu, sau mọi khoản bị trừ?
2. Mỗi kỳ tôi trả bao nhiêu, bao nhiêu kỳ, kỳ cuối có khác không?
3. Tổng cộng tôi trả bao nhiêu, và trong đó chi phí là bao nhiêu?
4. Khoản trả có vừa sức tôi không?
5. Bấm nút này thì tiền có đi ngay không, và quay lại được không?

Màn quyết định và sheet xác nhận phải trả lời đủ 1–3 bằng con số, không chỉ bằng lời.

## Trình bày chi phí

- Viết thành **phép tính cộng khớp tới từng đồng**: số vay − phí trừ trước = nhận về; gốc + lãi = tổng trả góp;
  lãi + phí = chi phí vay. Một con số tổng không kèm phép tính bị coi là phí ẩn, kể cả khi nó đúng.
- Phí trừ khi giải ngân là một **dòng trừ** có tên, không gộp im lặng vào "tổng phải trả".
- Kỳ trả làm tròn thì ghi **kỳ cuối** riêng ("11 kỳ 13.468.068 ₫, kỳ cuối 13.468.064 ₫") để tổng các kỳ đúng bằng tổng trả góp.
- Lãi suất ghi theo năm, kèm cách tính (ví dụ dư nợ giảm dần) ở chỗ người dùng xem trước khi ký.
- Một khái niệm một tên trên mọi màn và mọi vai trò: không lúc "tổng phải trả" lúc "tổng trả góp".
- Số tiền dùng `tabular-nums`, căn phải theo cột, cùng đơn vị ₫.

## Khả năng trả

Đặt khoản trả mỗi kỳ cạnh thu nhập hoặc doanh thu người dùng đã khai (ví dụ "khoảng 449.000 ₫ mỗi ngày bán
hàng, 19% doanh thu"). Khi có nhiều kỳ hạn, cho chọn ngay trên màn và cập nhật mọi con số cùng lúc.

## Xác nhận, kết quả, lỗi

- Ký, chuyển, giải ngân: sheet xác nhận lặp lại đúng các con số của lựa chọn hiện tại, có Hủy; Hủy giữ lựa chọn.
- Màn kết quả nói: ngày tiền đến, tài khoản nhận, kỳ trả đầu, số tiền mỗi kỳ.
- Lỗi khi gửi: nói rõ **chưa có tiền nào chuyển đi** hoặc chưa có gì được ghi nhận, giữ dữ liệu đã nhập, chặn gửi lặp,
  và không để danh sách bên dưới vẫn ghi "Đã nhận".
- Đề xuất có hạn: ghi hạn kèm thứ; quá hạn thì có đường xin đề xuất mới.

## Màn vận hành (người duyệt)

- Duyệt bị khoá khi thiếu điều kiện, kèm lý do đọc được; yêu cầu bổ sung và từ chối luôn sẵn.
- Từ chối bắt chọn lý do gửi người dùng; yêu cầu bổ sung nói đúng giấy tờ và hạn, và lời nhắn hiện y nguyên ở phía người dùng.
- Hạn xử lý hôm nay nổi lên bằng icon và chữ, không chỉ bằng màu.

## Kiểm trước khi giao

- Test trình duyệt kiểm **số học** trên sheet xác nhận (tổng các kỳ, gốc + lãi, lãi + phí), không chỉ kiểm có nút.
- Người duyệt độc lập tính tay lại các con số từ ảnh; số lệch là hard fail HF-9.

## Lỗi hay gặp (từ dự án thử)

- "Tổng phải trả" gộp phí đã trừ khi giải ngân, không ghi phép tính: người duyệt thấy 12 × trả mỗi tháng ≠ tổng.
- Lịch trả ghi các kỳ bằng nhau trong khi tổng lệch vài đồng vì làm tròn.
- Nhãn ghép khó hiểu như "12 tháng, 11 kỳ mỗi tháng".
- Phần chi phí nằm dưới thanh hành động cố định, người dùng chỉ thấy khi mở sheet ký.
