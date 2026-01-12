import time
import requests
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

# Variables de control
conteo_alertas = 0
LIMITE_ALERTAS = 4
TIEMPO_DESCANSO_HORA = 3600 # 1 hora de descanso

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# --- MENSAJE DE ARRANQUE ---
print(f"🚀 {BOT_NAME} - Asistente Personal en línea")
enviar_telegram(f"🚀 **{BOT_NAME} CONECTADO**\nAnalizando mercado con RSI 55/45.\nSesión de control manual activa.", ID_PERSONAL)

# --- BUCLE PRINCIPAL ---
while True:
    if conteo_alertas < LIMITE_ALERTAS:
        # Activos para analizar
        activos = [
            {"trading": "EURUSD", "display": "EUR/USD"},
            {"trading": "GBPUSD", "display": "GBP/USD"},
            {"trading": "USDJPY", "display": "USD/JPY"},
            {"trading": "AUDUSD", "display": "AUD/USD"},
            {"trading": "EURJPY", "display": "EUR/JPY"}
        ]
        
        for activo in activos:
            try:
                handler = TA_Handler(
                    symbol=activo['trading'],
                    exchange="FX_IDC",
                    screener="forex",
                    interval=Interval.INTERVAL_1_MINUTE
                )
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                
                # Sensibilidad Profesional (55/45)
                es_venta = rsi >= 55
                es_compra = rsi <= 45
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                    
                    # Formato de mensaje solicitado
                    msg = (f"⚠️  **ALERTA #{conteo_alertas} / {LIMITE_ALERTAS}** ⚠️\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"📢 ¿La enviamos al VIP?")
                    
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    # Espera de 2 minutos después de enviar una alerta
                    print(f"Alerta {conteo_alertas} enviada. Esperando 2 minutos...")
                    time.sleep(120) 
                    
                    if conteo_alertas >= LIMITE_ALERTAS:
                        break # Rompe el ciclo de activos para ir al descanso
            except Exception as e:
                print(f"Error analizando {activo['display']}: {e}")
                continue
            
            time.sleep(2) # Pausa entre escaneo de activos
            
    else:
        # LÓGICA DE DESCANSO (1 HORA)
        ahora = datetime.now(MI_ZONA_HORARIA)
        proxima_sesion = (ahora + timedelta(hours=1)).strftime('%I:%M %p')
        
        msg_descanso = (f"😴 **BLOQUE COMPLETADO (4/4)**\n"
                        f"──────────────────\n"
                        f"He enviado 4 señales. Entrando en descanso de 1 hora.\n"
                        f"🔄 Regreso a las: **{proxima_sesion}**")
        
        enviar_telegram(msg_descanso, ID_PERSONAL)
        print(f"Descansando hasta las {proxima_sesion}...")
        
        time.sleep(TIEMPO_DESCANSO_HORA)
        
        # Reinicio
        conteo_alertas = 0
        enviar_telegram(f"⚡ **¡DESCANSO TERMINADO!**\nBuscando nuevas oportunidades para el siguiente bloque.", ID_PERSONAL)
