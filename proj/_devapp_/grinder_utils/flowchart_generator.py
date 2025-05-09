from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
                              QListWidget, QSplitter, QWidget, QScrollArea)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
import json
import os

class FlowchartGenerator:
    """태스크 데이터를 기반으로 Mermaid 흐름도 코드를 생성하는 클래스"""
    
    @staticmethod
    def generate_mermaid_code(task_name, task_data):
        """태스크의 흐름도를 Mermaid 문법으로 생성"""
        
        # if not task_data or not task_data.get('steps'):
        if not task_data or not task_data.steps:
            return "flowchart TD\n    A[태스크 데이터 없음]"
        
        # steps = task_data.get('steps', {})
        # start_key = task_data.get('start_key', '')
        steps = task_data.steps
        start_key = task_data.start_key
        
        mermaid_code = ["flowchart TD"]
        step_ids = {}  # 단계 키를 ID로 매핑
        
        # 각 단계에 대한 노드 ID 생성
        for i, key in enumerate(steps.keys()):
            step_ids[key] = f"step{i+1}"
            
            # 노드 텍스트 준비
            node_text = key.replace('-', '\\-')  # Mermaid 문법에 맞게 하이픈 이스케이프
            
            # 시작 노드는 특별한 스타일 적용
            if key == start_key:
                mermaid_code.append(f"    {step_ids[key]}[\"{node_text}\"] :::startNode")
            else:
                mermaid_code.append(f"    {step_ids[key]}[\"{node_text}\"]")
        
        # 연결선 추가
        for key, step in steps.items():
            from_id = step_ids[key]
            
            # 다음 단계 연결
            # for next_step in step.get('next_step', []):
            for next_step in step.next_step:
                if next_step in step_ids:
                    to_id = step_ids[next_step]
                    mermaid_code.append(f"    {from_id} --> {to_id}")
            
            # 실패 단계 연결
            # fail_step = step.get('fail_step', '')
            fail_step = step.fail_step
            if fail_step and fail_step in step_ids:
                to_id = step_ids[fail_step]
                mermaid_code.append(f"    {from_id} -- 실패 --> {to_id} :::failLink")
        
        # 스타일 정의 추가
        mermaid_code.append("    classDef startNode fill:#d4f1f9,stroke:#45b3e0,stroke-width:2px;")
        mermaid_code.append("    classDef failLink stroke:#f66,stroke-width:2px,color:#f66;")
        
        return "\n".join(mermaid_code)
    
    @staticmethod
    def get_html_template(mermaid_code, task_name):
        """Mermaid 코드를 포함한 HTML 템플릿 생성"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>태스크 흐름도 - {task_name}</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; }}
                .mermaid {{ width: 100%; }}
                h2 {{ color: #333; text-align: center; }}
            </style>
        </head>
        <body>
            <h2>{task_name} 흐름도</h2>
            <div class="mermaid">
            {mermaid_code}
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    securityLevel: 'loose',
                    theme: 'default',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'
                    }}
                }});
            </script>
        </body>
        </html>
        """