# Windows에 알림(Notification)을 보내는 방법

C#에서 Windows에 **알림(Notification)** 을 보내는 방법은 여러 가지가 있습니다. 아래에서 대표적인 방법을 소개합니다.

---

## **🚀 1. Windows 10+ Toast Notification (최신 방식)**
Windows 10 이상에서는 **Windows.UI.Notifications** 네임스페이스를 사용하여 **토스트 알림(Toast Notification)** 을 보낼 수 있습니다.

### **📌 Toast Notification을 사용하려면 NuGet 패키지 설치 필요**
먼저 **Windows Community Toolkit - Notifications** 패키지를 설치해야 합니다.

1. **NuGet에서 설치**
   ```
   Install-Package Microsoft.Toolkit.Uwp.Notifications
   ```
2. **또는 Visual Studio에서 NuGet 패키지 매니저를 열고**  
   `Microsoft.Toolkit.Uwp.Notifications` 검색 후 설치

### **✅ C# 코드 (Toast Notification)**
```csharp
using Microsoft.Toolkit.Uwp.Notifications; // NuGet 패키지 필요

class Program
{
    static void Main()
    {
        new ToastContentBuilder()
            .AddText("Windows 알림 테스트")
            .AddText("이것은 C#에서 보낸 알림입니다.")
            .Show();

        Console.WriteLine("알림이 전송되었습니다!");
    }
}
```

✅ **장점**:
- Windows 10 이상의 **알림 센터**에 저장됨
- **UI가 깔끔하고 가독성 좋음**
- 버튼/이미지/링크 추가 가능

❌ **단점**:
- Windows 7, 8에서는 작동하지 않음

---

## **🚀 2. NotifyIcon을 사용한 트레이 알림 (Windows 7 이상 지원)**
Windows 7과 8에서도 **트레이 아이콘(Notification Area)** 을 활용하면 **풍선(Balloon Tip) 알림**을 보낼 수 있습니다.

### **✅ C# 코드 (NotifyIcon 알림)**
```csharp
using System;
using System.Drawing;
using System.Windows.Forms;

class Program
{
    static void Main()
    {
        NotifyIcon notifyIcon = new NotifyIcon()
        {
            Icon = SystemIcons.Information, // 기본 아이콘 설정
            Visible = true // 트레이 아이콘 보이게 설정
        };

        notifyIcon.ShowBalloonTip(3000, "알림 제목", "C#에서 보낸 Windows 알림입니다.", ToolTipIcon.Info);
        
        Console.WriteLine("알림이 전송되었습니다!");

        System.Threading.Thread.Sleep(5000); // 알림이 사라질 때까지 실행 유지

        notifyIcon.Dispose(); // 알림 종료 후 아이콘 제거
    }
}
```

✅ **장점**:
- **Windows 7 이상에서 동작**
- 간단한 코드로 사용 가능
- Windows 10/11에서도 **트레이 아이콘이 필요한 경우 유용**

❌ **단점**:
- Windows 알림 센터에 저장되지 않음
- **앱이 실행 중이어야 알림을 볼 수 있음**

---

## **🚀 3. PowerShell을 활용한 Windows 알림 (외부 실행)**
C#에서 PowerShell 명령을 실행하여 Windows 알림을 보낼 수도 있습니다.

### **✅ C# 코드 (PowerShell 실행)**
```csharp
using System;
using System.Diagnostics;

class Program
{
    static void Main()
    {
        string message = "C#에서 보낸 Windows 알림입니다.";
        string title = "알림 제목";

        string command = $"powershell -Command \"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; " +
                         "$template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02; " +
                         "$toastXml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template); " +
                         "$textNodes = $toastXml.GetElementsByTagName('text'); " +
                         "$textNodes.Item(0).AppendChild($toastXml.CreateTextNode('{title}')) | Out-Null; " +
                         "$textNodes.Item(1).AppendChild($toastXml.CreateTextNode('{message}')) | Out-Null; " +
                         "$toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml); " +
                         "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('C# App').Show($toast);\"";

        Process.Start("cmd.exe", "/C " + command);
        
        Console.WriteLine("PowerShell을 통해 알림이 전송되었습니다!");
    }
}
```

✅ **장점**:
- **C#에서 외부 프로세스로 Windows 알림을 트리거 가능**
- 앱 설치 없이 PowerShell로 실행 가능

❌ **단점**:
- **PowerShell 실행 권한이 필요할 수 있음**
- **보안 경고가 뜰 수도 있음**

---

## **🚀 4. 어떤 방법을 선택해야 할까?**
| 방법 | 지원 OS | Windows 알림 센터 저장 | 간단한 코드 | 사용 추천 상황 |
|------|------|------------------|--------------|--------------|
| **Toast Notification (최신)** | Win10+ | ✅ 저장됨 | ✅ | Windows 10 이상, UI가 중요할 때 |
| **NotifyIcon (트레이 알림)** | Win7+ | ❌ | ✅ | Windows 7 이상, 간단한 알림 필요할 때 |
| **PowerShell 실행** | Win10+ | ✅ | ❌ | 앱 설치 없이 빠르게 알림을 보낼 때 |

---

## **🎯 결론**
1. **Windows 10 이상**에서 공식적인 알림을 원하면  
   → **`Microsoft.Toolkit.Uwp.Notifications` (Toast Notification) 사용**  
2. **Windows 7+에서도 지원되는 간단한 알림**이 필요하면  
   → **`NotifyIcon` (트레이 아이콘 + 풍선 알림) 사용**  
3. **빠르게 알림을 보내고 싶다면**  
   → **PowerShell 실행 방식 사용**  

🚀 **이제 Windows에 알림을 쉽게 보낼 수 있습니다!** 😊
