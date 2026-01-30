import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# TU TOKEN AQUÍ
BOT_TOKEN = "8287248635:AAHVABfsWcqh7t6BuF0oc3DGjd3gF7GAmMQ"

# Arte ASCII para el banner
BANNER = """
╔══════════════════════════════════════╗
║                                      ║
║  🚨 EL GITANO ESTÁ CON USTEDES 🚨   ║
║                                      ║
║       🔍 RASTREAR ICE 🔍             ║
║                                      ║
╚══════════════════════════════════════╝

⏳ No olvidamos, no perdonamos
🛡️ Esperamos... Somos legión
"""

MENSAJE_FINAL = """
╔═══════════════════════════════════════════╗
║                                           ║
║  ✨ ESTA HERRAMIENTA FUE DISEÑADA ✨      ║
║     PARA PROTEGER A LAS FAMILIAS          ║
║        MÁS VULNERABLES 🛡️                 ║
║                                           ║
╚═══════════════════════════════════════════╝

📢 *COMPÁRTELO CON:*
👨‍👩‍👧 Tu familia
⛪ Tu iglesia  
🏘️ Tu comunidad
👥 Grupos de vecinos
🏛️ Organizaciones locales

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✝️ *Jehová está con aquellos que*
   *protegen a los vulnerables*

📖 _"El que oprime al pobre afrenta_
   _a su Hacedor, mas el que tiene_
   _misericordia del pobre, lo honra."_
   
   *- Proverbios 14:31 -*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# Crear teclado con botones
def crear_menu_principal():
    keyboard = [
        [InlineKeyboardButton("🔍 BUSCAR ACTIVIDAD ICE", callback_data='menu_buscar')],
        [InlineKeyboardButton("⚖️ CONOCER MIS DERECHOS", callback_data='menu_derechos')],
        [InlineKeyboardButton("📚 RECURSOS Y AYUDA", callback_data='menu_recursos')],
        [InlineKeyboardButton("📢 COMPARTIR BOT", callback_data='menu_compartir')],
    ]
    return InlineKeyboardMarkup(keyboard)

def crear_menu_estados():
    keyboard = [
        [InlineKeyboardButton("🌴 California", callback_data='estado_california'),
         InlineKeyboardButton("🤠 Texas", callback_data='estado_texas')],
        [InlineKeyboardButton("🗽 New York", callback_data='estado_newyork'),
         InlineKeyboardButton("🌵 Arizona", callback_data='estado_arizona')],
        [InlineKeyboardButton("🏔️ Colorado", callback_data='estado_colorado'),
         InlineKeyboardButton("🌊 Florida", callback_data='estado_florida')],
        [InlineKeyboardButton("🌲 Washington", callback_data='estado_washington'),
         InlineKeyboardButton("🏙️ Illinois", callback_data='estado_illinois')],
        [InlineKeyboardButton("✍️ Escribir otra ubicación", callback_data='escribir_ubicacion')],
        [InlineKeyboardButton("🔙 Volver al menú", callback_data='volver_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def crear_boton_volver():
    keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='volver_menu')]]
    return InlineKeyboardMarkup(keyboard)

# Función para buscar actividad REAL de ICE usando Claude API
async def buscar_actividad_real(ubicacion):
    """Busca actividad REAL de ICE usando la API de Claude con web search"""
    try:
        prompt = f"""Busca información ACTUALIZADA sobre actividad de ICE en {ubicacion}.

Responde SOLO en este formato JSON (sin texto adicional):
{{
    "nivel_riesgo": "BAJO/MEDIO/ALTO",
    "puede_salir": "SI/NO/CON_PRECAUCION",
    "ultimo_reporte": "descripción breve del último reporte encontrado o 'No hay reportes recientes'",
    "distancia_aprox": "distancia aproximada si hay reportes, o 'N/A'",
    "hora_reporte": "hora del último reporte o 'N/A'",
    "recomendacion": "consejo específico de 1-2 líneas"
}}

