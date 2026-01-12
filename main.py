import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh"

def enviar_telegram(mensaje, canal_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": canal_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def obtener_analisis(simbolo):
    try:
        handler = TA_Handler(symbol=simbolo, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        return analysis.indicators["RSI"], analysis.indicators["close"]
    except:
        return None, None

# --- LÓGICA DE OPERACIÓN ---
print("🚀 Bot Iniciado: Replicando formato de señales...")

while True:
    enviar_telegram("📡 **Analizando mercado en tiempo real para todos los brokers...**", CANAL_VIP)
    
    contador_ciclo = 0
    wins, loss = 0, 0

    while contador_ciclo < 4:
        # Pares para rotación rápida
        activos = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY"]
        
        for par in activos:
            if contador_ciclo >= 4: break
            
            rsi, precio_entrada = obtener_analisis(par)
            
            if rsi:
                # 1. DETECCIÓN DE PRE-AVISO (RSI acercándose a extremos)
                if (rsi >= 58 and rsi < 60) or (rsi <= 42 and rsi > 40):
                    accion_pre = "COMPRAR (UP) 🟢" if rsi <= 42 else "VENDER (DOWN) 🔴"
                    enviar_telegram(f"⚠️ **LÓGICA TRADING: PRE-AVISO**\nPair: {par}(OTC)\nAcción: **{accion_pre}**\nPrepárate en tu broker...", CANAL_VIP)
                    time.sleep(10) # Tiempo para que el usuario abra el broker

                # 2. SEÑAL VIP (Nivel confirmado)
                if rsi >= 60 or rsi <= 40:
                    direccion = "TRADE DOWN (BAJA) 🔻" if rsi >= 60 else "TRADE UP (SUBE) 🟢"
                    
                    # ENVIAR SEÑAL VIP (Como en el capture)
                    mensaje_vip = (f"💎 **Lógica Trading 📊 - SEÑAL VIP**\n"
                                   f"──────────────────\n"
                                   f"💱 Pair: {par}(OTC)\n"
                                   f"⏰ Tiempo: 2 Minutos\n"
                                   f"📈 Operación: **{direccion}**\n"
                                   f"──────────────────\n"
                                   f"Válido para cualquier Broker")
                    enviar_telegram(mensaje_vip, CANAL_VIP)
                    
                    # 3. ESPERA DE OPERACIÓN
                    time.sleep(125) 
                    
                    # 4. RESULTADO
                    _, precio_final = obtener_analisis(par)
                    es_win = (rsi >= 60 and precio_final < precio_entrada) or (rsi <= 40 and precio_final > precio_entrada)
                    
                    if es_win:
                        wins += 1
                        res_msg = f"✅ **RESULTADO: WIN** ✅\n{par}(OTC) - ¡Operación Exitosa!"
                    else:
                        loss += 1
                        res_msg = f"❌ **RESULTADO: LOSS** ❌\n{par}(OTC) - Intenta la próxima."
                    
                    enviar_telegram(res_msg, CANAL_VIP)
                    enviar_telegram(f"📑 *BITÁCORA*\n{res_msg}\nMarcador: {wins}W - {loss}L", CANAL_BITACORA)
                    
                    contador_ciclo += 1
                    time.sleep(30) # Pausa entre señales para no saturar

        time.sleep(15)

    # --- DESCANSO DE 1 HORA ---
    enviar_telegram(f"⏳ **SESIÓN FINALIZADA**\n\nSe cumplieron las 4 operaciones. Descanso de seguridad de **1 HORA** activado.", CANAL_VIP)
    time.sleep(3600)
