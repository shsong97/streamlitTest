import matplotlib.font_manager as fm

# 현재 시스템에서 Matplotlib이 인식하는 모든 폰트 목록 확인
font_list = [f.name for f in fm.fontManager.ttflist]
print("설치된 폰트 목록:", font_list)

# 'NanumGothic'이 있는지 확인
if 'NanumGothic' in font_list:
    print("✅ 'NanumGothic' 폰트가 정상적으로 인식되었습니다!")
else:
    print("❌ 'NanumGothic' 폰트가 Matplotlib에서 인식되지 않습니다.")