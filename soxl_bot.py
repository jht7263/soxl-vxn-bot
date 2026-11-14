import requests
import yfinance as yf
import pandas as pd

# [설정] SOXL 봇 토큰과 본인의 챗 ID 입력
TOKEN = "9007580045:AAHe_CRSIUg9FIk2I2WSdN8jjsUj9uULZcM"      
CHAT_ID = "7063499674" 
TICKER_SYMBOL = "SOXL"

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_rsi_data():
    try:
        stock = yf.Ticker(TICKER_SYMBOL)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 15:
            return f"⚠️ {TICKER_SYMBOL} 데이터를 불러오기에 데이터가 부족합니다."
            
        df['RSI'] = calculate_rsi(df)
        latest_rsi = df['RSI'].iloc[-1]
        latest_close = df['Close'].iloc[-1]
        
        if latest_rsi >= 70:
            status = "🔴 **과매수 구간 (주의)**"
        elif latest_rsi <= 30:
            status = "🟢 **과매도 구간 (기회 탐색)**"
        else:
            status = "⚪ **중립 구간**"
            
        message = (
            f"📈 **[{TICKER_SYMBOL}] 14일 RSI 지수 알림**\n\n"
            f"• 현재가: **${latest_close:,.2f}**\n"
            f"• 14일 RSI: **{latest_rsi:.2f}**\n\n"
            f"{status}\n\n"
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

if __name__ == "__main__":
    msg = get_rsi_data()
    send_telegram_message(msg)
