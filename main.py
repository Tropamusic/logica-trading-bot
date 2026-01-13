import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
LINK_VIP = "https://t.me/+tYm_D39iB8YxZDRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- BUCLE DE ANÁLISIS CONTINUO (SIN DESCANSOS) ---
while True:
    activos = [
        {"trading": "EURUSD", "display": "EUR/USD"},
        {"trading": "GBPUSD", "display": "GBP/USD"},
        {"trading": "USDJPY", "display": "USD/JPY"},
        {"trading": "AUDUSD", "display": "AUD/USD"}
    ]
    
    for activo in activos:
        try:
            handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            precio_entrada = analysis.indicators["close"]
            
            # PRECISIÓN QUIRÚRGICA: Solo cuando toca 60/40
            es_venta = 60 <= rsi <= 65
            es_compra = 35 <= rsi <= 40
            
            if es_venta or es_compra:
                conteo_alertas += 1
                direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                
                msg = (f"🎯 **SEÑAL DE PRECISIÓN #{conteo_alertas}**\n"
                       f"──────────────────\n"
                       f"💱 Par: **{activo['display']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI actual: **{round(rsi, 2)}**\n"
                       f"⏰ Tiempo: 2 Minutos\n"
                       f"──────────────────\n"
                       f"📢 **Lógica Trading: Nivel detectado. ¡Entra ya!**")
                enviar_telegram(msg, ID_PERSONAL)
                
                # Esperar 2 minutos de la operación
                time.sleep(125) 
                
                # Verificación de resultado
                check = handler.get_analysis()
                precio_final = check.indicators["close"]
                ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                
                if ganada:
                    res_txt = f"✅ **¡WIN! NIVEL RESPETADO** ✅\n💰 Par: {activo['display']}\n🔥 *Lógica Trading: Ganancia asegurada.*"
                else:
                    res_txt = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nGestión activa. Buscando la siguiente oportunidad..."
                
                enviar_telegram(res_txt, ID_PERSONAL)
                
                # Pausa de 5 min para que el mercado se acomode y no repetir señal
                print(f"Señal enviada. Esperando 5 min para buscar la próxima...")
                time.sleep(300) 
                
        except: continue
        time.sleep(1) # Escaneo constante a máxima velocidad
