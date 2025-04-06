"""
설정 관리 모듈 - INI 파일을 통한 설정 저장 및 로드
"""

import os
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox
from zzz.config import SETTINGS_FILE

class SettingsManager:
    """설정 관리 클래스"""
    
    def __init__(self, default_values=None):
        """
        설정 관리자 초기화
        
        Args:
            default_values (dict): 기본 설정값 딕셔너리
        """
        self.config = configparser.ConfigParser()
        self.settings_file = SETTINGS_FILE
        self.default_values = default_values or {}
        
        # 사용자 AppData 디렉토리에 설정 파일 저장 (권한 문제 해결)
        appdata_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ShowMeTheMoney', 'LORDNINE')
        
        # 폴더가 없으면 생성
        if not os.path.exists(appdata_path):
            try:
                os.makedirs(appdata_path)
            except Exception as e:
                print(f"AppData 디렉토리 생성 중 오류: {str(e)}")
        
        # 설정 파일 전체 경로 설정
        self.settings_path = os.path.join(appdata_path, self.settings_file)
        
        # 설정 로드 (파일이 없으면 기본값 사용)
        self.load_settings()
    
    def load_settings(self):
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
        if 'General' not in self.config:
            self.config['General'] = {}
        
        # 테서렉트 섹션 확인
        if 'Tesseract' not in self.config:
            self.config['Tesseract'] = {}
        
        return False
    
    def save_settings(self):
        """설정 파일 저장"""
        try:
            # 설정 파일 디렉토리가 있는지 확인
            settings_dir = os.path.dirname(self.settings_path)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
                
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            print(f"설정 파일 저장 완료: {self.settings_path}")
            return True
        except Exception as e:
            print(f"설정 파일 저장 중 오류 발생: {str(e)}")
            return False
    
    def get(self, section, key, default=None):
        """
        설정값 가져오기
        
        Args:
            section (str): 섹션명
            key (str): 키
            default: 기본값 (설정이 없을 경우 반환)
            
        Returns:
            설정값 또는 기본값
        """
        try:
            if section in self.config and key in self.config[section]:
                return self.config[section][key]
            return default
        except:
            return default
    
    def set(self, section, key, value):
        """
        설정값 저장
        
        Args:
            section (str): 섹션명
            key (str): 키
            value: 저장할 값
            
        Returns:
            bool: 성공 여부
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = str(value)
            return True
        except:
            return False
    
    def prompt_tesseract_path(self, parent=None):
        """
        테서렉트 OCR 경로 사용자 입력 요청
        
        Args:
            parent: 부모 윈도우 (tkinter)
            
        Returns:
            str: 선택된 테서렉트 경로 또는 None (취소 시)
        """
        # 현재 설정된 경로 가져오기
        current_path = self.get('Tesseract', 'Path', '')
        
        # 파일 선택 다이얼로그
        file_path = filedialog.askopenfilename(
            title="Tesseract OCR 실행 파일 선택",
            filetypes=[("실행 파일", "*.exe"), ("모든 파일", "*.*")],
            initialfile="tesseract.exe",
            parent=parent
        )
        
        if file_path:
            # 경로 저장
            self.set('Tesseract', 'Path', file_path)
            self.save_settings()
            return file_path
        
        return None
    
    def check_tesseract_path(self, parent=None):
        """
        테서렉트 OCR 경로 확인 및 없으면 사용자 입력 요청
        
        Args:
            parent: 부모 윈도우 (tkinter)
            
        Returns:
            str: 테서렉트 경로 또는 None (취소 시)
        """
        # 저장된 테서렉트 경로 가져오기
        tesseract_path = self.get('Tesseract', 'Path', '')
        
        # 경로가 없거나 파일이 존재하지 않으면 사용자에게 요청
        if not tesseract_path or not os.path.exists(tesseract_path):
            # 안내 메시지 표시
            messagebox.showinfo(
                "Tesseract OCR 설정",
                "Tesseract OCR 실행 파일을 선택해주세요.\n"
                "(Tesseract-OCR 설치 디렉토리 내의 tesseract.exe)\n\n"
                "아직 설치하지 않았다면 다음 링크에서 설치할 수 있습니다:\n"
                "https://github.com/UB-Mannheim/tesseract/wiki",
                parent=parent
            )
            
            # 파일 선택 다이얼로그
            tesseract_path = self.prompt_tesseract_path(parent)
            
            if not tesseract_path:
                messagebox.showwarning(
                    "경고",
                    "Tesseract OCR 경로가 설정되지 않았습니다.\n"
                    "OCR 기능을 사용하려면 설정이 필요합니다.",
                    parent=parent
                )
                return None
        
        return tesseract_path