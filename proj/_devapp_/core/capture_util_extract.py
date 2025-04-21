from PIL import Image
import numpy as np

def Extracted_Image1(filepath, savename):
    img = Image.open(filepath)
    img = img.convert("RGBA")  # 알파 채널 추가
    # img.save("test.png", format="PNG")
    
    # 넘파이 배열로 변환
    data = np.array(img)
    
    # 밝기 기준으로 마스크 생성 (아이콘은 밝은 색상)
    # RGB 값의 합이 임계값보다 크면 아이콘으로 판단
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    mask = ((r + g + b) > 200)  # 임계값 조정 가능
    
    # 마스크 적용
    data[:,:,3] = np.where(mask, 255, 0)  # 아이콘 부분만 불투명하게

    # 이미지로 변환 후 저장
    result = Image.fromarray(data)
    result.save(f"{savename}1.png")
    
def Extracted_Image2(filepath, savename):
    # 이미지 열기
    img = Image.open(filepath)
    img = img.convert("RGBA")

    # 넘파이 배열로 변환
    data = np.array(img)

    # 황금색 범위 마스크 생성
    r, g, b = data[:,:,0], data[:,:,1], data[:,:,2]
    # 황금색은 R과 G 채널 값이 높고, B 채널 값이 낮은 특성이 있음
    gold_mask = ((r > 150) & (g > 100) & (b < 100))

    # 마스크 적용
    data[:,:,3] = np.where(gold_mask, 255, 0)

    # 이미지로 변환 후 저장
    result = Image.fromarray(data)
    result.save(f"{savename}2.png")


def Test_Extract():
    filepath1 = "data\\images\\좌상단메뉴-월드맵.png"
    savename1 = "worldmap"
    filepath2 = "data\\images\\좌상단메뉴-마을이동.png"
    savename2 = "homing"
    filepath = filepath2
    savename = savename2
    Extracted_Image1(filepath, savename)
    Extracted_Image2(filepath, savename)