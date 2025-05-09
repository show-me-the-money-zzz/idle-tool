class FlowchartGenerator:
    """
    태스크 데이터를 기반으로 Mermaid 형식의 흐름도 코드를 생성하는 클래스
    """
    
    @staticmethod
    def generate_mermaid_code(task_name, task_data):
        """태스크 데이터로부터 Mermaid 흐름도 코드 생성"""
        mermaid_code = ["flowchart TD"]
        
        # 태스크 데이터 추출 (객체 또는 딕셔너리 형태 모두 지원)
        if hasattr(task_data, 'steps'):
            steps = task_data.steps
            start_key = task_data.start_key if hasattr(task_data, 'start_key') else ''
        else:
            steps = task_data.get('steps', {})
            start_key = task_data.get('start_key', '')
        
        # 노드 ID 매핑 생성
        step_ids = {}
        for i, key in enumerate(steps.keys()):
            # 안전한 노드 ID 생성
            safe_id = f"step{i+1}"
            step_ids[key] = safe_id
        
        # 노드 생성
        for key, node_id in step_ids.items():
            # 노드 텍스트에 ID만 표시 (원래 텍스트는 너무 길어서 표시하지 않음)
            # 대신 원래 텍스트를 툴팁이나 상세 보기에서 확인할 수 있게 설정 가능
            
            # 노드 텍스트에서 이스케이프 처리
            node_text = key.replace('"', '\\"')
            
            # 노드 스타일 설정
            if key == start_key:
                mermaid_code.append(f'    {node_id}["{node_text}"]:::startNode')
            else:
                mermaid_code.append(f'    {node_id}["{node_text}"]')
        
        # 일반 연결 추가 (녹색)
        for key, step in steps.items():
            if key not in step_ids:
                continue
                
            from_id = step_ids[key]
            
            # 다음 단계 추출
            next_steps = []
            if hasattr(step, 'next_step'):
                if isinstance(step.next_step, list):
                    next_steps = step.next_step
                else:
                    next_steps = [step.next_step] if step.next_step else []
            elif isinstance(step, dict):
                next_steps = step.get('next_step', [])
                if not isinstance(next_steps, list):
                    next_steps = [next_steps] if next_steps else []
            
            # 다음 단계 연결 (녹색)
            for next_step in next_steps:
                if next_step in step_ids:
                    to_id = step_ids[next_step]
                    mermaid_code.append(f"    {from_id} --> {to_id}:::successLink")
        
        # 실패 경로 추가 (빨간색)
        for key, step in steps.items():
            if key not in step_ids:
                continue
                
            from_id = step_ids[key]
            
            # 실패 단계 추출
            fail_step = None
            if hasattr(step, 'fail_step') and step.fail_step:
                fail_step = step.fail_step
            elif isinstance(step, dict) and step.get('fail_step'):
                fail_step = step.get('fail_step')
            
            if fail_step and fail_step in step_ids:
                to_id = step_ids[fail_step]
                mermaid_code.append(f"    {from_id} -- 실패 --> {to_id}:::failLink")
        
        # 스타일 정의 추가
        mermaid_code.append("    classDef startNode fill:#d4f1f9,stroke:#45b3e0,stroke-width:2px;")
        # mermaid_code.append("    classDef successLink stroke:#4CAF50,stroke-width:1.5px;")  # 녹색 연결선
        # mermaid_code.append("    classDef failLink stroke:#f44336,stroke-width:1.5px;")     # 빨간색 연결선
        
        return "\n".join(mermaid_code)
    
    @staticmethod
    def get_html_template(mermaid_code, task_name):
        """Mermaid 코드를 포함한 HTML 템플릿 생성"""
        # HTML 특수 문자 이스케이프
        escaped_task_name = task_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{escaped_task_name} 흐름도</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@8.11.0/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Malgun Gothic', 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h2 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .container {{
            max-width: 90%;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        .mermaid {{
            overflow: auto;
            font-size: 14px;
        }}
        .controls {{
            text-align: center;
            margin: 10px 0 20px 0;
        }}
        .controls button {{
            margin: 0 5px;
            padding: 5px 10px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
        }}
        .controls button:hover {{
            background-color: #e0e0e0;
        }}
        .info {{
            margin-top: 20px;
            padding: 10px;
            background-color: #f0f7ff;
            border-left: 4px solid #45b3e0;
            color: #333;
            font-size: 0.9em;
        }}
        .legend {{
            margin-top: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .legend-start {{
            background-color: #d4f1f9;
            border: 2px solid #45b3e0;
        }}
        .legend-normal {{
            background-color: white;
            border: 1px solid #333;
        }}
        .legend-success {{
            width: 50px;
            height: 2px;
            background-color: #4CAF50;
        }}
        .legend-fail {{
            width: 50px;
            height: 2px;
            background-color: #f44336;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>{escaped_task_name} 흐름도</h2>
        
        <!-- 확대/축소 버튼 -->
        <div class="controls">
            <button onclick="zoomIn()">확대 (+)</button>
            <button onclick="resetZoom()">원래 크기</button>
            <button onclick="zoomOut()">축소 (-)</button>
        </div>
        
        <div class="mermaid">
{mermaid_code}
        </div>
        
        <div class="info">
            <p>단계 ID와 설명을 모두 노드에 표시합니다. 녹색 선은 일반 진행 경로, 빨간색 선은 실패 경로를 나타냅니다.</p>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color legend-start"></div>
                    <span>시작 노드</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color legend-normal"></div>
                    <span>일반 노드</span>
                </div>
                <div class="legend-item">
                    <div class="legend-success"></div>
                    <span>다음 단계</span>
                </div>
                <div class="legend-item">
                    <div class="legend-fail"></div>
                    <span>실패 단계</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Mermaid 초기화 설정
        mermaid.initialize({{
            startOnLoad: true,
            securityLevel: 'loose',
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis',
                diagramPadding: 20,
                nodeSpacing: 50,
                rankSpacing: 70
            }}
        }});
        
        // 확대/축소 기능
        var currentZoom = 1.0;
        
        function zoomIn() {{
            currentZoom += 0.1;
            applyZoom();
        }}
        
        function zoomOut() {{
            if (currentZoom > 0.3) {{
                currentZoom -= 0.1;
                applyZoom();
            }}
        }}
        
        function resetZoom() {{
            currentZoom = 1.0;
            applyZoom();
        }}
        
        function applyZoom() {{
            const svgElements = document.querySelectorAll('.mermaid svg');
            if (svgElements.length > 0) {{
                svgElements.forEach(svg => {{
                    svg.style.transform = `scale(${{currentZoom}})`;
                    svg.style.transformOrigin = 'top center';
                }});
            }}
        }}
        
        // Mermaid 다이어그램 렌더링 재시도 (안정성 향상)
        document.addEventListener('DOMContentLoaded', function() {{
            // 첫 번째 렌더링 시도
            setTimeout(function() {{
                try {{
                    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                }} catch (e) {{
                    console.error("Mermaid 초기화 실패:", e);
                    
                    // 오류 발생 시 다시 시도
                    setTimeout(function() {{
                        try {{
                            mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                        }} catch (e) {{
                            console.error("재시도 실패:", e);
                        }}
                    }}, 1000);
                }}
            }}, 500);
        }});
    </script>
</body>
</html>"""
    
    @staticmethod
    def generate_simple_test_code():
        """간단한 테스트 코드"""
        return """flowchart TD
    A[시작] --> B[처리]:::successLink
    B --> C[판단]:::successLink
    C -->|Yes| D[종료]:::successLink
    C -->|No| B:::successLink
    classDef successLink stroke:#4CAF50,stroke-width:1.5px;"""
    
    @staticmethod
    def clean_flowchart_data(task_data):
        """태스크 데이터를 정리하여 관련 정보만 포함하는 딕셔너리 반환"""
        clean_data = {
            'start_key': '',
            'comment': '',
            'steps': {}
        }
        
        # 시작 키와 설명 추출
        if hasattr(task_data, 'start_key'):
            clean_data['start_key'] = task_data.start_key
        
        if hasattr(task_data, 'comment'):
            clean_data['comment'] = task_data.comment
        
        # 단계 정보 추출
        if hasattr(task_data, 'steps'):
            for key, step in task_data.steps.items():
                step_info = {}
                
                # 중요 속성 추출
                if hasattr(step, 'seq'):
                    step_info['seq'] = step.seq
                
                if hasattr(step, 'type'):
                    step_info['type'] = step.type
                
                if hasattr(step, 'next_step'):
                    step_info['next_step'] = step.next_step
                
                if hasattr(step, 'fail_step'):
                    step_info['fail_step'] = step.fail_step
                
                clean_data['steps'][key] = step_info
        
        return clean_data