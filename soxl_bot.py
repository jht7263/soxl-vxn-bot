import time
import requests
import yfinance as yf
import schedule

# [설정] SOXL 봇 토큰과 본인의 챗 ID 입력
TOKEN = "9007580045:AAHe_CRSIUg9FIk2I2WSdN8jjsUj9uULZcM"      
CHAT_ID = "7063499674"        

# 분석할 대상 (SOXL)
TICKER_SYMBOL = "SOXL"

def calculate_rsi(data, window=14):
    # RSI 계산 함수 (와일더 방식)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_rsi_data():
    try:
        # 최근 60일간의 데이터를 가져와서 RSI 계산
        stock = yf.Ticker(TICKER_SYMBOL)
        df = stock.history(period="60d")
        
        if len(df) < 20:
            return f"⚠️ {TICKER_SYMBOL} 데이터를 불러오기에 데이터가 부족합니다."
            
        df['RSI'] = calculate_rsi(df)
        latest_rsi = df['RSI'].iloc[-1]
        latest_close = df['Close'].iloc[-1]
        
        # RSI 상태 판단
        if latest_rsi >= 70:
            status = "🔴 과매수 구간 (주의)"
        elif latest_rsi <= 30:
            status = "🟢 과매도 구간 (기회 탐색)"
        else:
            status = "⚪ 중립 구간"
            
        message = (
            f"📈 **[{TICKER_SYMBOL}] RSI 지수 일일 모니터링**\n\n"
            f"• 현재가: **${latest_close:,.2f}**\n"
            f"• 14일 RSI: **{latest_rsi:.2f}**\n"
            f"• 상태: {status}\n"
            f"🕒 기준일: {df.index[-1].strftime('%Y-%m-%d')}"
        )
        return message
    except Exception as e:
        return f"🚨 SOXL RSI 지수 조회 중 오류 발생: {str(e)}"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("SOXL RSI 알림 발송 완료!")
    else:
        print(f"발송 실패: {response.text}")

def job():
    print("SOXL RSI 지수 알림 실행 중...")
    msg = get_rsi_data()
    send_telegram_message(msg)

if __name__ == "__main__":
    print("SOXL RSI 봇 테스트 전송을 시작합니다...")
    job() # 실행 시 테스트로 즉시 1회 전송
    
    # 매일 아침 9시와 저녁 9시에 알림 전송 예약
    schedule.every().day.at("09:00").do(job)
    schedule.every().day.at("21:00").do(job)

    print("매일 아침 9시, 저녁 9시 SOXL RSI 알림 대기 중...")
    while True:
        schedule.run_pending()
        time.sleep(1)