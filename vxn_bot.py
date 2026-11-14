import requests
import yfinance as yf

# [설정] 텔레그램 봇 토큰과 본인의 챗 ID 입력
TOKEN = "아까_발급받은_VXN_봇_토큰"      
CHAT_ID = "본인의_숫자_ID"        

def get_vxn_data():
    try:
        vxn = yf.Ticker("^VXN")
        df = vxn.history(period="1mo")
        
        if df.empty or len(df) < 2:
            return "⚠️ VXN 지수 데이터를 불러오기에 데이터가 부족합니다."
            
        latest_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        diff = latest_close - prev_close
        diff_percent = (diff / prev_close) * 100
        
        if latest_close >= 30:
            status = "🚨 **[공포 구간 / 강력 매수 타이밍!]**\nVXN이 30을 돌파했습니다. 적극적인 분할 매수를 검토해 보세요!"
        else:
            status = "⚪ **[평상 구간 / 관망]**\n아직 VXN 30 미만입니다. (기준치 30 미달)"
            
        message = (
            f"📉 **[나스닥 100 변동성 지수 (VXN)]**\n\n"
            f"• 현재 VXN: **{latest_close:.2f}**\n"
            f"• 전일 대비: {diff:+.2f} ({diff_percent:+.2f}%)\n\n"
            f"{status}\n\n"
            f"🕒 기준일: {df.index[-1].strftime('%Y-%m-%d')}"
        )
        return message
    except Exception as e:
        return f"🚨 VXN 지수 조회 중 오류 발생: {str(e)}"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("VXN 알림 발송 완료!")
    else:
        print(f"발송 실패: {response.text}")

if __name__ == "__main__":
    msg = get_vxn_data()
    send_telegram_message(msg)
