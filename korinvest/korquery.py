import os
import requests
import json
from dotenv import load_dotenv, find_dotenv
from korinvest import get_access_token, URL_BASE

# --- 환경변수 로드 ---
load_dotenv(find_dotenv())

# --- API 키 및 토큰 설정 (환경변수에서 로드) ---
APP_KEY = os.environ.get('KOREA_INVEST_APP_KEY')
APP_SECRET = os.environ.get('KOREA_INVEST_APP_SECRET')
ACCESS_TOKEN = os.environ.get('KOREA_INVEST_ACCESS_TOKEN')

if not all([APP_KEY, APP_SECRET]):
    raise ValueError('필수 환경변수가 설정되지 않았습니다: KOREA_INVEST_APP_KEY, KOREA_INVEST_APP_SECRET')

# 토큰 자동 갱신을 위한 전역 변수
_access_token = ACCESS_TOKEN

# --- 2단계: 토큰 갱신 및 도우미 함수 정의 ---

def refresh_access_token():
    """토큰이 만료되었을 때 새 토큰을 자동으로 발급받습니다."""
    global _access_token
    result = None
    try:
        print("⚠️  토큰 갱신 중...")
        result = get_access_token()
        if isinstance(result, dict) and 'access_token' in result:
            new_token = result['access_token']
        else:
            new_token = result  # 문자열로 직접 반환되는 경우
        _access_token = new_token
        print("✅ 새 토큰 발급 완료")
        return new_token
    except KeyError as e:
        print(f"❌ 토큰 갱신 응답 형식 오류: {e}")
        print(f"   응답: {result}")
        raise
    except Exception as e:
        print(f"❌ 토큰 갱신 실패: {e}")
        raise


def get_stock_price(stock_code: str, retry: bool = True) -> dict:
    """
    특정 종목의 현재가 및 정보를 조회합니다.
    토큰이 만료되면 자동으로 새 토큰을 발급받고 재시도합니다.
    
    Args:
        stock_code (str): 종목코드 (예: '005930' - 삼성전자)
        retry (bool): 토큰 만료 시 자동 재시도 여부 (기본값: True)
    
    Returns:
        dict: API 응답 데이터
    """
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {_access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "custype": "P",
        "tr_id": "FHKST01010400"  # 일별 시세 조회
    }
    params = {
        "fid_cond_mrkt_div_code": "J",  # 주식
        "fid_input_iscd": stock_code,
        "fid_org_adj_prc": "0",  # 수정주가 사용 안함
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"[DEBUG] Status Code: {response.status_code}")
        print(f"[DEBUG] Response Text: {response.text[:200]}")
        
        data = response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 요청 실패: {e}")
        data = {"rt_cd": "", "msg_cd": "", "msg1": str(e)}
    
    # 토큰 만료 에러 처리 및 자동 갱신
    if data.get('msg_cd') == 'EGW00123' and retry:  # 기간이 만료된 token
        print("⚠️  토큰이 만료되었습니다. 자동 갱신 중...")
        try:
            refresh_access_token()
        except Exception as e:
            return {
                "rt_cd": "1",
                "msg_cd": "TOKEN_REFRESH_FAILED",
                "msg1": f"토큰 갱신 실패: {e}",
            }
        # 재귀적으로 한 번 더 시도 (단, 무한 루프 방지를 위해 retry=False)
        return get_stock_price(stock_code, retry=False)
    
    return data


def print_stock_info(data: dict):
    """API 응답 데이터를 보기좋게 출력합니다."""
    if data.get('rt_cd') == '0':
        output = data.get('output', {})
        print(f"종목명: {output.get('hts_kor_isnm', 'N/A')}")
        print(f"현재가: {output.get('stck_prpr', 'N/A')}원")
        print(f"전일대비: {output.get('prdy_vrss', 'N/A')}원 ({output.get('prdy_ctrt', 'N/A')}%)")
    else:
        print(f"API 호출 실패: {data.get('msg1', '알 수 없는 오류')}")



if __name__ == "__main__":
    try:
        # 환경 정보 출력
        print("=== 환경 정보 ===")
        print(f"APP_KEY: {APP_KEY[:20]}..." if APP_KEY else "미설정")
        print(f"ACCESS_TOKEN: {_access_token[:30]}..." if _access_token else "미설정")
        print(f"URL_BASE: {URL_BASE}")
        print()
        
        # 예제 1: 삼성전자 조회
        print("=== 삼성전자 주가 조회 ===")
        samsung_data = get_stock_price("005930")
        print_stock_info(samsung_data)
        
        print("\n=== 원본 응답 (디버깅) ===")
        print(json.dumps(samsung_data, indent=2, ensure_ascii=False))
        
        # 예제 2: SK하이닉스 조회
        print("\n=== SK하이닉스 주가 조회 ===")
        sk_data = get_stock_price("000660")
        print_stock_info(sk_data)
        
    except ValueError as e:
        print(f"설정 오류: {e}")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

