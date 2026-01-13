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

# --- BUCLE DE ANÁLISIS PROFESIONAL ---
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
                
                # NIVELES DE SEGURIDAD PARA DINERO REAL (60/40)
                es_venta = rsi >= 60  
                es_compra = rsi <= 40 
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                    
                    # Mensaje de Entrada
                    msg = (f"⚠️  **NUEVA SEÑAL #{conteo_alertas} / {LIMITE_ALERTAS}** ⚠️\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"📢 **Opera con responsabilidad. Gestión de riesgo activa.**")
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    # Espera de operación (2 min)
                    time.sleep(125) 
                    
                    # Verificación de Resultado
                    check = handler.get_analysis()
                    precio_final = check.indicators["close"]
                    ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                    
                    if ganada:
                        res_msg = f"✅ **RESULTADO: ¡WIN!** ✅\n💰 Par: {activo['display']}\n🔥 *¡Sube tu captura al VIP, Lógica Trading!*"
                    else:
                        res_msg = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nTranquilo, la disciplina es la clave del éxito."
                    
                    enviar_telegram(res_msg, ID_PERSONAL)
                    
                    if conteo_alertas < LIMITE_ALERTAS:
                        time.sleep(300) # 5 min entre alertas
                    
            except: continue
            time.sleep(2)
    else:
        # --- DESCANSO Y PRE-AVISO ---
        reinicio_dt = datetime.now(MI_ZONA_HORARIA) + timedelta(minutes=TIEMPO_DESCANSO_MINUTOS)
        reinicio_str = reinicio_dt.strftime('%I:%M %p')
        
        enviar_telegram(f"😴 **BLOQUE COMPLETADO**\nSesión cerrada con {LIMITE_ALERTAS} alertas.\nRegresamos a las: **{reinicio_str}**", ID_PERSONAL)
        
        time.sleep(1500) # Espera 25 min
        
        enviar_telegram(f"⏳ **¡PREPARADOS!**\nFaltan **5 MINUTOS** para el próximo bloque de Lógica Trading. Abran sus brokers.", ID_PERSONAL)
        
        time.sleep(300) # Espera 5 min finales
        conteo_alertas = 0 
