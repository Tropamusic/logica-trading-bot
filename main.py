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
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def obtener_datos(simbolo):
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

# --- BUCLE PRINCIPAL 24/7 ---
print(f"🚀 {BOT_NAME} Iniciado. Esperando condiciones de mercado...")

while True:
    # Aviso de inicio de sesión
    enviar_telegram(f"✅ **SISTEMA CONECTADO**\n\nBuscando las mejores oportunidades del mercado. Prepárense para las próximas **4 señales**.", CANAL_VIP)
    
    operaciones_ciclo = 0
    wins, loss = 0, 0

    while operaciones_ciclo < 4:
        # Pares principales para mayor frecuencia
        pares = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "EURJPY"]
        
        for par in pares:
            if operaciones_ciclo >= 4: break
            
            rsi, precio_entrada = obtener_datos(par)
            
            if rsi:
                # 1. LÓGICA DE PRE-AVISO (RSI cerca del límite)
                if (rsi >= 58 and rsi < 60) or (rsi <= 42 and rsi > 40):
                    enviar_telegram(f"⚠️ **PRE-AVISO LÓGICA TRADING**\n\n💱 Par: {par} (OTC)\n🔥 El mercado está llegando a zona de entrada.\n¡Abre tu Broker!", CANAL_VIP)
                    time.sleep(15) # Tiempo para que el usuario se prepare

                # 2. SEÑAL VIP (ENTRADA CONFIRMADA)
                if rsi >= 60 or rsi <= 40:
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 60 else "SUBE (UP) 🟢"
                    
                    mensaje_señal = (f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n"
                                     f"💱 Par: {par} (OTC)\n"
                                     f"🎯 Acción: **{direccion}**\n"
                                     f"⏱ Tiempo: 2 Minutos\n"
                                     f"📊 RSI: {rsi:.2f}\n\n"
                                     f"🔥 **¡ENTRA YA AHORA!** 🔥")
                    enviar_telegram(mensaje_señal, CANAL_VIP)
                    
                    # 3. ESPERA DE LA OPERACIÓN (2 MINUTOS)
                    time.sleep(125)
                    
                    # 4. RESULTADO
                    _, precio_final = obtener_datos(par)
                    es_win = (rsi >= 60 and precio_final < precio_entrada) or (rsi <= 40 and precio_final > precio_entrada)
                    
                    if es_win:
                        wins += 1
                        res_txt = f"✅ **WIN GANADA** ✅\nPar: {par}\n¡Excelente profit para el equipo!"
                    else:
                        loss += 1
                        res_txt = f"❌ **LOSS PERDIDA** ❌\nPar: {par}\nAnalizando para la próxima entrada."
                    
                    enviar_telegram(res_txt, CANAL_VIP)
                    enviar_telegram(f"📑 *BITÁCORA*\n{res_txt}\nMarcador: {wins}W - {loss}L", CANAL_BITACORA)
                    
                    operaciones_ciclo += 1
                    time.sleep(20) # Pausa para buscar el siguiente par

        time.sleep(15) # Escaneo constante

    # --- DESCANSO DE 1 HORA (Antidetección) ---
    enviar_telegram(f"⏳ **SESIÓN FINALIZADA**\n\nCompletamos las 4 señales con éxito. El bot descansará **1 HORA** para proteger la cuenta.\n\nMarcador de sesión: {wins}W - {loss}L", CANAL_VIP)
    print("Iniciando descanso de 1 hora...")
    time.sleep(3600)
