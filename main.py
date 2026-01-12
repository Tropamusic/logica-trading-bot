import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

def enviar_telegram(mensaje, canal_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": canal_id, 
        "text": mensaje, 
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": [[{"text": "📥 UNIRSE AL VIP", "url": LINK_CANAL_PRINCIPAL}]]}
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def obtener_analisis(simbolo):
    try:
        handler = TA_Handler(
            symbol=simbolo,
            exchange="FX_IDC",
            screener="forex",
            interval=Interval.INTERVAL_1_MINUTE
        )
        analysis = handler.get_analysis()
        return analysis.indicators["RSI"], analysis.indicators["close"]
    except:
        return None, None

# --- INICIO DEL BOT ---
print(f"🚀 {BOT_NAME} Iniciado 24/7...")
enviar_telegram(f"✅ **{BOT_NAME} ACTIVADO**\n\nSincronizado con TradingView 24/7. 📡\nEnviando señales cada 2 minutos.", CANAL_VIP)

wins, loss = 0, 0

while True:
    # Definimos una racha de trabajo (ejemplo: 10 señales antes de descansar)
    operaciones_realizadas = 0
    
    while operaciones_realizadas < 10:
        activos = [
            {"t": "EURUSD", "d": "EUR/USD (OTC)"},
            {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
            {"t": "AUDUSD", "d": "AUD/USD (OTC)"},
            {"t": "USDJPY", "d": "USD/JPY (OTC)"}
        ]

        for activo in activos:
            rsi, precio_entrada = obtener_analisis(activo["t"])
            
            if rsi:
                # SEÑAL DE VENTA (DOWN)
                if rsi >= 64:
                    enviar_telegram(f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n💱 Par: {activo['d']}\n🔻 Acción: **BAJA (DOWN)**\n⏱ Tiempo: 2 Minutos\n📊 RSI: {rsi:.2f}\n\n🔥 **¡ENTRAR YA!** 🔥", CANAL_VIP)
                    
                    time.sleep(125) # 2 minutos de operación
                    
                    _, precio_final = obtener_analisis(activo["t"])
                    if precio_final and precio_final < precio_entrada:
                        wins += 1
                        res = f"✅ **WIN GANADA** ✅\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    else:
                        loss += 1
                        res = f"❌ **LOSS PERDIDA** ❌\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    
                    enviar_telegram(res, CANAL_VIP)
                    enviar_telegram(f"📑 *BITÁCORA*\n{res}", CANAL_BITACORA)
                    operaciones_realizadas += 1
                    time.sleep(10) # Pausa breve para buscar la siguiente

                # SEÑAL DE COMPRA (UP)
                elif rsi <= 36:
                    enviar_telegram(f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n💱 Par: {activo['d']}\n🟢 Acción: **SUBE (UP)**\n⏱ Tiempo: 2 Minutos\n📈 RSI: {rsi:.2f}\n\n🔥 **¡ENTRAR YA!** 🔥", CANAL_VIP)
                    
                    time.sleep(125)
                    
                    _, precio_final = obtener_analisis(activo["t"])
                    if precio_final and precio_final > precio_entrada:
                        wins += 1
                        res = f"✅ **WIN GANADA** ✅\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    else:
                        loss += 1
                        res = f"❌ **LOSS PERDIDA** ❌\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    
                    enviar_telegram(res, CANAL_VIP)
                    enviar_telegram(f"📑 *BITÁCORA*\n{res}", CANAL_BITACORA)
                    operaciones_realizadas += 1
                    time.sleep(10)

        time.sleep(15) # Escaneo constante si no hay señales

    # --- PERIODO DE DESCANSO ---
    enviar_telegram(f"⏳ **MODO DESCANSO ACTIVADO**\n\nHe completado un ciclo de señales. Tomaré un descanso de 1 hora para analizar la tendencia global.\n\nMarcador actual: {wins}W - {loss}L", CANAL_VIP)
    print("Iniciando descanso de 1 hora...")
    time.sleep(3600) # Descansa exactamente 1 hora (3600 segundos)
    enviar_telegram(f"🚀 **BOT REACTIVADO**\n\nEl descanso ha terminado. ¡Volvemos a buscar señales ganadoras!", CANAL_VIP)
