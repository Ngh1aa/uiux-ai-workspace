# Dữ liệu bộ đề chuẩn

Nhánh này chỉ chứa dữ liệu benchmark của [uiux-ai-workspace](https://github.com/Ngh1aa/uiux-ai-workspace):
`benchmarks/runs/`, `benchmarks/evidence/` và `benchmarks/trials/`. Code, đề và `REPORT.md` nằm ở `main`.

`main` ghi commit dữ liệu đang dùng trong `benchmarks/data-ref.txt`. Lấy dữ liệu về cây làm việc của `main`:

```sh
python scripts/fetch-benchmark-data.py
```

Cách thêm một lần chạy mới: xem `benchmarks/README.md` trên `main`.
Không sửa file đã có: điểm, ảnh và bằng chứng được ràng bằng SHA-256.
