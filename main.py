import time
import requests
import threading
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
LINK_VIP = "https://t.me/+tYm_D39iB8YxZDRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
LIMITE_ALERTAS = 4
TIEMPO_DESCANSO_MINUTOS = 30

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- BUCLE DE ANÁLISIS DE PRECISIÓN ---
while True:
    if conteo_alertas < LIMITE_ALERTAS:
        activos = [
            {"trading": "EURUSD", "display": "EUR/USD"},
            {"trading": "GBPUSD", "display": "GBP/USD"},
            {"trading": "USDJPY", "display": "USD/JPY"},
            {"trading": "AUDUSD", "display": "AUD/USD"}
        ]
        
        for activo in activos:
            if conteo_alertas >= LIMITE_ALERTAS: break
            
            try:
                handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio_entrada = analysis.indicators["close"]
                
                # AJUSTE DE PRECISIÓN: Solo entra si está entre 60-65 o 35-40
                # Esto evita señales cuando el RSI ya se disparó a 70+ o bajó de 30
                es_venta = 60 <= rsi <= 65
                es_compra = 35 <= rsi <= 40
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                    
                    # Mensaje Profesional
                    msg = (f"🎯 **SEÑAL DE PRECISIÓN #{conteo_alertas}**\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"📊 RSI actual: **{round(rsi, 2)}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"📢 **Entra justo ahora. ¡Nivel 60/40 alcanzado!**")
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    time.sleep(125) # Espera 2 min
                    
                    # Verificación
                    check = handler.get_analysis()
                    precio_final = check.indicators["close"]
                    ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                    
                    if ganada:
                        res_msg = f"✅ **¡WIN! NIVEL RESPETADO** ✅\n💰 Par: {activo['display']}\n🔥 *Lógica Trading: Precisión total.*"
                    else:
                        res_msg = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nEl mercado rompió el nivel. Seguimos con gestión."
                    
                    enviar_telegram(res_msg, ID_PERSONAL)
                    
                    if conteo_alertas < LIMITE_ALERTAS:
                        time.sleep(300) 
                    
            except: continue
            time.sleep(1) # Escaneo más rápido para no perder el "toque"
    else:
        # Lógica de descanso de 30 min (con pre-aviso de 5 min)
        reinicio_dt = datetime.now(MI_ZONA_HORARIA) + timedelta(minutes=TIEMPO_DESCANSO_MINUTOS)
        enviar_telegram(f"😴 **SESIÓN COMPLETADA**\nRegresamos a las: **{reinicio_dt.strftime('%I:%M %p')}**", ID_PERSONAL)
        time.sleep(1500) 
        enviar_telegram(f"⏳ **¡PRE-ALERTA!**\nEn **5 MINUTOS** iniciamos nuevas señales de precisión.", ID_PERSONAL)
        time.sleep(300)
        conteo_alertas = 0
