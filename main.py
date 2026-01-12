import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 

def enviar_telegram(mensaje, canal_id, con_boton=True):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": canal_id, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    if con_boton:
        payload["reply_markup"] = {"inline_keyboard": [[{"text": "📥 ENTRAR AL BROKER", "url": LINK_CANAL_PRINCIPAL}]]}
    
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
print("🚀 Bot de Señales Activo...")

while True:
    # Mensaje de inicio de jornada
    enviar_telegram("📡 **Buscando señales de alta precisión en TradingView...**", CANAL_VIP, False)
    
    contador_ciclo = 0
    wins, loss = 0, 0

    while contador_ciclo < 4:
        activos = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY"]
        
        for par in activos:
            if contador_ciclo >= 4: break
            
            rsi, precio_entrada = obtener_analisis(par)
            
            # Ajustamos el RSI para que dispare señales cada 2 minutos aproximadamente
            if rsi and (rsi >= 60 or rsi <= 40):
                direccion = "BAJA (DOWN) 🔻" if rsi >= 60 else "SUBE (UP) 🟢"
                
                # --- PASO 1: ENVIAR LA SEÑAL DE OPERACIÓN (ESTO ES LO QUE TE FALTABA) ---
                mensaje_entrada = (f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n"
                                   f"💱 Par: {par} (OTC)\n"
                                   f"🎯 Acción: **{direccion}**\n"
                                   f"⏱ Tiempo: 2 Minutos\n"
                                   f"📊 RSI: {rsi:.2f}\n\n"
                                   f"🔥 **¡ENTRA YA AHORA!** 🔥")
                
                enviar_telegram(mensaje_entrada, CANAL_VIP)
                
                # --- PASO 2: ESPERAR LOS 2 MINUTOS DE LA OPERACIÓN ---
                time.sleep(125) 
                
                # --- PASO 3: VERIFICAR Y ENVIAR RESULTADO ---
                _, precio_final = obtener_analisis(par)
                if (rsi >= 60 and precio_final < precio_entrada) or (rsi <= 40 and precio_final > precio_entrada):
                    wins += 1
                    res = f"✅ **RESULTADO: WIN** ✅\nPar: {par}\n¡Operación ganada con éxito!"
                else:
                    loss += 1
                    res = f"❌ **RESULTADO: LOSS** ❌\nPar: {par}\nMarcador actual: {wins}W - {loss}L"
                
                enviar_telegram(res, CANAL_VIP)
                enviar_telegram(f"📑 *REGISTRO BITÁCORA*\n{res}", CANAL_BITACORA)
                
                contador_ciclo += 1
                time.sleep(15) # Pausa pequeña para la siguiente señal

        time.sleep(20) # Escaneo constante si no hay señales

    # --- PASO 4: DESCANSO DE 1 HORA ---
    enviar_telegram(f"⏳ **SESIÓN FINALIZADA**\n\nCompletamos 4 operaciones. El bot descansará **1 HORA** para seguridad.\nMarcador: {wins}W - {loss}L", CANAL_VIP, False)
    time.sleep(3600)
