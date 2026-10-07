# Hoàn tất bằng chứng nộp bài

Pipeline chính Bước 2 và Bước 3 đã chạy thành công; vẫn phải bổ sung ảnh thật.
Không dùng JSON/log thay cho các ảnh bắt buộc. Lưu ảnh dưới 1 MB vào
`nop-bai/anh-chup-man-hinh/`, giữ URL trên thanh địa chỉ với ảnh trình duyệt.

| Tên ảnh | Mở trang / thực hiện |
|---|---|
| 01-mlflow-ui.png | http://127.0.0.1:5000, experiment adult-income-lab. Hiện f1_score, accuracy, n_estimators, learning_rate, max_depth bằng Columns; sắp F1 giảm dần, thấy ít nhất ba cấu hình khác nhau. |
| 02-actions-buoc-2.png | [Run Bước 2](https://github.com/DngVinh/K4-L3-DAY21-DuongXuanVinh-2A202602622-CI-CD-for-AI-Systems/actions/runs/37573632735), thấy bốn jobs xanh. |
| 03-actions-buoc-3.png | [Run Bước 3](https://github.com/DngVinh/K4-L3-DAY21-DuongXuanVinh-2A202602622-CI-CD-for-AI-Systems/actions/runs/37574988490), thấy commit data và bốn jobs xanh; event push. |
| 04-curl-api.png | Chụp PowerShell có hai lệnh bên dưới và kết quả, thấy IP VM. |
| 05a-storage-dvc.png | [Bucket GCP](https://console.cloud.google.com/storage/browser/lday21-income-mlops-dngvinh?project=lday21-income-mlops), mở dvc/. |
| 05b-storage-model.png | Cùng bucket, mở artifacts/current/, thấy model.joblib. Hai ảnh 05a/05b được phép thay ảnh 05 theo hướng dẫn gốc. |
| 07-quality-gate-chan.png (tùy chọn) | [Negative proof](https://github.com/DngVinh/K4-L3-DAY21-DuongXuanVinh-2A202602622-CI-CD-for-AI-Systems/actions/runs/37575822975): mô hình yếu thật, gate dự kiến failed và Release skipped. Đây là workflow kiểm chứng không triển khai, không phải lỗi pipeline chính. |

```powershell
curl.exe --fail --silent --show-error http://35.208.68.97:8080/healthz
'{"features":[28,2,14,2,11,0,1,0,0,45]}' | curl.exe --fail --silent --show-error http://35.208.68.97:8080/score -H 'Content-Type: application/json' --data-binary '@-'
```

## Bonus DagsHub (chưa hoàn tất)

Đăng nhập https://dagshub.com bằng GitHub, chọn Create → New Repository → Import
Repository → GitHub. Chỉ cấp quyền cho repo lab và kết nối repo này. Gửi URL repo
DagsHub để xác nhận username/tên repo; tuyệt đối không gửi token vào chat.

Tại GitHub repo → Settings → Secrets and variables → Actions → New repository
secret, thêm ba secret trực tiếp trên giao diện:

- `MLFLOW_TRACKING_URI`: `https://dagshub.com/<USERNAME>/<REPO>.mlflow`.
- `MLFLOW_TRACKING_USERNAME`: username DagsHub.
- `MLFLOW_TRACKING_PASSWORD`: access token DagsHub (không phải mật khẩu GitHub).

Sau đó workflow **DagsHub Tracking Bonus (no deployment)** sẽ ghi năm cấu hình
thật lên MLflow từ xa và lưu báo cáo, không thay thế model VM. Chụp thêm
`06-dagshub-mlflow.png` khi có run thật và cập nhật checkbox bonus 1. Không đánh
dấu hoàn thành chỉ vì có workflow/secrets.

Nguồn: [kết nối repo](https://dagshub.com/docs/quick_start/connect_existing_project/),
[MLflow tracking](https://dagshub.com/docs/feature_guide/experiment_tracking/).

## Kiểm tra cuối

Xác nhận thông tin học viên trong bao-cao.md; báo cáo khoảng 525 từ, cần xem trước
bản in để đảm bảo một trang A4. Kiểm tra ảnh không có secrets, bổ sung ảnh, commit
và push thư mục nop-bai. Cuối cùng dán URL repo public vào https://vlearn.dev,
mở lại URL ở chế độ ẩn danh; chỉ đánh dấu checklist sau khi thực sự hoàn tất.
