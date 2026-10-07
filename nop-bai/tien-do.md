# Tiến độ đối chiếu rubric

Cập nhật ngày 07/10/2026. Chỉ đánh dấu phần đã thực thi hoặc kiểm chứng. Người học
đã duyệt tạo tài nguyên trong Project ID `lday21-income-mlops`. Bucket riêng tư
`lday21-income-mlops-dngvinh` đã bật versioning; `dvc push` đã đẩy ba file.
VM `income-api` (e2-micro, us-central1-a, Debian 12/Python 3.11) đang chạy tại
`35.208.68.97`; bootstrap đã hoàn tất, SSH qua IAP và quyền restart đã kiểm chứng.
Bước 2 đã có bốn jobs xanh và API VM hoạt động; chưa có DagsHub hoặc ảnh nộp bài.

| Hạng mục | Bằng chứng hiện có | Còn cần làm |
|---|---|---|
| MLflow tracking và metrics | 5 cấu hình trong experiment adult-income-lab; SQLite và artifacts local | Chụp ảnh 01 kèm URL, params, F1/accuracy |
| Phân tích siêu tham số | Chọn 200 cây / 0,1 / depth 3; report đã điền | Xác nhận thông tin học viên và xem trước bản in A4 |
| DVC | Ba CSV, ba con trỏ .dvc; remote GCS và push thành công | Ảnh 05 |
| CI/CD bốn jobs | Run 37573632735 có bốn jobs xanh; 34 tests qua | Chụp ảnh 02 |
| Quality gate | CLI và tests chặn F1 < 0,65, NaN và F1 hồi quy | Chụp run Actions Quality Gate failed / Release skipped |
| Serving | API IP VM healthz/score/version qua; run ID khớp report | Ảnh 04 |
| Tự động hóa dữ liệu | Script giữ snapshot batch 1, từ chối append lặp; so sánh 44.722 mẫu local | Hoàn tất Bước 2 rồi append, dvc push, commit dữ liệu, ảnh 03 |
| Bonus 1 | Workflow nhận URI/username/token MLflow từ secrets | Liên kết DagsHub, chạy và chụp ảnh remote |
| Bonus 2 | 17 ngưỡng, best threshold và F1 mặc định được log riêng | Giữ metrics triển khai/ngưỡng phục vụ nhất quán |
| Bonus 3 | Confusion matrix và precision/recall hai lớp trong detail.txt | Xác nhận artifact trên Actions |
| Bonus 4 | Test chặn hồi quy; publisher tạo immutable history trước cập nhật | Kiểm chứng trên bucket/VM thực |
| Bonus 5 | Tỷ lệ dương 24,77%; tests với 43,75% kích hoạt drift | Lưu log cảnh báo ở run thực nếu muốn thêm bằng chứng |

## Số liệu có thể tái tạo

- Batch 1: F1 **0,7281**, accuracy **0,8820**, ngưỡng phục vụ **0,5**.
- Batch 1 + batch 2: F1 **0,7444**, accuracy **0,8860**, ngưỡng phục vụ **0,5**.
- Bonus quét ngưỡng batch 1: best F1 **0,7511** tại **0,4**; là chẩn đoán
  chọn ngưỡng trên holdout, không thay đổi rule phục vụ của pipeline lõi.
- Chi tiết metrics, hashes và run IDs: [ket-qua-local.json](ket-qua-local.json).
- Batch 1 gốc chưa được append trong dataset chính, để giữ đúng trình tự
  chứng minh Bước 2 trước khi chạy Bước 3. Dataset kết hợp chỉ nằm trong file local.

## Bằng chứng còn thiếu

CI dùng `income-ci`, VM dùng `income-vm` chỉ đọc GCS. WIF chỉ chấp nhận đúng
repo và nhánh main; mạng `income-lab` riêng, SSH chỉ cho dải IAP, API 8080 công khai.
Không tạo khóa JSON GCP dài hạn. Secret GCP provider/account/bucket đã được tạo.
Lỗi truy cập khóa giữa hai tài khoản Windows đã giải quyết bằng phiên đăng nhập
GitHub riêng của sandbox, được người học duyệt và xác thực bằng mã thiết bị.
Không sao chép token cũ, thay đổi ACL hay vượt qua cơ chế chặn. Secrets SSH và
public host key đã thiết lập; host key lấy từ serial console GCP và được pin.

Quyền publisher hiện không có `storage.objects.delete`: đủ tạo artifact mới,
chưa đủ thay thế object current của lần phát hành sau. Trước Bước 3 cần duyệt
chính xác hai object current, hiệu ứng thay thế và cách khôi phục bằng versioning/history.

Chưa có năm ảnh 01–05. Công cụ UI phiên này không có trình duyệt kết nối và
không mở được in-app browser; MLflow UI local đã được khởi động và trả HTTP 200.
Mở http://127.0.0.1:5000 để chụp experiment adult-income-lab.

Code đã commit/push tại `1c60e43`; repo public. Bước 2 đã hoàn tất qua dispatch,
không coi đây là bằng chứng tự động hóa dữ liệu Bước 3. Kết quả và URL Actions
thật nằm trong [ket-qua-cloud-buoc-2.json](ket-qua-cloud-buoc-2.json). Chưa đánh dấu
checklist nộp bài hoàn tất hoặc khẳng định đạt 100 điểm. Làm các bước còn thiếu
trong [DEPLOYMENT.md](../DEPLOYMENT.md).
