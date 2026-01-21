# AUTO v0 – Definition

**Phase**: Automation Proof  
**Built on**: MPV / Anchor (read-only)  
**Date**: 2026-01-21

---

## 1. Purpose (Mục tiêu duy nhất)

AUTO v0 exists to prove that a verified signal system can be executed automatically in live market conditions without altering signal validity.

AUTO v0 **không nhằm**:
- ❌ tăng lợi nhuận
- ❌ cải thiện win-rate
- ❌ tối ưu entry / exit

> **👉 AUTO v0 chỉ trả lời một câu hỏi duy nhất:**  
> *"Liệu hệ thống có thể tự động thực thi đúng những gì MPV đã chứng minh, một cách lặp lại và kiểm chứng được hay không?"*

---

## 2. Scope (Phạm vi được phép)

AUTO v0 **CHỈ** bao gồm:
1. Consume signal đã LOCKED từ backend
2. Auto-execute signal lên MT4 Demo
3. Ghi nhận:
   - execution time
   - execution price
   - trade lifecycle
4. Append-only execution logs

**Không thêm bất kỳ logic nào khác.**

---

## 3. Non-goals (Những gì AUTO v0 KHÔNG làm)

AUTO v0 **không**:
- ❌ Generate signal
- ❌ Filter signal
- ❌ Optimize SL / TP
- ❌ Retry execution nếu miss
- ❌ Open hơn 1 lệnh / ngày
- ❌ Close lệnh sớm vì "đi ngược"
- ❌ Override bằng tay sau khi auto chạy

> Nếu cần bất kỳ điều nào trên → **không còn là AUTO v0**.

---

## 4. Hard Constraints (Bất biến – kế thừa từ Anchor)

### 4.1 Signal integrity
Signal phải:
- có `timestamp`
- có `TTL`
- `immutable`

**Auto chỉ được đọc, không được sửa.**

### 4.2 Daily execution cap
- Tối đa **1 lệnh / ngày**
- `0` hoặc `1`
- Nếu đã execute → **block toàn bộ signal còn lại trong ngày**

### 4.3 Confidence rule
- Chỉ execute signal có **confidence cao nhất trong ngày**
- Confidence:
  - được tính tại thời điểm generate
  - không update
  - không suy diễn lại

---

## 5. Execution Model

```
Signal (LOCKED, Anchor-defined)
        ↓
Confidence Ranking (read-only)
        ↓
Daily Execution Gate (max 1/day)
        ↓
Execution Adapter (stateless)
        ↓
MT4 Demo Trade
```

**Execution Adapter**:
- Không giữ state
- Không decision-making
- Không market interpretation

---

## 6. Evidence & Logging (bắt buộc)

Mỗi execution phải tạo ra:

### 6.1 Execution log (append-only)
```json
{
  "signal_id": "SIG-20260121-001",
  "signal_time": "2026-01-21T08:15:00Z",
  "auto_order_time": "2026-01-21T08:15:04Z",
  "latency_ms": 4000,
  "signal_price": 1.0872,
  "execution_price": 1.0873,
  "status": "EXECUTED"
}
```

### 6.2 Daily gate log
- Số signal generate
- Signal được execute
- Signal bị skip + reason

---

## 7. Success Criteria (Pass / Fail)

### AUTO v0 được coi là **PASS** nếu:
- ✅ Auto execute đúng signal (ID + timestamp)
- ✅ Không execute signal EXPIRED
- ✅ Không execute hơn 1 lệnh / ngày
- ✅ Execution latency nằm trong biên cho phép (định nghĩa trước)
- ✅ Log đầy đủ, append-only, audit được

### AUTO v0 **FAIL** nếu xảy ra bất kỳ điều nào:
- ❌ Double execution
- ❌ Execute signal sau TTL
- ❌ Manual override sau auto
- ❌ Thay đổi signal logic để "cho auto chạy đẹp hơn"

---

## 8. Relationship to Anchor (rất quan trọng)

- **Anchor (MPV)** = read-only
- **AUTO v0** = layer bên trên

Mọi so sánh / claim phải ghi rõ:
- "Anchor-based" hay "Auto-based"

> **AUTO v0 does not redefine truth. It demonstrates repeatability.**

---

## 9. Exit Condition (Khi nào AUTO v0 kết thúc)

AUTO v0 kết thúc khi:
1. Có đủ số ngày chạy (ví dụ 10–20 execution)
2. Không vi phạm constraint
3. Evidence đầy đủ

👉 Sau đó mới được phép:
- bàn đến AUTO v1
- bàn đến optimization
- bàn đến scale

---

## 10. One-line summary

> **AUTO v0 proves that a verified signal system can be executed automatically, deterministically, and auditable — without rewriting history.**
