import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"
BOT_NAME = "🔱 LÓGICA TRADING PRO"

# ESTADÍSTICAS Y CONTROL
bloqueo = False
contador_senales = 0
wins, losses = 0, 0
LIMITE_SENALES = 5
TIEMPO_ENFRIAMIENTO = 1800 

# LISTA DE 10 ACTIVOS (MERCADO REAL)
activos_config = [
    {"s": "XAUUSD", "e": "OANDA", "n": "ORO ✨"},
    {"s": "EURUSD", "e": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"s": "GBPUSD", "e": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"s": "USDJPY", "e": "FX_IDC", "n": "USD/JPY 🇯🇵"},
    {"s": "AUDUSD", "e": "FX_IDC", "n": "AUD/USD 🇦🇺"},
    {"s": "USDCAD", "e": "FX_IDC", "n": "USD/CAD 🇨🇦"},
    {"s": "EURJPY", "e": "FX_IDC", "n": "EUR/JPY 🇯🇵"},
    {"s": "GBPJPY", "e": "FX_IDC", "n": "GBP/JPY 🇬🇧"},
    {"s": "NZDUSD", "e": "FX_IDC", "n": "NZD/USD 🇳🇿"},
    {"s": "USDCHF", "e": "FX_IDC", "n": "USD/CHF 🇨🇭"}
]

analistas = []
for a in activos_config:
    analistas.append({
        "handler": TA_Handler(symbol=a['s'], exchange=a['e'], screener="forex", interval=Interval.INTERVAL_1_MINUTE),
        "n": a['n']
    })

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def verificar_resultado(handler, nombre_activo, precio_entrada, direccion):
    global wins, losses, bloqueo
    time.sleep(120) 
    try:
        precio_final = handler.get_analysis().indicators["close"]
        if (direccion == "BAJA" and precio_final < precio_entrada) or (direccion == "SUBE" and precio_final > precio_entrada):
            wins += 1
            enviar_telegram(f"✅ **WIN: {nombre_activo}**\n💰 Entrada: `{precio_entrada}` | Cierre: `{precio_final}`")
        else:
            losses += 1
            enviar_telegram(f"❌ **LOSS: {nombre_activo}**\n📉 Entrada: `{precio_entrada}` | Cierre: `{precio_final}`")
    except: pass
    bloqueo = False

print(f"🚀 {BOT_NAME} - MULTI-ACTIVO (10) ACTIVADO")
enviar_telegram(f"🚀 **{BOT_NAME} ONLINE**\n📡 Monitoreando 10 activos con reporte de rendimiento.")

while True:
    if contador_senales >= LIMITE_SENALES:
        total = wins + losses
        efect = (wins / total * 100) if total > 0 else 0
        enviar_telegram(f"📊 **{BOT_NAME}: REPORTE FINAL**\n──────────────────\n✅ Ganadas: **{wins}**\n❌ Perdidas: **{losses}**\n🎯 Efectividad: **{round(efect, 2)}%**\n──────────────────\n🧊 Descanso de 30 min iniciado.")
        time.sleep(TIEMPO_ENFRIAMIENTO)
        contador_senales, wins, losses = 0, 0, 0

    if bloqueo:
        time.sleep(10)
        continue

    for a in analistas:
        if bloqueo or contador_senales >= LIMITE_SENALES: break
        try:
            indicators = a["handler"].get_analysis().indicators
            rsi = indicators["RSI"]
            precio_actual = indicators["close"]
            atr = indicators["ATR"]
            
            # Alerta de volatilidad inteligente
            vol_alta = (atr > 0.0007) if "JPY" not in a['n'] else (atr > 0.03)

            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                contador_senales += 1
                dir_op = "BAJA" if rsi >= 58.0 else "SUBE"
                emoji = "🔻" if dir_op == "BAJA" else "🟢"
                
                aviso_v = "⚠️ **VOLATILIDAD ALTA**\n" if vol_alta else ""
                enviar_telegram(f"{aviso_v}🔔 **SEÑAL #{contador_senales}: {a['n']}**\n📈 Operación: **{dir_op} {emoji}**\n📊 RSI: `{round(rsi, 2)}` | Precio: `{precio_actual}`")
                
                threading.Thread(target=verificar_resultado, args=(a["handler"], a["n"], precio_actual, dir_op)).start()
            
            time.sleep(5) # Delay seguro para 10 activos
        except Exception as e:
            if "429" in str(e): time.sleep(120)
            continue
    time.sleep(10)
