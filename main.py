import time
import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIFICADORES ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"

# Canal donde se envían las SEÑALES (ENTRA YA)
CANAL_VIP = "-1002237930838"  

# Canal donde se envían los RESULTADOS (WIN/LOSS)
CANAL_BITACORA = "-1003621701961" 

LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

def enviar_telegram(mensaje, canal_id, con_boton=True):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": canal_id, "text": mensaje, "parse_mode": "Markdown"}
    if con_boton:
        payload["reply_markup"] = {"inline_keyboard": [[{"text": "📥 UNIRSE AL VIP", "url": LINK_CANAL_PRINCIPAL}]]}
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

# --- INICIO AUTOMÁTICO AL GUARDAR ---
print(f"🚀 {BOT_NAME} Iniciado correctamente...")
# Aviso de activación al canal VIP
enviar_telegram(f"✅ **{BOT_NAME} ACTIVADO**\n\nAnalizando mercado real en TradingView... 📡\nBuscando las mejores señales VIP.", CANAL_VIP)

wins, loss = 0, 0

while True:
    # Pares a monitorear
    activos = [
        {"t": "EURUSD", "d": "EUR/USD (OTC)"},
        {"t": "AUDUSD", "d": "AUD/USD (OTC)"},
        {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
        {"t": "USDJPY", "d": "USD/JPY (OTC)"}
    ]

    for activo in activos:
        rsi, precio_entrada = obtener_analisis(activo["t"])
        
        if rsi:
            # --- LÓGICA DE VENTA (DOWN) ---
            if rsi >= 64:
                # 1. Envía la señal al canal VIP
                enviar_telegram(f"💎 **SEÑAL VIP** 💎\n\n💱 Par: {activo['d']}\n🔻 Operación: **BAJA (DOWN)**\n⏱ Tiempo: 2 Minutos\n📉 RSI: {rsi:.2f}\n\n¡ENTRA YA! 🔥", CANAL_VIP)
                
                time.sleep(125) # Espera el tiempo de la operación (2 min)
                
                _, precio_final = obtener_analisis(activo["t"])
                if precio_final and precio_final < precio_entrada:
                    wins += 1
                    res_msg = f"✅ **RESULTADO: WIN** ✅\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                else:
                    loss += 1
                    res_msg = f"❌ **RESULTADO: LOSS** ❌\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                
                # 2. Envía el resultado a ambos para transparencia
                enviar_telegram(res_msg, CANAL_VIP)
                enviar_telegram(f"📑 *REGISTRO DE BITÁCORA*\n{res_msg}", CANAL_BITACORA)

            # --- LÓGICA DE COMPRA (UP) ---
            elif rsi <= 36:
                # 1. Envía la señal al canal VIP
                enviar_telegram(f"💎 **SEÑAL VIP** 💎\n\n💱 Par: {activo['d']}\n🟢 Operación: **SUBE (UP)**\n⏱ Tiempo: 2 Minutos\n📈 RSI: {rsi:.2f}\n\n¡ENTRA YA! 🔥", CANAL_VIP)
                
                time.sleep(125)
                
                _, precio_final = obtener_analisis(activo["t"])
                if precio_final and precio_final > precio_entrada:
                    wins += 1
                    res_msg = f"✅ **RESULTADO: WIN** ✅\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                else:
                    loss += 1
                    res_msg = f"❌ **RESULTADO: LOSS** ❌\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                
                enviar_telegram(res_msg, CANAL_VIP)
                enviar_telegram(f"📑 *REGISTRO DE BITÁCORA*\n{res_msg}", CANAL_BITACORA)

    time.sleep(10) # Pausa de escaneo para no saturar
