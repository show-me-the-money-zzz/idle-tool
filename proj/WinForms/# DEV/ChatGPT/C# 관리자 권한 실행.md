# C#에서 코드 상에서 관리자 권한 요청하는 방법

C#에서는 코드 상에서 **관리자 권한을 직접 부여할 수는 없지만**, **관리자 권한으로 실행되도록 자동 요청하는 방법**은 가능합니다. 아래는 대표적인 해결 방법들입니다.

---

## **✅ 방법 1: `app.manifest` 파일을 사용하여 관리자 권한 요청**

### **1️⃣ `app.manifest` 파일 추가**
1. **Visual Studio에서 `app.manifest` 파일을 추가**
   - **Solution Explorer**에서 `프로젝트 > 마우스 우클릭 > Add > New Item`
   - `Application Manifest File` 추가 (`app.manifest`)

2. **`app.manifest` 파일을 수정하여 관리자 권한 요청**
   ```xml
   <requestedExecutionLevel level="requireAdministrator" uiAccess="false" />
   ```
   - `level="requireAdministrator"` : 프로그램이 실행될 때 **관리자 권한 요청**
   - `uiAccess="false"` : UI 권한 상승을 허용하지 않음

✅ **장점**:
- 사용자가 프로그램을 실행할 때 **자동으로 관리자 권한 요청**됨
- 프로그램 실행 시 **UAC(User Account Control) 팝업이 뜸**

❌ **단점**:
- **항상 관리자 권한이 필요함**, 일반 사용자 모드에서는 실행 불가

---

## **✅ 방법 2: `Process.Start`를 사용하여 관리자 권한으로 다시 실행**
관리자 권한이 없는 경우, **현재 실행된 프로그램을 종료하고 관리자 권한으로 다시 실행**할 수 있습니다.

```csharp
using System;
using System.Diagnostics;
using System.Security.Principal;

class Program
{
    static void Main()
    {
        if (!IsAdministrator())
        {
            // 현재 관리자 권한이 아니라면, 관리자 권한으로 재실행
            RestartAsAdmin();
        }
        else
        {
            Console.WriteLine("관리자 권한으로 실행되었습니다.");
        }
    }

    static bool IsAdministrator()
    {
        using (WindowsIdentity identity = WindowsIdentity.GetCurrent())
        {
            WindowsPrincipal principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }
    }

    static void RestartAsAdmin()
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = Process.GetCurrentProcess().MainModule.FileName,
            UseShellExecute = true,
            Verb = "runas" // 관리자 권한으로 실행
        };

        try
        {
            Process.Start(startInfo);
            Environment.Exit(0); // 기존 프로세스 종료
        }
        catch
        {
            Console.WriteLine("관리자 권한 실행이 취소되었습니다.");
        }
    }
}
```

✅ **장점**:
- 코드에서 관리자 권한을 확인하고, 없을 경우 자동으로 **관리자 권한으로 다시 실행**
- **관리자 권한이 필요할 때만 요청**

❌ **단점**:
- 처음 실행 시에는 관리자 권한 없이 실행되므로, **권한이 필요한 기능이 실행되기 전에 체크해야 함**
- UAC 팝업이 나타남 (자동 승인은 불가)

---

## **✅ 방법 3: `Task Scheduler`를 사용하여 관리자 권한 없이 실행**

### **1️⃣ 관리자 권한으로 실행되는 작업 생성**
- `taskschd.msc` 실행 (작업 스케줄러 열기)
- **새 작업(Task) 추가** → "관리자 권한으로 실행" 체크
- `C:\path\to\yourapp.exe` 경로를 실행하도록 설정
- 작업 이름을 예: `"MyAdminTask"` 로 지정

### **2️⃣ C# 코드에서 작업 실행**
```csharp
using System.Diagnostics;

class Program
{
    static void Main()
    {
        Process.Start("schtasks", "/run /tn \"MyAdminTask\"");
    }
}
```

✅ **장점**:
- **UAC 팝업 없이** 관리자 권한 실행 가능
- 사용자가 별도 권한 상승 없이 실행 가능

❌ **단점**:
- 처음 한 번은 **수동으로 작업을 등록해야 함**
- 작업 스케줄러를 사용하지 않는 환경에서는 실행 불가

---

## **🚀 최종 정리**
| 방법 | UAC 팝업 | 일반 실행 가능 | 추가 설정 필요 |
|------|---------|-------------|-------------|
| **`app.manifest` 수정** | ✅ 있음 | ❌ 관리자 권한 필수 | 🔹 필요 |
| **`Process.Start`로 재실행** | ✅ 있음 | ✅ 가능 | ❌ 불필요 |
| **Task Scheduler 사용** | ❌ 없음 | ✅ 가능 | 🔹 필요 |

✅ **가장 쉬운 방법**: `Process.Start`로 관리자 권한 요청  
✅ **완전 자동 실행 (UAC 없이)**: Task Scheduler 사용  
✅ **항상 관리자 실행 필요**: `app.manifest` 수정  

🚀 **권한 문제가 발생하는 코드에서는 `Process.Start`로 관리자 권한을 다시 요청하는 방법이 가장 추천됩니다!** 😊
