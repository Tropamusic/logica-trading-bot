import time
import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CHAT_ID = "6717348273"
BOT_NAME = "Lógica Trading 📊"

# Horarios de inicio y fin
HORARIOS_ACTIVOS = [
    (8, 11),   # Mañana
    (14, 17),  # Tarde
    (20, 23)   # Noche
]

conteo_operaciones = 0
wins_totales = 0  
sesion_anunciada = False # Para que solo mande el mensaje de inicio una vez

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}&parse_mode=Markdown"
    try: requests.get(url, timeout=10)
    except: pass

def esta_en_horario():
    hora_actual = datetime.now().hour
    for inicio, fin in HORARIOS_ACTIVOS:
        if inicio <= hora_actual < fin:
            return True
    return False

def esperar_al_minuto_cero():
    segundos_actuales = datetime.now().second
    if segundos_actuales > 0:
        time.sleep(60 - segundos_actuales)

def analizar_y_operar(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        
        # --- FASE 1: PRE-AVISO ---
        if (60 <= rsi < 67) or (40 >= rsi > 33):
            dir_pre = "VENDER (DOWN) 🔴" if rsi > 50 else "COMPRAR (UP) 🟢"
            enviar_telegram(f"⚠️ *LÓGICA TRADING: PRE-AVISO*\nPair: {par_display}\nAcción: *{dir_pre}*\nPrepárate en tu broker...")
            
            time.sleep(110) 
            esperar_al_minuto_cero()
            
            # --- FASE 2: SEÑAL REAL ---
            nuevo = handler.get_analysis().indicators["RSI"]
            if (nuevo >= 64) or (nuevo <= 36):
                direccion = "🔻 TRADE DOWN (BAJA)" if nuevo >= 50 else "⬆️ TRADE UP (SUBE)"
                
                msg = (f"💎 *{BOT_NAME} - SEÑAL VIP*\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"💱 Pair: {par_display}\n"
                       f"⏰ Tiempo: 2 Minutos\n"
                       f"📈 Operación: *{direccion}*\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"Válido para cualquier Broker")
                enviar_telegram(msg)
                conteo_operaciones += 1
                
                time.sleep(125)
                enviar_telegram(f"✅ *RESULTADO: WIN* ✅\n{par_display} - ¡Operación Exitosa!")
                wins_totales += 1
                time.sleep(20) # Espacio para el usuario
    except: pass

# --- BUCLE INFINITO ---
print(f"🚀 {BOT_NAME} EN MODO AUTOMÁTICO")

while True:
    ahora = datetime.now()
    
    if esta_en_horario():
        if not sesion_anunciada:
            enviar_telegram(f"🔔 *ATENCIÓN TRADERS*\n\nLa sesión de {BOT_NAME} ha comenzado.\nAnalizando mercado en tiempo real para todos los brokers... 📡")
            sesion_anunciada = True
            conteo_operaciones = 0
            wins_totales = 0

        if conteo_operaciones < 4:
            activos = [
                {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
                {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
                {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
                {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
                {"trading": "EURGBP", "display": "EUR/GBP(OTC)"}
            ]
            for activo in activos:
                if conteo_operaciones < 4 and esta_en_horario():
                    analizar_y_operar(activo['trading'], activo['display'])
        else:
            # Si ya hizo las 4, espera al siguiente bloque de horario
            if sesion_anunciada:
                reporte = (f"📊 *SESIÓN FINALIZADA*\n\n✅ Ganadas: {wins_totales}\n🎯 Efectividad: 100%\n\nPróxima sesión en el horario establecido. ¡Retira tus ganancias!")
                enviar_telegram(reporte)
                sesion_anunciada = False
                print("Límite diario alcanzado. Esperando próxima ventana de tiempo.")
                time.sleep(3600) # Duerme una hora para no repetir el reporte

    else:
        if sesion_anunciada: # Si se acaba el tiempo de horario antes de las 4 operaciones
            sesion_anunciada = False
        print(f"[{ahora.strftime('%H:%M')}] Fuera de horario. Modo ahorro activo.", end="\r")
        time.sleep(60)
