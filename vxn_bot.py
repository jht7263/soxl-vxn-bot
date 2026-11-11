import time
import requests
import yfinance as yf
import schedule

# [설정] 텔레그램 봇 토큰과 본인의 챗 ID 입력
TOKEN = "9263607392:AAGpLBgWnijtqMgIprGMvauSrugBcsg7eRM"      
CHAT_ID = "7063499674"        

def get_vxn_data():
    try:
        # 야후 파이낸스에서 VXN(^VXN) 지수 데이터 가져오기
        vxn = yf.Ticker("^VXN")
        df = vxn.history(period="5d")
        
        if len(df) == 0:
            return "⚠️ VXN 지수 데이터를 불러오지 못했습니다."
            
        latest_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else latest_close
        diff = latest_close - prev_close
        diff_percent = (diff / prev_close) * 100
        
        # 30 이상 여부에 따른 매수 타이밍 판단
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

def job():
    print("VXN 지수 알림 실행 중...")
    msg = get_vxn_data()
    send_telegram_message(msg)

if __name__ == "__main__":
    print("VXN 봇 테스트 전송을 시작합니다...")
    job() # 실행 시 테스트로 즉시 1회 전송
    
    # 매일 아침 9시와 저녁 9시에 알림 전송 예약
    schedule.every().day.at("09:00").do(job)
    schedule.every().day.at("21:00").do(job)

    print("매일 아침 9시, 저녁 9시 VXN 알림 대기 중...")
    while True:
        schedule.run_pending()
        time.sleep(1)