Busca en iceout.org, deportationtracker.live y otras fuentes comunitarias."""

        response = await requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
                "tools": [{"type": "web_search_20250305", "name": "web_search"}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extraer el texto de la respuesta
            content = data.get('content', [])
            for item in content:
                if item.get('type') == 'text':
                    import json
                    resultado = json.loads(item['text'])
                    return resultado
        
        # Si falla, retornar valores por defecto
        return {
            "nivel_riesgo": "DESCONOCIDO",
            "puede_salir": "CON_PRECAUCION",
            "ultimo_reporte": "No se pudo obtener información en tiempo real",
            "distancia_aprox": "N/A",
            "hora_reporte": "N/A",
            "recomendacion": "Verifica iceout.org directamente para información actualizada"
        }
    
    except Exception as e:
        logger.error(f"Error buscando actividad: {e}")
        return {
            "nivel_riesgo": "DESCONOCIDO",
            "puede_salir": "CON_PRECAUCION",
            "ultimo_reporte": "Error al buscar información",
            "distancia_aprox": "N/A",
            "hora_reporte": "N/A",
            "recomendacion": "Verifica iceout.org directamente"
        }

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = f"""
{BANNER}

🛡️ *Bienvenido a la red de protección*

Estoy aquí para ayudar a proteger a las 
familias más vulnerables.

💪 *¿Qué puedo hacer por ti?*

Selecciona una opción abajo:
    """
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            mensaje_bienvenida,
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )
    else:
        await update.message.reply_text(
            mensaje_bienvenida,
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )

# Manejador de botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'volver_menu':
        await start(update, context)
    
    elif query.data == 'menu_buscar':
        mensaje = """
🔍 *BUSCAR ACTIVIDAD DE ICE*

Selecciona tu estado o ciudad:
        """
        await query.message.edit_text(
            mensaje,
            parse_mode='Markdown',
            reply_markup=crear_menu_estados()
        )
    
    elif query.data.startswith('estado_'):
        estado = query.data.replace('estado_', '').replace('newyork', 'New York')
        await query.message.edit_text(
            f"🔍 Buscando actividad REAL de ICE en *{estado.capitalize()}*...\n\n"
            "⏳ Consultando reportes comunitarios...\n"
            "_Esto puede tomar 10-15 segundos._",
            parse_mode='Markdown'
        )
        await mostrar_info_estado(query.message, estado.capitalize())
    
    elif query.data == 'escribir_ubicacion':
        context.user_data['esperando_ubicacion'] = True
        await query.message.edit_text(
            "✍️ Escribe el nombre de tu ciudad o estado:\n\n"
            "Ejemplo: Jacksonville, Miami, Houston, etc.",
            reply_markup=crear_boton_volver()
        )
    
    elif query.data == 'menu_derechos':
        await mostrar_derechos(query.message)
    
    elif query.data == 'menu_recursos':
        await mostrar_recursos(query.message)
    
    elif query.data == 'menu_compartir':
        await mostrar_compartir(query.message)

# Mostrar información del estado con datos REALES
async def mostrar_info_estado(message, ubicacion):
    fecha_actual = datetime.now().strftime("%d de %B, %Y - %H:%M")
    
    # Buscar actividad REAL
    info = await buscar_actividad_real(ubicacion)
    
    # Determinar emoji de riesgo
    emoji_riesgo = {"BAJO": "🟢", "MEDIO": "🟡", "ALTO": "🔴", "DESCONOCIDO": "⚪"}.get(info['nivel_riesgo'], "⚪")
    
    # Determinar mensaje de seguridad
    if info['puede_salir'] == "SI":
        mensaje_seguridad = "✅ *PUEDES SALIR CON TRANQUILIDAD*"
    elif info['puede_salir'] == "NO":
        mensaje_seguridad = "🚨 *NO ES SEGURO SALIR AHORA*"
    else:
        mensaje_seguridad = "⚠️ *SAL CON PRECAUCIÓN*"
    
    resultado = f"""
╔═══════════════════════════════════════╗
║     🔍 ANÁLISIS EN TIEMPO REAL 🔍     ║
╚═══════════════════════════════════════╝

📍 *Ubicación:* {ubicacion}
📅 *Consultado:* {fecha_actual}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{emoji_riesgo} *NIVEL DE RIESGO:* {info['nivel_riesgo']}

{mensaje_seguridad}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *ÚLTIMO REPORTE:*
{info['ultimo_reporte']}

