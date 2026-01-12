import time
import requests
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_y_operar(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = float(analysis.indicators["close"]) # Aseguramos formato decimal
        
        # Niveles 60/40
        es_venta = rsi >= 60
        es_compra = rsi <= 40

        if es_compra or es_venta:
            conteo_operaciones += 1
            dir_txt = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
            
            # Mensaje de Entrada
            msg = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                   f"──────────────────\n"
                   f"💱 Par: {par_display}\n"
                   f"⏰ Tiempo: 2 Minutos\n"
                   f"📈 Operación: **{dir_txt}**\n"
                   f"──────────────────\n"
                   f"🔥 **¡ENTRA YA!** 🔥")
            enviar_telegram(msg, ID_VIP)
            enviar_telegram(msg, ID_PERSONAL)
            
            # ESPERA DE OPERACIÓN (120 seg) + MARGEN DE CIERRE (10 seg)
            time.sleep(130) 
            
            # CONSULTA DE PRECIO FINAL (Con re-intento para mayor precisión)
            nuevo_analisis = handler.get_analysis()
            precio_final = float(nuevo_analisis.indicators["close"])
            
            # LÓGICA DE GANANCIA (WIN)
            win = False
            if es_venta and precio_final < precio_entrada:
                win = True
            elif es_compra and precio_final > precio_entrada:
                win = True
            
            # MENSAJE DE RESULTADO CON PRECIOS VISIBLES
            if win:
                wins_totales += 1
                res = f"✅ **OPERACIÓN GANADORA** ✅\n💰 Profit: {par_display}"
            else:
                # Si la diferencia es casi cero, a veces es empate (DOJI), el bot lo marcará loss por seguridad
                res = f"❌ **RESULTADO: LOSS** ❌\nMejorando punto de entrada..."

            enviar_telegram(res, ID_VIP)
            
            # Bitácora detallada para que tú veas por qué dio ese resultado
            detalle = (f"📑 *BITÁCORA DE PRECIOS*\n"
                       f"📊 Par: {par_display}\n"
                       f"📥 Entrada: {precio_entrada:.5f}\n"
                       f"📤 Cierre: {precio_final:.5f}\n"
                       f"📈 RSI: {rsi:.2f}")
            enviar_telegram(detalle, ID_BITACORA)
            
            time.sleep(15) # Pequeña pausa para refrescar
            return True 
    except: pass
    return False

# --- BUCLE ---
while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    if (8 <= ahora.hour < 11) or (14 <= ahora.hour < 17) or (20 <= ahora.hour < 23):
        if conteo_operaciones < LIMITE_OPERACIONES:
            for activo in [
                {"trading": "EURUSD", "display": "EUR/USD"},
                {"trading": "GBPUSD", "display": "GBP/USD"},
                {"trading": "USDJPY", "display": "USD/JPY"},
                {"trading": "AUDUSD", "display": "AUD/USD"}
            ]:
                if analizar_y_operar(activo['trading'], activo['display']):
                    break
                time.sleep(10) # Escaneo más lento para evitar duplicados
        else:
            time.sleep(1800) # Descanso tras límite
            conteo_operaciones = 0
            wins_totales = 0
    else:
        time.sleep(60)
