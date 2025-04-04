# generate_version_info.py
import os

# 버전 정보를 한 곳에서 관리
VERSION = "0.0.203"
VERSION_PARTS = VERSION.split('.')

# 버전 정보 파일 생성 함수
def generate_version_info():
    version_info_template = f'''# VSVersionInfo
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=({VERSION_PARTS[0]}, {VERSION_PARTS[1]}, {VERSION_PARTS[2]}, 0),
        prodvers=({VERSION_PARTS[0]}, {VERSION_PARTS[1]}, {VERSION_PARTS[2]}, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                u'040904B0',
                [
                    StringValue(u'CompanyName', u'로드나인'),
                    StringValue(u'FileDescription', u'쇼 미더 머니 자동화 도구'),
                    StringValue(u'FileVersion', u'{VERSION}'),
                    StringValue(u'InternalName', u'RUNNER'),
                    StringValue(u'LegalCopyright', u'© 2024 로드나인'),
                    StringValue(u'OriginalFilename', u'RUNNER-로드나인.exe'),
                    StringValue(u'ProductName', u'쇼 미더 머니 자동화 도구'),
                    StringValue(u'ProductVersion', u'{VERSION}')
                ]
            )
        ]),
        VarFileInfo([VarValue(u'Translation', [1033, 1200])])
    ]
)'''

    # version_info 파일 생성
    with open('version_info', 'w', encoding='utf-8') as f:
        f.write(version_info_template)

# 스크립트로 직접 실행할 때
if __name__ == '__main__':
    generate_version_info()
    print(f"Version info file generated for version {VERSION}")