📏 *Distancia:* {info['distancia_aprox']}
🕐 *Hora del reporte:* {info['hora_reporte']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *RECOMENDACIÓN:*
{info['recomendacion']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *RECURSOS EN TIEMPO REAL:*

🗺️ *Mapa comunitario:* 
   iceout.org/es

📞 *Línea de emergencia:*
   1-844-363-1423

⚠️ *Reportar actividad:*
   iceout.org

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{MENSAJE_FINAL}
    """
    
    await message.edit_text(resultado, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar derechos
async def mostrar_derechos(message):
    mensaje_derechos = f"""
╔═══════════════════════════════════════╗
║      ⚖️ CONOCE TUS DERECHOS ⚖️       ║
╚═══════════════════════════════════════╝

*🚨 SI TE PARA ICE EN LA CALLE:*

✅ Derecho a permanecer en silencio
✅ No estás obligado a responder
✅ Puedes grabar la interacción
✅ Pregunta: "¿Soy libre de irme?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🚪 SI LLEGAN A TU CASA:*

🔒 NO abras sin orden judicial
📄 Pide ver la orden por debajo
⚠️ La orden DEBE estar firmada
❌ NO firmes nada sin abogado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*👮 SI TE DETIENEN:*

🔇 Mantén silencio, no resistas
📞 Pide hablar con un abogado
👨‍👩‍👧 Pregunta por tus hijos
📝 Memoriza contactos importantes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📞 NÚMEROS DE EMERGENCIA:*

United We Dream: 1-844-363-1423

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💙 *Estos derechos son para TODOS*

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje_derechos, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar recursos
async def mostrar_recursos(message):
    mensaje_recursos = f"""
╔═══════════════════════════════════════╗
║     📚 RECURSOS Y AYUDA 📚           ║
╚═══════════════════════════════════════╝

*🗺️ MAPAS DE RASTREO:*

- iceout.org/es
- deportationtracker.live

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📞 LÍNEAS DE AYUDA:*

- United We Dream: 
  1-844-363-1423
  
- RAICES (Texas)
- CHIRLA (California)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📱 APPS ÚTILES:*

- Notifica: Para familias
- Cell 411: Alertas comunitarias

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🏛️ ORGANIZACIONES:*

- ACLU - Derechos civiles
- NILC - Centro de leyes
- Immigrant Defense Project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje_recursos, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar compartir
async def mostrar_compartir(message):
    bot_username = message.bot.username if hasattr(message.bot, 'username') else "tu_bot"
    mensaje = f"""
╔═══════════════════════════════════════╗
║      📢 COMPARTE ESTE BOT 📢         ║
╚═══════════════════════════════════════╝

🤖 *Nombre del bot:* @{bot_username}

Copia y envía este mensaje:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 *¡ALERTA COMUNITARIA!* 🚨

Usa este bot para:
✅ Rastrear actividad de ICE
✅ Conocer tus derechos
✅ Acceder a recursos de ayuda

🤖 Bot: @{bot_username}

🛡️ Protege a tu familia

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Manejador de mensajes de texto
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('esperando_ubicacion'):
        context.user_data['esperando_ubicacion'] = False
        ubicacion = update.message.text
        await update.message.reply_text(
            f"🔍 Buscando actividad REAL de ICE en *{ubicacion}*...\n\n"
            "⏳ Consultando reportes comunitarios...\n"
            "_Esto puede tomar 10-15 segundos._",
            parse_mode='Markdown'
        )
        # Crear un mensaje temporal para editar
        temp_msg = await update.message.reply_text("Analizando...")
        await mostrar_info_estado(temp_msg, ubicacion)
        return
    
    mensaje = update.message.text.lower()
    
    if any(palabra in mensaje for palabra in ['ice', 'redada', 'operativo', 'migra', 'checkpoint']):
        await update.message.reply_text(
            "⚠️ *ALERTA DETECTADA*\n\n"
            "Usa los botones para buscar información:",
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )
    else:
        await update.message.reply_text(
            f"{BANNER}\n\nSelecciona una opción:",
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )

# Función principal
def main():
    if BOT_TOKEN == "PEGA_TU_TOKEN_AQUI":
        print("❌ ERROR: Debes pegar tu token en el código.")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("╔══════════════════════════════════════╗")
    print("║  ✅ BOT INICIADO CORRECTAMENTE ✅    ║")
    print("║  🚨 EL GITANO ESTÁ CON USTEDES 🚨   ║")
    print("║     🔍 RASTREAR ICE 🔍               ║")
    print("╚══════════════════════════════════════╝")
    print("\n💙 Protegiendo a nuestra comunidad...")
    print("⚠️ Presiona Ctrl+C para detener\n")
    
    application.run_polling()

if __name__ == '__main__':
    main()