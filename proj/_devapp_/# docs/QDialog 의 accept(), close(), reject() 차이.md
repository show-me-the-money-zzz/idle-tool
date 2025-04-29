# QDialog: accept(), close(), reject() 차이 정리

## ✨ 개관
`QDialog` 에서 `accept()`, `close()`, `reject()`는 다양한 의미가 있으며, 각각 다른 상황에 맞춰 사용됩니다.

---

## ✨ 요약 비교

| 항목 | `accept()` | `close()` | `reject()` |
|------|------------|-----------|------------|
| 의미 | **"확인/성공적으로 완료"** | 그냥 창을 닫음 (성공/실패 의미 없음) | **"취소 또는 명시적 실패"** |
| 리턴 코드 | `QDialog.Accepted` | `QDialog.Rejected` (또는 마지막 상태) | `QDialog.Rejected` |
| `exec()`와 연동 | ✔️ | ✔️ | ✔️ |
| 용도 | 확인, 저장 완료 | 일반 닫기, 무시 | 명시적 취소, 실패 처리 |
| 연결 함수 | OK 버튼, 확인 버튼 | Cancel 버튼, X 버튼 | Cancel 버튼, 취소 이벤트 |

---

## ✨ 동작 환경

### `accept()`
- 다이얼로그를 **성공적으로 완료**한 것으로 간주합니다.
- `exec()` 호출 시 반환값을 **`QDialog.Accepted`**로 설정합니다.

### `close()`
- 단순히 창을 닫는 동작입니다.
- `exec()` 호출 중이라면 기본적으로 **`QDialog.Rejected`**로 간주됩니다.

### `reject()`
- 명시적으로 **취소**나 **실패**를 의미합니다.
- `exec()` 호출 중이라면 항상 **`QDialog.Rejected`** 반환합니다.

---

## ✨ 실사 예시

```python
dialog = MyDialog()
result = dialog.exec()

if result == QDialog.Accepted:
    print("✔️ 사용자 완료")
else:
    print("❌ 사용자 취소 또는 닫기")
```

- `dialog.accept()` 호출 → `Accepted` 반환
- `dialog.close()` 호출 → `Rejected` 반환
- `dialog.reject()` 호출 → `Rejected` 반환 (명시적 취소)

---

## ✨ 실전 사용 예

| 상황 | 호출할 메서드 |
|------|---------------|
| "저장 완료" 버튼 클릭 | `accept()` |
| "취소" 버튼 클릭 | `reject()` 또는 `close()` |
| X 버튼 클릭 (타이틀바) | `close()` (기본 연결) |

---

## ✨ 추가 정보

- `reject()`는 항상 명시적으로 "취소" 의미를 전달할 때 사용합니다.
- `close()`는 취소든 무시든 일반적인 닫기를 처리합니다.
- `accept()`는 성공적인 완료를 명시합니다.

---

# ✨ 종합 결론

**다음을 기준으로 사용하세요:**

> 완료를 확인하고 종료할 경우 → `accept()` 호출
>
> 단순히 닫거나 취소할 경우 → `close()` 또는 `reject()` 호출
>
> 취소를 명시하고 싶으면 → `reject()` 호출

✨