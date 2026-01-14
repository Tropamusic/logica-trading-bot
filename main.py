import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# LOS ACTIVOS DE LOS PROFESIONALES (Alta liquidez, sin enfoque en JPY)
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO (MÁXIMA VOLATILIDAD) ✨"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD (LIQUIDEZ PURA) 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD (EL CABLE) 🇬🇧"},
    {"symbol": "BTCUSD", "ex": "BITSTAMP", "n": "BITCOIN (24/7) ₿"},
    {"symbol": "US30", "ex": "CURRENCYCOM", "n": "DOW JONES (INSTITUCIONAL) 🇺🇸"},
    {"symbol": "USOIL", "ex": "TVC", "n": "PETRÓLEO WTI 🛢️"}
]

print("🚀 LÓGICA TRADING: Bot de Acción del Precio Activado.")
print("💎 Analizando niveles críticos de soporte y resistencia...")

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"})
    except: pass

while True:
    try:
        for a in activos:
            # Analizamos en 1 minuto para señales rápidas
            handler = TA_Handler(
                symbol=a['symbol'],
                exchange=a['ex'],
                screener="forex" if "USD" in a['symbol'] else "crypto" if "BTC" in a['symbol'] else "cfd",
                interval=Interval.INTERVAL_1_MINUTE
            )
            
            analisis = handler.get_analysis()
            resumen = analisis.summary # Los profesionales miran el RESUMEN de fuerza
            precio = analisis.indicators["close"]
            
            # MOSTRAR EN CONSOLA PARA VER QUE ESTÁ VIVO
            print(f"📡 {a['n']}: {resumen['RECOMMENDATION']} | Precio: {precio}")

            # LÓGICA PROFESIONAL: Solo entramos cuando hay "FUERTE" (Strong)
            # Esto significa que múltiples indicadores de precio coinciden
            if "STRONG" in resumen['RECOMMENDATION']:
                tipo = resumen['RECOMMENDATION'] # "STRONG_BUY" o "STRONG_SELL"
                dir_msg = "COMPRA (UP) 🟢" if "BUY" in tipo else "VENTA (DOWN) 🔻"
                
                msg = (f"🔥 **¡ALERTA PROFESIONAL: {a['n']}!**\n"
                       f"──────────────────\n"
                       f"📈 Acción: **{dir_msg}**\n"
                       f"💵 Precio Real: `{precio}`\n"
                       f"⚡ Fuerza: **INSTITUCIONAL**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *Lógica Trading: Operando con el flujo del dinero.*")
                
                enviar_telegram(msg)
                print(f"✅ SEÑAL ENVIADA EN {a['symbol']}. Pausando 2 min para no saturar...")
                time.sleep(125) # Tu regla de oro: 2 min de experiencia
                break 

    except Exception as e:
        print(f"⚠️ Reconectando con mercado real...")
        time.sleep(5)
        continue
    
    time.sleep(2) # Escaneo constante
