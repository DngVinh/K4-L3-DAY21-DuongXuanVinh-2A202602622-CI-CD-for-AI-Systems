# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Dương Xuân Vinh |
| MSSV | 2A202602622 |
| Lớp / Khóa | K4 |
| Repo GitHub | [DngVinh/CI-CD-for-AI-Systems](https://github.com/DngVinh/K4-L3-DAY21-DuongXuanVinh-2A202602622-CI-CD-for-AI-Systems) |
| Ngày nộp | Chưa nộp; chuẩn bị ngày 07/10/2026 |

## 1. Siêu tham số và lý do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |
| 4 | 200 | 0.1 | 3 | 0.7281 | 0.8820 |
| 5 | 200 | 0.05 | 3 | 0.7014 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=3`.

**Lý do:** Bộ 200/0,1/3 đạt F1 cao nhất; 200 cây ở learning rate 0,05 vẫn kém. Depth 5 không cải thiện. Giữ random_state=42; F1 mặc định 0,5 thống nhất API/gate.

## 2. Vì sao gate dùng F1 thay vì accuracy

Lớp thu nhập cao chiếm 24,8%. Luôn đoán thu nhập thấp đạt accuracy 75,2% nhưng F1 dương bằng 0. F1 kết hợp precision/recall lớp dương; weighted F1 ưu tiên lớp đa số, macro F1 trung bình hai lớp, không tương đương gate 0,65. Nếu tìm khách hàng thu nhập cao, bỏ sót mất cơ hội; gán nhầm tăng chi phí. Chi phí thực tế phụ thuộc nghiệp vụ.

## 3. Khó khăn và cách giải quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Thư viện không chạy với môi trường ban đầu. | Máy có Python 3.14, lab dùng thư viện cũ. | Tạo venv Python 3.11 trong workspace. |
| MLflow lỗi import dependency. | Setuptools và SQLAlchemy mới bỏ API cũ. | Pin setuptools 70.3.0 và SQLAlchemy 2.0.30. |
| Push không tạo run tự động. | GitHub chặn workflows của repo fork. | Bật workflows trên UI; commit dữ liệu kích hoạt pipeline. |

## 4. So sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 Actions/VM, 22.361 mẫu | 0.7281 | 0.8820 |
| Bước 3 Actions/VM, 44.722 mẫu | 0.7444 | 0.8860 |

**Nhận xét:** F1 tăng 0,0163, accuracy tăng 0,0040; cùng phân phối nên cải thiện nhỏ. Commit chỉ sửa con trỏ dữ liệu tự kích hoạt bốn jobs xanh. API VM đã tải model mới, run ID khớp report.

Runs: [Bước 2](https://github.com/DngVinh/K4-L3-DAY21-DuongXuanVinh-2A202602622-CI-CD-for-AI-Systems/actions/runs/37573632735), [Bước 3](https://github.com/DngVinh/K4-L3-DAY21-DuongXuanVinh-2A202602622-CI-CD-for-AI-Systems/actions/runs/37574988490).

## 5. Bonus

- [ ] Bonus 1: Workflow hỗ trợ DagsHub; chưa có token và run từ xa.
- [x] Bonus 2: Quét 17 ngưỡng; F1 0,7511 tại 0,4 so với 0,7281 tại 0,5; chưa phải test độc lập.
- [x] Bonus 3: Tạo confusion matrix và precision/recall hai lớp; workflow lưu artifact.
- [x] Bonus 4: Log so sánh F1 cũ/mới; GCS giữ history/versions; tests chặn hồi quy.
- [x] Bonus 5: Ghi tỷ lệ dương 24,77%; tests xác nhận cảnh báo khi lệch trên 5 điểm phần trăm.
