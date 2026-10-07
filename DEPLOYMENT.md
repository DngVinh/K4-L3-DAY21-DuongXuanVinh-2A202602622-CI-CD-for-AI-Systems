# Hoàn tất lab trên GCP và thu thập bằng chứng 100 điểm

Mã nguồn hỗ trợ toàn bộ tiêu chí chính và năm bonus. Các mục cloud bên dưới cần
tài khoản GCP/GitHub của người học; cấu hình sẵn không chứng minh rằng đã triển khai.
Không có thao tác xóa tài nguyên hoặc dọn dữ liệu trong hướng dẫn này.

## 1. Chạy và tái tạo kết quả cục bộ

Dùng Python 3.11 để tương thích các phiên bản trong `requirements.txt`.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
.\.venv\Scripts\python.exe prepare_data.py
.\.venv\Scripts\python.exe -m src.experiments --compare
.\.venv\Scripts\mlflow.exe ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Chỉ chạy `prepare_data.py` khi ba file CSV chưa tồn tại; script gốc ghi dữ liệu ra
các đường dẫn cố định. Chỉ chạy bộ thí nghiệm khi thư mục đầu ra là mới hoặc khi
đã kiểm tra dữ liệu của lần trước. Dữ liệu kết hợp dùng để so sánh cục bộ nằm ở
`data/local_combined.csv`, giữ nguyên batch 1 để chạy pipeline Bước 2 trước.
`outputs/experiments.json` chứa kết quả thật của từng run và so sánh hai batch.

MLflow ghi các metrics F1/accuracy, tham số và model vào experiment
`adult-income-lab`. Trong UI hiện các cột `f1_score`, `accuracy`,
`n_estimators`, `learning_rate`, `max_depth`, sắp xếp F1 giảm dần, rồi chụp
`nop-bai/anh-chup-man-hinh/01-mlflow-ui.png` kèm thanh địa chỉ.

Quét ngưỡng trên holdout theo yêu cầu bonus tạo ra chỉ số có ảnh hưởng của việc
chọn ngưỡng; đây chưa phải đánh giá độc lập trên một test set mới. Holdout không
được đưa vào `fit()`. Core dùng `model.predict()` (ngưỡng 0,5) cho F1 gate và
API; `best_threshold` và `best_f1_score` được ghi riêng để so sánh bonus 2.

## 2. Chuẩn bị GCP

Project ID do người học cung cấp: `lday21-income-mlops`. Tên tài nguyên dự kiến:
bucket `lday21-income-mlops-dngvinh`, VM `income-api`, zone `us-central1-a`.
Đã xác nhận đăng nhập, project ACTIVE và billing bật. Người học đã duyệt tạo
tài nguyên: bucket riêng tư/versioning, VM e2-micro Debian 12 tại `35.208.68.97`,
mạng riêng `income-lab`; SSH chỉ qua IAP, cổng API 8080 công khai. Bootstrap đã
hoàn tất; Python 3.11.2 và quyền restart service đã kiểm chứng qua SSH.
Run Actions `37573632735` đã có bốn jobs xanh; API VM healthz/score/version
đã kiểm chứng, run ID `6c4bab25c3594612849243a6e97b47d8`, F1 0,7281/accuracy 0,8820.

Google Cloud CLI dùng bản archive 588.0.0 chính thức trong
`.tools/google-cloud-sdk`; cấu hình riêng ở `.tools/gcloud-config` được loại khỏi
Git. Windows hiện có ExecutionPolicy Restricted, nên dùng lệnh CLI chính thức
dưới đây thay vì chạy wrapper PowerShell chưa ký. Không cần đổi ExecutionPolicy.
Từ PowerShell tại gốc repo:

```powershell
$env:CLOUDSDK_CONFIG = Join-Path (Get-Location) '.tools\gcloud-config'
$env:CLOUDSDK_PYTHON = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$env:CLOUDSDK_CORE_PROJECT = 'lday21-income-mlops'
& '.\.tools\google-cloud-sdk\bin\gcloud.cmd' auth login --update-adc
& '.\.tools\google-cloud-sdk\bin\gcloud.cmd' projects describe lday21-income-mlops
```

