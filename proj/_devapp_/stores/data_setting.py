import os
import configparser

from grinder_utils import finder, system

class DataSettingManager:
    FILE_NAME = "data_settings.ini"
    SECTION_GENERAL = "General"
    
    def __init__(self, default_values=None):
        self.config = configparser.ConfigParser()
        self.settings_file = DataSettingManager.FILE_NAME
        self.default_values = default_values or {}
        
        path = finder.Get_DataPath()
        
        # 폴더가 없으면 생성
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                print(f"Data 디렉토리 생성 중 오류: {str(e)}")
        
        # 설정 파일 전체 경로 설정
        self.settings_path = os.path.join(path, self.settings_file)
        
        # 설정 로드 (파일이 없으면 기본값 사용)
        self._load()
        
    def _load(self):
        """설정 파일 로드"""
        # 파일이 존재하면 로드
        if os.path.exists(self.settings_path):
            try:
                self.config.read(self.settings_path, encoding='utf-8')
                return True
            except Exception as e:
                print(f"설정 파일 로드 중 오류 발생: {str(e)}")
                return False
        
        # 파일이 없으면 기본 섹션 생성
        if DataSettingManager.SECTION_GENERAL not in self.config:
            self.config[DataSettingManager.SECTION_GENERAL] = {}
        
        return False
    
    def _save(self):
        """설정 파일 저장"""
        try:
            # 설정 파일 디렉토리가 있는지 확인
            settings_dir = os.path.dirname(self.settings_path)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
                
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            system.PrintDEV(f"데이터 설정 파일 저장 완료: {self.settings_path}")
            return True
        except Exception as e:
            print(f"설정 파일 저장 중 오류 발생: {str(e)}")
            return False
        
    def get(self, section, key, default=None):
        try:
            if section in self.config and key in self.config[section]:
                return self.config[section][key]
            return default
        except:
            return default
        
    def set(self, section, key, value):
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = str(value)
            return True
        except:
            return False
        
    KEY_GENERAL_RESOLUTION = "resolution"
    def Get_General(self, key, default=None):
        return self.get(DataSettingManager.SECTION_GENERAL, key, default)
    def Get_Resolution(self):
        resolution = self.get(DataSettingManager.SECTION_GENERAL, DataSettingManager.KEY_GENERAL_RESOLUTION, default=None)
        if None == resolution:
            return None
        resolarr = resolution.split("x") #Set_Resolution에서 사용한 구분자
        ret = [ int(resolarr[0]), int(resolarr[1]) ]
        return ret

    def Set_Resolution(self, width, height):
        val = f"{width}x{height}"
        if self.set(DataSettingManager.SECTION_GENERAL, DataSettingManager.KEY_GENERAL_RESOLUTION, val):
            if self._save():
                return True
        return False
    
DataSetting = DataSettingManager()