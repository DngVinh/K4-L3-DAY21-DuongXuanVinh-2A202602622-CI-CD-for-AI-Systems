# Tiến độ đối chiếu rubric

Cập nhật ngày 07/10/2026. Chỉ đánh dấu phần đã thực thi hoặc kiểm chứng. Người học
đã duyệt tạo tài nguyên trong Project ID `lday21-income-mlops`. Bucket riêng tư
`lday21-income-mlops-dngvinh` đã bật versioning; `dvc push` đã đẩy ba file.
VM `income-api` (e2-micro, us-central1-a, Debian 12/Python 3.11) đang chạy tại
`35.208.68.97`; bootstrap đã hoàn tất, SSH qua IAP và quyền restart đã kiểm chứng.
Bước 2 và Bước 3 có bốn jobs xanh, API VM hoạt động; chưa có DagsHub hoặc ảnh nộp bài.

| Hạng mục | Bằng chứng hiện có | Còn cần làm |
|---|---|---|
| MLflow tracking và metrics | 5 cấu hình trong experiment adult-income-lab; SQLite và artifacts local | Chụp ảnh 01 kèm URL, params, F1/accuracy |
| Phân tích siêu tham số | Chọn 200 cây / 0,1 / depth 3; report đã điền | Xác nhận thông tin học viên và xem trước bản in A4 |
| DVC | Ba CSV, ba con trỏ .dvc; remote GCS và push thành công | Ảnh 05 |
| CI/CD bốn jobs | Run 37573632735 có bốn jobs xanh; 34 tests qua | Chụp ảnh 02 |
| Quality gate | CLI và tests chặn F1 < 0,65, NaN và F1 hồi quy | Chụp run Actions Quality Gate failed / Release skipped |
| Serving | API IP VM healthz/score/version qua; run ID khớp report | Ảnh 04 |
| Tự động hóa dữ liệu | Run push 37574988490 từ commit chỉ sửa con trỏ; bốn jobs xanh | Ảnh 03 |
| Bonus 1 | Workflow nhận URI/username/token MLflow từ secrets | Liên kết DagsHub, chạy và chụp ảnh remote |
| Bonus 2 | 17 ngưỡng, best threshold và F1 mặc định được log riêng | Giữ metrics triển khai/ngưỡng phục vụ nhất quán |
| Bonus 3 | Detail trong artifact Actions/GCS; bản sao tại detail-cloud-buoc-3.txt | Có thể thêm ảnh/log bonus |
| Bonus 4 | Log so sánh F1 và history/versions GCS đã kiểm chứng; tests chặn hồi quy | Có thể thêm ảnh/log bonus |
| Bonus 5 | Tỷ lệ dương 24,77%; tests với 43,75% kích hoạt drift | Lưu log cảnh báo ở run thực nếu muốn thêm bằng chứng |

## Số liệu có thể tái tạo

- Batch 1: F1 **0,7281**, accuracy **0,8820**, ngưỡng phục vụ **0,5**.
- Batch 1 + batch 2: F1 **0,7444**, accuracy **0,8860**, ngưỡng phục vụ **0,5**.
- Bonus quét ngưỡng batch 1: best F1 **0,7511** tại **0,4**; là chẩn đoán
  chọn ngưỡng trên holdout, không thay đổi rule phục vụ của pipeline lõi.
- Chi tiết metrics, hashes và run IDs: [ket-qua-local.json](ket-qua-local.json).
- Sau Bước 2, batch 2 đã được append vào dataset chính; snapshot batch 1 giữ
  nguyên MD5 `6097c9bf1219a011f64a7a594a7b617d`. Dataset 44.722 mẫu đã lên GCS.
  F1 0,7444 và accuracy 0,8860 đã xác nhận trên Actions và model phục vụ ở VM.

## Bằng chứng còn thiếu

CI dùng `income-ci`, VM dùng `income-vm` chỉ đọc GCS. WIF chỉ chấp nhận đúng
repo và nhánh main; mạng `income-lab` riêng, SSH chỉ cho dải IAP, API 8080 công khai.
Không tạo khóa JSON GCP dài hạn. Secret GCP provider/account/bucket đã được tạo.
Lỗi truy cập khóa giữa hai tài khoản Windows đã giải quyết bằng phiên đăng nhập
GitHub riêng của sandbox, được người học duyệt và xác thực bằng mã thiết bị.
Không sao chép token cũ, thay đổi ACL hay vượt qua cơ chế chặn. Secrets SSH và
public host key đã thiết lập; host key lấy từ serial console GCP và được pin.

Người học đã xác nhận rõ danh sách thay đổi Bước 3 bằng câu xác nhận phá hủy.
Đã cấp role thay thế riêng, chỉ đúng hai object current và tự hết hiệu lực lúc
14:00 ngày 07/10/2026 (Asia/Bangkok). Không xóa phiên bản/history; model current
đã là Bước 3, cả hai generations cũ và bản sao history vẫn còn. Nếu cần cấp lại phải xin
duyệt mới, không coi xác nhận cũ là quyền triển khai lâu dài.

Commit `d35461e` đổi hash/size dữ liệu; `14f46d5` thêm metadata 44.722 mẫu.
Cả hai chỉ sửa `data/train_batch1.csv.dvc`. UI người học cung cấp đã xác nhận
GitHub chặn workflows của fork dù API báo enabled/active; người học bấm bật.
Commit `67447c0` bổ sung SHA256 dữ liệu (vẫn chỉ sửa con trỏ) đã tự kích hoạt
run `37574988490`, event `push`, bốn jobs success. Không dispatch thủ công Bước 3.
Model/report checksum và run ID VM khớp; log so sánh F1 0,728111 -> 0,744395.
Chi tiết:
[du-lieu-buoc-3.json](du-lieu-buoc-3.json).

Chưa có năm ảnh 01–05. Công cụ UI phiên này không có trình duyệt kết nối và
không mở được in-app browser; MLflow UI local đã được khởi động và trả HTTP 200.
Mở http://127.0.0.1:5000 để chụp experiment adult-income-lab.

Code đã commit/push tại `1c60e43`; repo public. Bước 2 đã hoàn tất qua dispatch,
không coi đây là bằng chứng tự động hóa dữ liệu Bước 3. Kết quả và URL Actions
thật nằm trong [ket-qua-cloud-buoc-2.json](ket-qua-cloud-buoc-2.json). Chưa đánh dấu
checklist nộp bài hoàn tất hoặc khẳng định đạt 100 điểm. Làm các bước còn thiếu
trong [DEPLOYMENT.md](../DEPLOYMENT.md).
