import time
import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIFICADORES ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_PRINCIPAL = "-1002237930838"  
CANAL_RESULTADOS = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

# Horarios de operación activos
HORARIOS_ACTIVOS = [(8, 11), (14, 17), (20, 23)]

def enviar_telegram(mensaje, canal_id, con_boton=True):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": canal_id, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    if con_boton:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "📥 UNIRSE AL VIP", "url": LINK_CANAL_PRINCIPAL}]]
        }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except:
        return None

def obtener_datos_tv(simbolo):
    try:
        handler = TA_Handler(
            symbol=simbolo,
            exchange="FX_IDC",
            screener="forex",
            interval=Interval.INTERVAL_1_MINUTE
        )
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio = analysis.indicators["close"]
        return rsi, precio
    except Exception as e:
        print(f"Error en TradingView para {simbolo}: {e}")
        return None, None

def esta_en_horario():
    hora_actual = datetime.now().hour
    for inicio, fin in HORARIOS_ACTIVOS:
        if inicio <= hora_actual < fin: return True
    return False

# --- INICIO DEL PROGRAMA ---
print("🚀 Bot LogicaDeApuesta Conectado a TradingView")

# Mensaje de activación inmediata al guardar el código
enviar_telegram(f"✅ **{BOT_NAME} CONECTADO**\n\nSincronizando con TradingView... 📡\nEstado: Buscando señales en pares OTC.", CANAL_PRINCIPAL)

wins, loss = 0, 0

while True:
    if esta_en_horario():
        activos = [
            {"t": "EURUSD", "d": "EUR/USD (OTC)"},
            {"t": "AUDUSD", "d": "AUD/USD (OTC)"},
            {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
            {"t": "USDJPY", "d": "USD/JPY (OTC)"}
        ]

        for par in activos:
            rsi, precio_entrada = obtener_datos_tv(par["t"])
            
            if rsi:
                # LÓGICA DE SEÑAL REAL
                # VENTA (DOWN) - RSI sobre 64
                if rsi >= 64:
                    enviar_telegram(f"💎 **SEÑAL CONFIRMADA** 💎\n\n💱 Par: {par['d']}\n🔻 Operación: **BAJA (DOWN)**\n⏱ Tiempo: 2 Minutos\n📉 RSI: {rsi:.2f}\n\n¡ENTRAR YA! 🔥", CANAL_PRINCIPAL)
                    
                    time.sleep(125) # Espera la duración de la operación
                    
                    _, precio_final = obtener_datos_tv(par["t"])
                    if precio_final and precio_final < precio_entrada:
                        wins += 1
                        resultado = "✅ RESULTADO: WIN ✅"
                    else:
                        loss += 1
                        resultado = "❌ RESULTADO: LOSS ❌"
                    
                    enviar_telegram(f"{resultado}\nPar: {par['d']}\nMarcador: {wins}W - {loss}L", CANAL_PRINCIPAL)
                    enviar_telegram(f"📑 *BITÁCORA*\n{resultado}\n📊 Marcador: {wins}W - {loss}L", CANAL_RESULTADOS)
                
                # COMPRA (UP) - RSI bajo 36
                elif rsi <= 36:
                    enviar_telegram(f"💎 **SEÑAL CONFIRMADA** 💎\n\n💱 Par: {par['d']}\n🟢 Operación: **SUBE (UP)**\n⏱ Tiempo: 2 Minutos\n📈 RSI: {rsi:.2f}\n\n¡ENTRAR YA! 🔥", CANAL_PRINCIPAL)
                    
                    time.sleep(125)
                    
                    _, precio_final = obtener_datos_tv(par["t"])
                    if precio_final and precio_final > precio_entrada:
                        wins += 1
                        resultado = "✅ RESULTADO: WIN ✅"
                    else:
                        loss += 1
                        resultado = "❌ RESULTADO: LOSS ❌"
                    
                    enviar_telegram(f"{resultado}\nPar: {par['d']}\nMarcador: {wins}W - {loss}L", CANAL_PRINCIPAL)
                    enviar_telegram(f"📑 *BITÁCORA*\n{resultado}\n📊 Marcador: {wins}W - {loss}L", CANAL_RESULTADOS)

    time.sleep(10) # Escaneo constante cada 10 segundos
    
