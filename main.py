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
        "reply_markup": {"inline_keyboard": [[{"text": "📥 ENTRAR AL BROKER", "url": LINK_CANAL_PRINCIPAL}]]}
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

# --- INICIO DE LÓGICA ---
print(f"🚀 {BOT_NAME} Activo: Ciclos de 4 operaciones con descanso.")
wins, loss = 0, 0

while True:
    enviar_telegram(f"✅ **SESIÓN INICIADA**\n\nBuscando las próximas **4 señales** de alta precisión... 📡", CANAL_VIP)
    
    contador_ciclo = 0

    # CICLO DE 4 OPERACIONES
    while contador_ciclo < 4:
        activos = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "EURJPY"]
        
        for par in activos:
            if contador_ciclo >= 4: break # Salir si ya completó las 4 en este ciclo
            
            rsi, precio_entrada = obtener_analisis(par)
            
            if rsi:
                # NIVEL DE SEGURIDAD RSI (60/40)
                if rsi >= 60 or rsi <= 40:
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 60 else "SUBE (UP) 🟢"
                    
                    # 1. ENVIAR SEÑAL OPERATIVA
                    enviar_telegram(f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n💱 Par: {par} (OTC)\n🎯 Acción: **{direccion}**\n⏱ Tiempo: 2 Minutos\n📊 RSI: {rsi:.2f}\n\n🔥 **¡ENTRA YA!** 🔥", CANAL_VIP)
                    
                    # 2. ESPERA DE LA OPERACIÓN (2 MINUTOS)
                    time.sleep(125) 
                    
                    # 3. VERIFICACIÓN DE RESULTADO
                    _, precio_final = obtener_analisis(par)
                    if (rsi >= 60 and precio_final < precio_entrada) or (rsi <= 40 and precio_final > precio_entrada):
                        wins += 1
                        res = f"✅ **RESULTADO: WIN** ✅\nPar: {par}\nMarcador Global: {wins}W - {loss}L"
                    else:
                        loss += 1
                        res = f"❌ **RESULTADO: LOSS** ❌\nPar: {par}\nMarcador Global: {wins}W - {loss}L"
                    
                    enviar_telegram(res, CANAL_VIP)
                    enviar_telegram(f"📑 *BITÁCORA*\n{res}", CANAL_BITACORA)
                    
                    contador_ciclo += 1
                    print(f"Operación {contador_ciclo}/4 completada.")
                    time.sleep(10) # Pausa entre señales
            
        time.sleep(15) # Escaneo si no hay señales activas

    # --- DESCANSO DE SEGURIDAD (ANTIDETECCIÓN) ---
    enviar_telegram(f"⏳ **MODO ANTI-DETECCIÓN ACTIVADO**\n\nHe completado las 4 operaciones del ciclo. Para proteger las cuentas de los usuarios, el bot descansará **1 HORA**.\n\nPróximo reinicio en: 60 minutos.", CANAL_VIP)
    print("Iniciando descanso de 1 hora para evitar detección del broker...")
    
    time.sleep(3600) # 1 hora de descanso absoluto
    
    enviar_telegram(f"🚀 **REINICIANDO SESIÓN**\n\nDescanso finalizado. Buscando nuevas oportunidades... 🔥", CANAL_VIP)
