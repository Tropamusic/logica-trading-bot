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

analistas = [
    {"handler": TA_Handler(symbol="XAUUSD", exchange="OANDA", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "ORO ✨"},
    {"handler": TA_Handler(symbol="EURUSD", exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "EUR/USD 🇪🇺"},
    {"handler": TA_Handler(symbol="GBPUSD", exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "GBP/USD 🇬🇧"},
    {"handler": TA_Handler(symbol="USDJPY", exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "USD/JPY 🇯🇵"}
]

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def verificar_resultado(handler, nombre_activo, precio_entrada, direccion):
    global wins, losses, bloqueo
    time.sleep(120) # Tu regla de los 2 minutos de experiencia
    try:
        precio_final = handler.get_analysis().indicators["close"]
        if (direccion == "BAJA" and precio_final < precio_entrada) or (direccion == "SUBE" and precio_final > precio_entrada):
            wins += 1
            enviar_telegram(f"✅ **WIN: {nombre_activo}**\nEntrada: `{precio_entrada}` | Cierre: `{precio_final}`\n¡Buen trade, Lógica Trading! 💰")
        else:
            losses += 1
            enviar_telegram(f"❌ **LOSS: {nombre_activo}**\nEntrada: `{precio_entrada}` | Cierre: `{precio_final}`\nAnaliza el mercado y sigue. 📉")
    except: pass
    bloqueo = False

print(f"🚀 {BOT_NAME} ACTIVADO")
enviar_telegram(f"🚀 **{BOT_NAME} ONLINE**\nAnalizando mercado real con alertas de volatilidad.")

while True:
    if contador_senales >= LIMITE_SENALES:
        total = wins + losses
        efect = (wins / total * 100) if total > 0 else 0
        enviar_telegram(f"📊 **{BOT_NAME}: REPORTE**\n──────────────────\n✅ Ganadas: **{wins}**\n❌ Perdidas: **{losses}**\n🎯 Efectividad: **{round(efect, 2)}%**\n──────────────────\n🧊 Descanso de 30 min iniciado.")
        time.sleep(TIEMPO_ENFRIAMIENTO)
        contador_senales, wins, losses = 0, 0, 0

    if bloqueo:
        time.sleep(10)
        continue

    for a in analistas:
        if bloqueo or contador_senales >= LIMITE_SENALES: break
        try:
            analisis = a["handler"].get_analysis()
            indicators = analisis.indicators
            rsi = indicators["RSI"]
            precio_actual = indicators["close"]
            atr = indicators["ATR"]

            # LÓGICA DE ALERTA DE VOLATILIDAD
            # Si el ATR es inusualmente alto, el mercado está "picado"
            volatilidad_alta = False
            if "USD" in a['n'] and atr > 0.0007: volatilidad_alta = True
            if "ORO" in a['n'] and atr > 0.8: volatilidad_alta = True
            
            print(f"📊 {a['n']}: RSI {round(rsi, 2)} | ATR: {round(atr, 4)}")

            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                contador_senales += 1
                dir_op = "BAJA" if rsi >= 58.0 else "SUBE"
                emoji = "🔻" if dir_op == "BAJA" else "🟢"
                
                alerta_v = "⚠️ **¡ALERTA! VOLATILIDAD ALTA**\n" if volatilidad_alta else ""
                
                enviar_telegram(f"{alerta_v}🔔 **SEÑAL #{contador_senales}: {a['n']}**\n"
                                f"──────────────────\n"
                                f"📈 Operación: **{dir_op} {emoji}**\n"
                                f"📊 RSI: `{round(rsi, 2)}` | Precio: `{precio_actual}`\n"
                                f"⏳ *Verificando en 2 min...*")
                
                threading.Thread(target=verificar_resultado, args=(a["handler"], a["n"], precio_actual, dir_op)).start()
            
            time.sleep(6) 
        except Exception as e:
            if "429" in str(e): time.sleep(120)
            continue
    time.sleep(10)
