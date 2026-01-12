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
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 1800 
aviso_enviado = False

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_y_operar(par_trading, par_display):
    """
    Esta función analiza un par. Si encuentra señal, gestiona TODO el proceso
    y devuelve True para que el bot sepa que ya operó.
    """
    global conteo_operaciones, wins_totales
    
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # SENSIBILIDAD 60/40
        es_venta = rsi >= 60
        es_compra = rsi <= 40

        if es_compra or es_venta:
            direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
            
            msg = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                   f"──────────────────\n"
                   f"💱 Par: {par_display}\n"
                   f"⏰ Tiempo: 2 Minutos\n"
                   f"📈 Operación: **{direccion}**\n"
                   f"──────────────────\n"
                   f"🔥 **¡ENTRA YA AHORA!** 🔥")
            
            enviar_telegram(msg, ID_VIP)
            enviar_telegram(msg, ID_PERSONAL)
            
            # 1. Aumentamos el conteo inmediatamente
            conteo_operaciones += 1
            
            # 2. Espera total de la operación (125 seg)
            # Durante este tiempo, el bot NO analizará otros pares
            time.sleep(125) 
            
            # 3. Verificación de resultado
            p_final = handler.get_analysis().indicators["close"]
            win = (es_venta and p_final < precio_entrada) or (es_compra and p_final > precio_entrada)
            
            res_msg = "✅ **OPERACIÓN GANADORA** ✅" if win else "❌ **RESULTADO: LOSS** ❌"
            if win: wins_totales += 1
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\n📊 {par_display} | E: {precio_entrada:.5f} -> S: {p_final:.5f}", ID_BITACORA)
            
            # 4. Pausa de enfriamiento tras la operación
            time.sleep(30)
            return True # Indica que se realizó una operación
            
    except: pass
    return False

# --- ACTIVOS ---
activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

# --- BUCLE MAESTRO ---
while True:
    ahora_vzla = datetime.now(MI_ZONA_HORARIA)
    hora = ahora_vzla.hour
    minuto = ahora_vzla.minute

    # Lógica de Aviso 5 min antes
    if (hora in [7, 13, 19]) and (minuto == 55) and not aviso_enviado:
        enviar_telegram(f"⏳ **¡PREPÁRENSE! 5 MINUTOS...**\nLa sesión de {BOT_NAME} está por iniciar. 🚀", ID_VIP)
        aviso_enviado = True
    if minuto == 0: aviso_enviado = False

    # Horarios: 8-11, 14-17, 20-23
    es_hora_operativa = (8 <= hora < 11) or (14 <= hora < 17) or (20 <= hora < 23)

    if es_hora_operativa:
        if conteo_operaciones >= LIMITE_OPERACIONES:
            # Reporte de cierre de sesión
            h_regreso = (ahora_vzla + timedelta(minutes=30)).strftime('%I:%M %p')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n"
                       f"❌ Perdidas: {LIMITE_OPERACIONES - wins_totales}\n\n"
                       f"⏳ Próxima sesión: **{h_regreso} (Vzla/EST)**")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO)
            conteo_operaciones = 0
            wins_totales = 0
        else:
            # Escaneo secuencial (Uno por uno)
            for activo in activos:
                # Si ya llegamos al límite en este ciclo, paramos
                if conteo_operaciones >= LIMITE_OPERACIONES:
                    break
                
                # Intentamos operar este activo
                opero = analizar_y_operar(activo['trading'], activo['display'])
                
                # Si operó, rompemos el ciclo 'for' para volver al 'while' 
                # y re-escanear todo desde el principio. ¡ESTO EVITA DUPLICADOS!
                if opero:
                    break
                
                time.sleep(5) # Pausa entre escaneo de diferentes pares
    else:
        time.sleep(60) # Fuera de horario espera un minuto para re-chequear
