import requests
import yfinance as yf

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
        # 타임아웃 방지를 위해 세션 및 다운로드 방식 적용
        df = yf.download(TICKER_SYMBOL, period="3mo", progress=False)
        
        if df.empty or len(df) < 15:
            return f"⚠️ {TICKER_SYMBOL} 실시간 주가 데이터를 불러오기에 데이터가 부족합니다."
            
        # MultiIndex 구조일 경우 단일화
        if 'Close' in df.columns and hasattr(df['Close'], 'iloc'):
            close_series = df['Close'].iloc[:, 0] if len(df['Close'].shape) > 1 else df['Close']
        else:
            close_series = df['Close']

        temp_df = pd.DataFrame({'Close': close_series})
        temp_df['RSI'] = calculate_rsi(temp_df)
        
        latest_rsi = temp_df['RSI'].iloc[-1]
        latest_close = temp_df['Close'].iloc[-1]
        
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
            f"🕒 기준일: {temp_df.index[-1].strftime('%Y-%m-%d')}"
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
    requests.post(url, json=payload)

if __name__ == "__main__":
    msg = get_rsi_data()
    send_telegram_message(msg)
