# WinForms에서 UniRx 및 UniTask 적용하기

WinForms에서 **UniRx**와 **UniTask**를 적용하면 **반응형 프로그래밍**과 **비동기 처리**를 효율적으로 사용할 수 있습니다. 기본적으로 WinForms는 `Reactive Extensions (Rx)` 패턴을 지원하지 않지만, UniRx를 활용하면 **이벤트 기반 프로그래밍**을 더욱 편리하게 관리할 수 있으며, UniTask를 사용하면 `async/await` 기반의 **비동기 작업을 최적화**할 수 있습니다.

---

## ✅ UniRx와 UniTask 설치 방법
WinForms 프로젝트에서 **NuGet 패키지를 설치**해야 합니다.

### **🔹 NuGet 패키지 설치 (Visual Studio)**
```powershell
Install-Package UniRx
Install-Package Cysharp.Threading.Tasks
```

---

## ✅ UniRx 적용: WinForms에서 반응형 프로그래밍
WinForms의 이벤트를 `UniRx`를 사용하여 반응형으로 처리할 수 있습니다.

### **📌 예제 1: 버튼 클릭 이벤트를 `UniRx`로 처리**
```csharp
using System;
using System.Reactive.Linq;
using System.Windows.Forms;
using UniRx;

public class MainForm : Form
{
    private Button button;
    private Label label;

    public MainForm()
    {
        button = new Button { Text = "클릭!", Location = new System.Drawing.Point(10, 10) };
        label = new Label { Text = "상태: 대기 중", Location = new System.Drawing.Point(10, 50), AutoSize = true };

        Controls.Add(button);
        Controls.Add(label);

        // 버튼 클릭 이벤트를 UniRx 스트림으로 변환
        Observable.FromEventPattern(button, nameof(button.Click))
            .Subscribe(_ => label.Text = "버튼이 클릭됨!");

        // 타이머 예제 (1초마다 "업데이트" 출력)
        Observable.Interval(TimeSpan.FromSeconds(1))
            .Subscribe(_ => Console.WriteLine("업데이트..."))
            .AddTo(this); // 폼이 닫힐 때 자동 해제
    }
}
```

---

## ✅ UniTask 적용: 비동기 처리
UniTask를 사용하면 `async/await`를 더 깔끔하게 사용할 수 있습니다.

### **📌 예제 2: 버튼 클릭 시 비동기 작업 실행**
```csharp
using System;
using System.Windows.Forms;
using Cysharp.Threading.Tasks;
using System.Threading.Tasks;

public class MainForm : Form
{
    private Button button;
    private Label label;

    public MainForm()
    {
        button = new Button { Text = "비동기 실행", Location = new System.Drawing.Point(10, 10) };
        label = new Label { Text = "대기 중...", Location = new System.Drawing.Point(10, 50), AutoSize = true };

        Controls.Add(button);
        Controls.Add(label);

        button.Click += async (sender, e) => await RunAsyncTask();
    }

    private async UniTask RunAsyncTask()
    {
        label.Text = "작업 진행 중...";
        await UniTask.Delay(TimeSpan.FromSeconds(2)); // 2초 대기
        label.Text = "작업 완료!";
    }
}
```

---

## ✅ UniRx + UniTask 결합
UniRx와 UniTask를 결합하면 더욱 유용한 비동기 처리를 할 수 있습니다.

### **📌 예제 3: 버튼 클릭 후 비동기 작업 실행**
```csharp
using System;
using System.Windows.Forms;
using Cysharp.Threading.Tasks;
using UniRx;

public class MainForm : Form
{
    private Button button;
    private Label label;

    public MainForm()
    {
        button = new Button { Text = "비동기 + Rx 실행", Location = new System.Drawing.Point(10, 10) };
        label = new Label { Text = "대기 중...", Location = new System.Drawing.Point(10, 50), AutoSize = true };

        Controls.Add(button);
        Controls.Add(label);

        // Rx 이벤트 스트림에서 비동기 작업 실행
        Observable.FromEventPattern(button, nameof(button.Click))
            .Subscribe(async _ => await RunAsyncTask())
            .AddTo(this);
    }

    private async UniTask RunAsyncTask()
    {
        label.Text = "비동기 작업 시작...";
        await UniTask.Delay(TimeSpan.FromSeconds(3));
        label.Text = "작업 완료!";
    }
}
```

---

## ✅ WinForms 컨트롤의 UI 업데이트 문제 해결
WinForms의 UI는 **메인 스레드(UI 스레드)에서만 업데이트 가능**합니다.
만약 **비동기 작업에서 UI를 업데이트해야 한다면 `UniTask.SwitchToMainThread()`를 사용**하면 됩니다.

✔ **📌 예제 4: 비동기 작업 후 UI 업데이트**
```csharp
private async UniTask RunAsyncTask()
{
    label.Text = "비동기 작업 중...";

    // 백그라운드 작업 (CPU 작업 시)
    await UniTask.RunOnThreadPool(() =>
    {
        Task.Delay(2000).Wait(); // 2초 대기 (실제 CPU 연산 처리 가능)
    });

    // UI 업데이트를 위해 메인 스레드로 복귀
    await UniTask.SwitchToMainThread();
    label.Text = "작업 완료!";
}
```

---

## 🎯 결론
| 기능 | 적용 방법 |
|

