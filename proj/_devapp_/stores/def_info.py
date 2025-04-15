HP = -1
MP = -1

POTION = -1
Is_Potion0 = -1

Locate_Kind = ""
Locate_Name = ""

def Update_Value(key, text):
    # print(f"{key}: {text}")
    # return

    text = text.replace("\n", "").replace("\r", "")  # 줄바꿈 제거
    
    match key:
        case "스탯:피통": _Set_HP(text)
        case "스탯:마나통": _Set_MP(text)
        case "스탯:물약": _Set_Potion(text)
        # case "스탯:물약-엥꼬": Is_Potion0 = 0
        
        case "지역:종류":
            global Locate_Kind
            Locate_Kind = text
            # print(f"Locate_Kind= {Locate_Kind}")
        case "지역:이름":
            global Locate_Name
            Locate_Name = text
            # print(f"Locate_Name= {Locate_Name}")

def Update_Values(key, textlist):
    text = ""
    if "스탯:피통" == key or "스탯:마나통" == key:
        text = textlist[0]
    else:
        text = " ".join(textlist)
        
    Update_Value(key, text)


def _Set_HP(text):
    global HP
    HP = _Parse_Vital("HP", text)
    # print(f"HP= {HP}")
    
def _Set_MP(text):
    global MP
    MP = _Parse_Vital("MP", text)
    # print(f"MP= {MP}")
    
def _Set_Potion(text):
    global POTION
    try:
        strvar = text.replace(",", "").replace(".", "")
        POTION = int(strvar)
    except Exception as e:
        POTION = -1;
    # print(f"POTION= {POTION}")

def _Parse_Vital(kind, text):
    if text:
        try:
            # 문자열 분리 및 정리
            curr = text.split("/")[0].strip()  # 왼쪽 값 (현재 HP)
            curr = curr.replace(",", "").replace(".", "")

            # 숫자로 변환
            return int(curr)

        except Exception as e:
            # print(f"[kind] 입력값 '{strValue}' 처리 실패: {e}")
            return -1
    else: return -1