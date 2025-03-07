# C#에서 Newtonsoft.Json을 사용하여 JSON 파일을 저장하는 방법

C#에서 **Newtonsoft.Json**을 사용하여 JSON 파일을 로컬에 저장하는 방법을 설명합니다.

---

## **✅ 1. JObject를 JSON 파일로 저장하는 방법**
`JObject` 또는 `JArray`를 **파일에 저장**하는 방법은 `File.WriteAllText()` 또는 `StreamWriter`를 사용할 수 있습니다.

### **🔹 방법 1: `File.WriteAllText()`를 사용한 저장**
```csharp
using System.IO;
using Newtonsoft.Json.Linq;

static void SaveJsonToFile(string path, JObject json)
{
    File.WriteAllText(path, json.ToString());
}

static void Main()
{
    string path = @"C:\path\to\file.json";

    // 저장할 JSON 객체 생성
    JObject json = new JObject
    {
        ["name"] = "John Doe",
        ["age"] = 30,
        ["city"] = "New York"
    };

    // JSON을 파일로 저장
    SaveJsonToFile(path, json);

    Console.WriteLine("JSON 파일 저장 완료!");
}
```
✅ **장점**:
- 간단하고 빠름
- 기존 파일이 있을 경우 덮어씌움

---

### **🔹 방법 2: `StreamWriter`를 사용한 저장**
```csharp
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

static void SaveJsonToFile(string path, JObject json)
{
    using (StreamWriter file = File.CreateText(path))
    using (JsonTextWriter writer = new JsonTextWriter(file))
    {
        json.WriteTo(writer);
    }
}

static void Main()
{
    string path = @"C:\path\to\file.json";

    JObject json = new JObject
    {
        ["name"] = "John Doe",
        ["age"] = 30,
        ["city"] = "New York"
    };

    SaveJsonToFile(path, json);
    Console.WriteLine("JSON 파일 저장 완료!");
}
```
✅ **장점**:
- `JsonTextWriter`를 사용하여 JSON을 **보다 효율적으로 저장**
- JSON 포맷을 **더 정밀하게 조정 가능**

---

## **✅ 2. JSON을 객체에서 변환하여 저장 (`JsonConvert.SerializeObject`)**
JSON을 C# **객체(Object)** 에서 변환한 후 저장하는 방법도 가능합니다.

```csharp
using System;
using System.IO;
using Newtonsoft.Json;

class Person
{
    public string Name { get; set; }
    public int Age { get; set; }
    public string City { get; set; }
}

static void SaveObjectToJson(string path, object obj)
{
    string json = JsonConvert.SerializeObject(obj, Formatting.Indented);
    File.WriteAllText(path, json);
}

static void Main()
{
    string path = @"C:\path\to\file.json";

    // C# 객체 생성
    Person person = new Person
    {
        Name = "Alice",
        Age = 25,
        City = "Los Angeles"
    };

    // 객체를 JSON으로 변환 후 파일 저장
    SaveObjectToJson(path, person);
    Console.WriteLine("객체를 JSON 파일로 저장 완료!");
}
```
✅ **장점**:
- 객체를 JSON으로 변환 후 저장 가능
- **`Formatting.Indented`** 옵션으로 JSON을 가독성 있게 저장

---

## **✅ 3. JSON을 기존 파일에 추가하는 방법**
이미 존재하는 JSON 파일의 데이터를 수정하거나 새 데이터를 추가하는 경우, JSON을 읽어온 후 **값을 추가하고 다시 저장**하면 됩니다.

```csharp
using System.IO;
using Newtonsoft.Json.Linq;

static void AddToJsonFile(string path, string key, string value)
{
    // 기존 JSON 로드
    JObject json;
    if (File.Exists(path))
    {
        using (StreamReader file = File.OpenText(path))
        using (JsonTextReader reader = new JsonTextReader(file))
        {
            json = (JObject)JToken.ReadFrom(reader);
        }
    }
    else
    {
        json = new JObject();
    }

    // 새로운 데이터 추가
    json[key] = value;

    // 다시 저장
    File.WriteAllText(path, json.ToString());
}

static void Main()
{
    string path = @"C:\path\to\file.json";
    AddToJsonFile(path, "new_key", "new_value");

    Console.WriteLine("JSON 파일에 데이터 추가 완료!");
}
```
✅ **장점**:
- 기존 JSON 파일을 유지하면서 데이터 추가 가능
- 파일이 없으면 자동으로 생성됨

---

## **🚀 최종 정리**
| 목적 | 사용 방법 |
|------|-----------|
| **JSON을 파일로 저장 (JObject)** | `File.WriteAllText(json.ToString())` |
| **JSON을 StreamWriter로 저장** | `json.WriteTo(JsonTextWriter)` |
| **객체(Object)를 JSON으로 변환 후 저장** | `JsonConvert.SerializeObject(obj, Formatting.Indented)` |
| **JSON 파일에 새로운 값 추가** | JSON을 읽어온 후 수정 후 다시 저장 |

🚀 **이제 C#에서 JSON 파일을 자유롭게 저장하고 관리할 수 있습니다!** 😊