Hoàn tất đăng nhập tài khoản có quyền truy cập project trong trình duyệt.
`--update-adc` tạo credentials cho các SDK/DVC dùng cùng tài khoản; không dán
token, mã xác thực hoặc nội dung credentials vào chat. Xem
[tài liệu đăng nhập Google Cloud CLI](https://docs.cloud.google.com/sdk/gcloud/reference/auth/login).
Lệnh chỉ kiểm tra project; chưa tạo bucket/VM hoặc cấp quyền IAM mới.

Chọn project GCP đã bật billing và kiểm tra ngân sách trước khi tạo VM. Việc VM
nhỏ nằm trong ưu đãi miễn phí phụ thuộc tài khoản, region và hạn mức hiện tại.
Làm theo `tasks/buoc-2.md`, các mục 2.1–2.5, với các lưu ý:

- Bucket riêng cho lab; service account có `roles/storage.objectAdmin` chỉ trên
  bucket đó, không cấp quyền quản trị/xóa bucket.
- VM Ubuntu 22.04, Python 3.11 và scikit-learn **1.4.2** giống môi trường train.
- Cổng 8080 chỉ mở tới các IP cần kiểm thử; API lab chưa có xác thực người dùng.
- Dùng ADC/identity của VM hoặc file key được quản lý riêng. Không đưa key vào Git.
- SSH key tạo trong đường dẫn được người học chỉ định; cấu hình quyền restart
  duy nhất service `income-api` cho user triển khai.

Trong workspace, đặt đường dẫn file key qua biến môi trường (không gửi nội dung
key vào chat). Sau khi có tên bucket thực:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = '<duong-dan-key-do-ban-quan-ly>'
$env:DVC_SITE_CACHE_DIR = Join-Path (Get-Location) '.tools/dvc-site-cache'
.\.venv\Scripts\dvc.exe remote add -d labstore gs://<TEN_BUCKET>/dvc
.\.venv\Scripts\dvc.exe push
```

`.dvc/config` ban đầu chỉ định tên remote; **chưa có URL bucket thực**. Lệnh
`remote add` điền URL này. CI lấy tên bucket từ secret và tạo cấu hình local.
Các file CSV được giữ ngoài Git; chỉ commit ba con trỏ `.csv.dvc`.

## 3. VM và service

Triển khai source vào một thư mục dành riêng cho lab trên VM, ví dụ
`/home/<USER>/income-lab`, bao gồm `src/__init__.py` và `src/serve.py`.
Tạo venv Python 3.11 cho service rồi cài các dependency phục vụ:

```text
fastapi==0.111.0
uvicorn==0.29.0
scikit-learn==1.4.2
pandas==2.2.2
joblib==1.4.2
google-cloud-storage==2.16.0
```

Dùng mẫu `deploy/income-api.service.example`; thay USER, BUCKET và đường dẫn.
Service tải model GCS vào bộ nhớ lúc khởi động, không ghi vào thư mục home.
Chưa khởi động service trước khi model được publish lần đầu.

## 4. GitHub Secrets và Bước 2

Thiết lập các repository secrets:

| Secret | Giá trị |
|---|---|
| GCP_WORKLOAD_IDENTITY_PROVIDER | projects/199867906533/locations/global/workloadIdentityPools/income-github/providers/github |
| GCP_SERVICE_ACCOUNT | income-ci@lday21-income-mlops.iam.gserviceaccount.com |
| ARTIFACT_BUCKET | Tên bucket, không gồm gs:// |
| SERVER_SSH_KEY | Private key triển khai |
| SERVER_HOST_KEY | Toàn bộ public host key ed25519, lấy qua serial console GCP |
| MLFLOW_TRACKING_URI | URL DagsHub MLflow, nếu làm bonus 1 |
| MLFLOW_TRACKING_USERNAME | Username DagsHub |
| MLFLOW_TRACKING_PASSWORD | Token DagsHub |

Workflow thực tế dùng WIF với token ngắn hạn, giới hạn đúng repo/nhánh main;
không dùng STORAGE_CREDENTIALS. Release mở tunnel IAP tới đúng VM/cổng 22,
SSH bằng user `income-ci`, pin host key; sudo chỉ cho restart `income-api`.
Không mở SSH công khai. Bucket bật versioning; role publisher không có delete.
Người học đã duyệt thay thế hai object current cho Bước 3; role riêng có điều
kiện đúng hai tên object và hết hiệu lực lúc 14:00 ngày 07/10/2026 (Asia/Bangkok).
Giữ version/history, không xóa dữ liệu. Sau hết hạn cần xác nhận mới nếu cấp lại.
Dataset 44.722 mẫu đã push bằng DVC; người học bật workflows bị chặn trên fork.
Commit chỉ sửa con trỏ `67447c0` đã tự tạo run push `37574988490`, bốn jobs xanh;
F1 0,7444, accuracy 0,8860, VM tải run `17a1602cee7b4d68b900c460fb26d716`.
Generations cũ và history còn nguyên; xem `nop-bai/du-lieu-buoc-3.json`.

Bonus 1: kết nối repo với DagsHub, dùng URI
`https://dagshub.com/<USER>/<REPO>.mlflow` theo
[tài liệu DagsHub](https://dagshub.com/docs/feature_guide/experiment_tracking/).
Thiếu secret URI thì CI dùng SQLite; trường hợp này chưa hoàn thành bonus 1.

Commit code, cấu hình DVC và các con trỏ dữ liệu. **DVC push trước git push** để
runner pull đúng dữ liệu. Kiểm tra Actions có bốn jobs xanh rồi chụp ảnh 02.
Train chỉ upload candidate vào `artifacts/runs/<run-id>-<attempt>/`;
Release chỉ cập nhật `artifacts/current/` sau quality gate và so sánh F1 cũ.
Model/report cũ được sao lưu vào `artifacts/history/` trước khi publish.
Precondition generation của GCS chặn ghi đè khi có thay đổi đồng thời; không xóa
candidate, history hoặc dữ liệu cũ.

Hai object current không được cập nhật như một giao dịch duy nhất. Nếu upload
report thất bại sau upload model, Release dừng; không restart service và cần
kiểm tra lịch sử đã lưu để khôi phục cặp model/report phù hợp. Pipeline không
tự xóa hoặc ghi đè lại cặp lỗi. Health check thất bại cũng cần kiểm tra service.

Kiểm tra gate ngay trên máy:

```powershell
.\.venv\Scripts\python.exe -m src.quality_gate --f1 0.64
.\.venv\Scripts\python.exe -m src.quality_gate --f1 0.65
```

Lệnh đầu phải trả exit code khác 0. Tests cũng kiểm tra F1 hồi quy không upload
model. Để chứng minh trên Actions, dùng một commit tham số yếu, lưu ảnh/log
Quality Gate đỏ và Release skipped, sau đó khôi phục tham số bằng patch/commit
mới. Chỉ thay các tham số; giữ nguyên dữ liệu và model đang phục vụ.

## 5. Bước 3 và bằng chứng

Sau khi Bước 2 có đủ bằng chứng, bổ sung batch 2 theo `tasks/buoc-3.md`. Script
`append_batch.py` giữ một bản batch 1 trước khi bổ sung và từ chối chạy lần hai.

```powershell
.\.venv\Scripts\python.exe append_batch.py
.\.venv\Scripts\dvc.exe add data/train_batch1.csv
.\.venv\Scripts\dvc.exe push
git add data/train_batch1.csv.dvc
git commit -m "data: bo sung 22361 mau du lieu moi (train_batch2)"
git push origin main
```

Workflow được kích hoạt bởi con trỏ dữ liệu. Nếu F1 mới thấp hơn model hiện tại,
bonus 4 chủ động chặn Release; không vô hiệu hóa gate để lấy ảnh xanh. Dùng kết
quả so sánh cục bộ để chọn cấu hình đạt ngưỡng và không hồi quy trước khi triển
khai cả hai bước; bộ mặc định được chọn theo F1 của các thí nghiệm thật.

Ảnh 03 phải là run của commit dữ liệu. Ảnh 04 chứa hai lệnh `curl.exe` gọi IP VM
và kết quả; 05 chứa bucket, `dvc/` và `artifacts/current/model.joblib`. Có thể
dùng `/version` để đối chiếu run ID của model đang phục vụ với report.
Thêm ảnh DagsHub, gate chặn, báo cáo detail và drift nếu làm bonus.
Điền report bằng số liệu Actions thật, giữ độ dài tối đa một trang A4, kiểm tra
cả năm ảnh không chứa secrets, rồi commit hồ sơ và nộp URL repo vào vlearn.dev.
