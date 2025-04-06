# C#에서 PC 고유 값 생성 및 실행 제한 방법

C#에서 특정 PC에 대한 고유 값을 생성하여, **다른 PC에서 실행될 경우 제한을 거는 방법**을 설명합니다.

---

## **🚀 1. PC 고유 값 생성**
PC 고유 값을 얻기 위해 **CPU 정보, BIOS Serial Number, 하드디스크 ID, MAC 주소** 등을 조합하여 **HWID(하드웨어 ID)** 를 생성합니다.

### **1.1 CPU ID 가져오기**
```csharp
using System;
using System.Management;

static string GetCpuId()
{
    string cpuId = "";
    ManagementClass mc = new ManagementClass("Win32_Processor");
    ManagementObjectCollection moc = mc.GetInstances();
    foreach (ManagementObject mo in moc)
    {
        cpuId = mo.Properties["ProcessorId"].Value.ToString();
        break;
    }
    return cpuId;
}
```

### **1.2 BIOS Serial Number 가져오기**
```csharp
static string GetBiosSerialNumber()
{
    string biosSerial = "";
    ManagementClass mc = new ManagementClass("Win32_BIOS");
    ManagementObjectCollection moc = mc.GetInstances();
    foreach (ManagementObject mo in moc)
    {
        biosSerial = mo.Properties["SerialNumber"].Value.ToString();
        break;
    }
    return biosSerial;
}
```

### **1.3 하드디스크 Serial Number 가져오기**
```csharp
static string GetHddSerialNumber()
{
    string serial = "";
    ManagementObjectSearcher mos = new ManagementObjectSearcher("SELECT * FROM Win32_DiskDrive");
    foreach (ManagementObject mo in mos.Get())
    {
        serial = mo["SerialNumber"].ToString().Trim();
        break;
    }
    return serial;
}
```

### **1.4 MAC 주소 가져오기**
```csharp
using System.Net.NetworkInformation;

static string GetMacAddress()
{
    foreach (NetworkInterface nic in NetworkInterface.GetAllNetworkInterfaces())
    {
        if (nic.OperationalStatus == OperationalStatus.Up)
        {
            return nic.GetPhysicalAddress().ToString();
        }
    }
    return string.Empty;
}
```

---

## **🚀 2. HWID(고유 값) 생성 및 해싱 (SHA256)**
```csharp
using System;
using System.Security.Cryptography;
using System.Text;

static string GenerateHardwareId()
{
    string rawData = GetCpuId() + "-" + GetBiosSerialNumber() + "-" + GetHddSerialNumber() + "-" + GetMacAddress();
    using (SHA256 sha256 = SHA256.Create())
    {
        byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(rawData));
        StringBuilder builder = new StringBuilder();
        foreach (byte b in bytes)
        {
            builder.Append(b.ToString("x2"));
        }
        return builder.ToString();
    }
}
```
✅ **결과 예시**:
```
PC 고유 해시 값: 3eebfb8f8d3f1b4c7e6b4a3a997cf7aaad4b2d4f8cb2d5ea7a6c5b2f8d4f
```

---

## **🚀 3. 실행 제한 적용 방법**
### **3.1 HWID를 파일에 저장하고 검증**
```csharp
using System.IO;

static void ValidatePc()
{
    string hardwareId = GenerateHardwareId();
    string filePath = "C:\\ProgramData\\app_hwid.txt"; // HWID 저장 경로

    if (File.Exists(filePath))
    {
        string storedId = File.ReadAllText(filePath);
        if (storedId != hardwareId)
        {
            Console.WriteLine("🚫 이 PC에서는 실행할 수 없습니다!");
            Environment.Exit(0);
        }
    }
    else
    {
        File.WriteAllText(filePath, hardwareId);
        Console.WriteLine("✅ PC 등록 완료.");
    }
}
```

✅ **이제 처음 실행한 PC에서만 실행 가능하며, 다른 PC에서는 실행이 차단됩니다.**

---

## **🚀 4. 클라우드 서버에서 HWID 인증 (고급 방법)**
HWID를 **서버에 등록하고 실행 시 서버에서 인증**하는 방법도 가능합니다.

### **클라이언트 → 서버 전송 코드**
```csharp
using System.Net.Http;
using System.Threading.Tasks;

static async Task<bool> VerifyHwIdOnline(string hwid)
{
    HttpClient client = new HttpClient();
    HttpResponseMessage response = await client.GetAsync($"https://myserver.com/api/verify?hwid={hwid}");
    return response.IsSuccessStatusCode;
}
```

✅ **이 방법을 사용하면 HWID를 서버에서 관리하여 보안성을 강화할 수 있습니다.**

---

## **🚀 5. 최종 정리**
| 방법 | 보안성 | 변경 가능성 | 추천 상황 |
|------|------|------|------|
| CPU + BIOS + HDD + MAC 주소 조합 | ✅ 높음 | ❌ 하드웨어 변경 시 바뀜 | 강력한 인증 필요할 때 |
| MAC 주소 기반 | ❌ 낮음 | ❌ 네트워크 카드 변경 시 바뀜 | 간단한 PC 인증 |
| HWID 저장 후 검증 | ✅ 높음 | ❌ 파일 삭제 시 초기화 | 소프트웨어 실행 제한 |
| 서버 기반 인증 | ✅ 최고 | ❌ 하드웨어 변경 시 다시 등록 필요 | 강력한 라이선스 관리 |

✅ **가장 강력한 보안이 필요한 경우** → **서버 인증 방식**
✅ **빠르고 간단한 PC 인증이 필요하면** → **BIOS + CPU + HDD 기반 HWID**
✅ **파일 기반으로 제한하려면** → **C:\ProgramData에 HWID 저장 후 검증**

🚀 **이제 특정 PC에서만 프로그램을 실행할 수 있습니다!** 😊
