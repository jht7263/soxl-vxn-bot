
import requests
import yfinance as yf

# 텔레그램 봇 설정
TOKEN = "9007580045:AAHe_CRSIUg9FIk2I2WSdN8jjsUj9uULZcM" 
CHAT_ID = "7063499674"


def get_vxn_data():
    try:
        vxn = yf.Ticker("^VXN")
        df = vxn.history(period="1mo")

        if df.empty or len(df) < 2:
            return "⚠️ VXN 지수 데이터를 불러오기에 데이터가 부족합니다."

        latest_close = float(df["Close"].iloc[-1])
        prev_close = float(df["Close"].iloc[-2])

        diff = latest_close - prev_close
        diff_percent = (diff / prev_close) * 100 if prev_close != 0 else 0

        if latest_close >= 30:
            status = (
                "🚨 [공포 구간 / 매수 검토 구간]\n"
                "VXN이 30을 돌파했습니다. "
                "시장 상황을 확인하고 분할 매수를 검토하세요!"
            )
        else:
            status = (
                "⚪ [평상 구간 / 관망]\n"
                "아직 VXN 30 미만입니다. (기준치 30 미달)"
            )

        message = (
            f"📉 *[나스닥 100 변동성 지수 (VXN)]*\n\n"
            f"• 현재 VXN: *{latest_close:.2f}*\n"
            f"• 전일 대비: {diff:+.2f} ({diff_percent:+.2f}%)\n\n"
            f"{status}\n\n"
            f"🕒 기준일: {df.index[-1].strftime('%Y-%m-%d')}"
        )

        return message

    except Exception as e:
        return f"🚨 VXN 지수 조회 중 오류 발생: {str(e)}"


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        print("VXN 알림 발송 완료!")

    except requests.exceptions.RequestException as e:
        print(f"텔레그램 발송 실패: {e}")


if __name__ == "__main__":
    msg = get_vxn_data()
    send_telegram_message(msg)
