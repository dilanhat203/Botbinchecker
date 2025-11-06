import telebot
import requests
import json
import sys
import time
import datetime
import random
from colorama import init, Fore, Style

# Inicializa colorama
init(autoreset=True)

# Diccionario para guardar estadísticas por usuario
user_stats = {}
total_queries = 0
start_time = time.time()

def uptime_str(seconds: float) -> str:
    sec = int(seconds)
    days, sec = divmod(sec, 86400)
    hrs, sec = divmod(sec, 3600)
    mins, sec = divmod(sec, 60)
    if days:
        return f"{days}d {hrs:02d}:{mins:02d}:{sec:02d}"
    return f"{hrs:02d}:{mins:02d}:{sec:02d}"

def get_bin_info(bin_number: str):
    """Obtiene la información del BIN desde la API y mide el tiempo de respuesta."""
    global total_queries
    start_time_req = time.time()
    try:
        response = requests.get(f"https://data.handyapi.com/bin/{bin_number}", timeout=10)
        response.raise_for_status()
        elapsed = time.time() - start_time_req
        api = response.json()
        api["elapsed_time"] = elapsed
        total_queries += 1
        return api
    except requests.exceptions.Timeout:
        return {"Status": "ERROR", "Message": "⏰ Tiempo de espera agotado al conectar con la API."}
    except requests.exceptions.RequestException as e:
        return {"Status": "ERROR", "Message": f"❌ Error de conexión: {str(e)}"}
    except json.JSONDecodeError:
        return {"Status": "ERROR", "Message": "⚠️ Respuesta inválida del servidor."}

def get_flag(country_name: str):
    """Devuelve una bandera según el país."""
    flags = {
        # América
        "Argentina": "🇦🇷", "Bolivia": "🇧🇴", "Brazil": "🇧🇷", "Chile": "🇨🇱",
        "Colombia": "🇨🇴", "Costa Rica": "🇨🇷", "Cuba": "🇨🇺", "Dominican Republic": "🇩🇴",
        "Ecuador": "🇪🇨", "El Salvador": "🇸🇻", "Guatemala": "🇬🇹", "Honduras": "🇭🇳",
        "Mexico": "🇲🇽", "Nicaragua": "🇳🇮", "Panama": "🇵🇦", "Paraguay": "🇵🇾",
        "Peru": "🇵🇪", "Uruguay": "🇺🇾", "Venezuela": "🇻🇪", "Canada": "🇨🇦",
        "United States": "🇺🇸", "Belize": "🇧🇿", "Guyana": "🇬🇾", "Suriname": "🇸🇷",
        "Bahamas": "🇧🇸", "Barbados": "🇧🇧", "Trinidad and Tobago": "🇹🇹",

        # Europa
        "United Kingdom": "🇬🇧", "England": "🏴", "Scotland": "🏴", "Wales": "🏴",
        "Ireland": "🇮🇪", "France": "🇫🇷", "Spain": "🇪🇸", "Portugal": "🇵🇹",
        "Germany": "🇩🇪", "Italy": "🇮🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
        "Switzerland": "🇨🇭", "Austria": "🇦🇹", "Sweden": "🇸🇪", "Norway": "🇳🇴",
        "Denmark": "🇩🇰", "Finland": "🇫🇮", "Poland": "🇵🇱", "Czech Republic": "🇨🇿",
        "Slovakia": "🇸🇰", "Hungary": "🇭🇺", "Romania": "🇷🇴", "Bulgaria": "🇧🇬",
        "Greece": "🇬🇷", "Turkey": "🇹🇷", "Russia": "🇷🇺", "Russian Federation": "🇷🇺", "Ukraine": "🇺🇦",
        "Belarus": "🇧🇾", "Serbia": "🇷🇸", "Croatia": "🇭🇷", "Slovenia": "🇸🇮",
        "Lithuania": "🇱🇹", "Latvia": "🇱🇻", "Estonia": "🇪🇪", "Iceland": "🇮🇸",
        "Luxembourg": "🇱🇺", "Malta": "🇲🇹", "Cyprus": "🇨🇾", "North Macedonia": "🇲🇰",
        "Albania": "🇦🇱", "Bosnia and Herzegovina": "🇧🇦", "Montenegro": "🇲🇪",

        # África
        "South Africa": "🇿🇦", "Nigeria": "🇳🇬", "Egypt": "🇪🇬", "Morocco": "🇲🇦",
        "Tunisia": "🇹🇳", "Algeria": "🇩🇿", "Kenya": "🇰🇪", "Uganda": "🇺🇬",
        "Tanzania": "🇹🇿", "Ghana": "🇬🇭", "Senegal": "🇸🇳", "Cameroon": "🇨🇲",
        "Ethiopia": "🇪🇹", "Ivory Coast": "🇨🇮", "DR Congo": "🇨🇩", "Madagascar": "🇲🇬",
        "Zimbabwe": "🇿🇼", "Zambia": "🇿🇲", "Angola": "🇦🇴", "Mozambique": "🇲🇿",

        # Asia
        "China": "🇨🇳", "Hong Kong": "🇭🇰", "Taiwan": "🇹🇼", "Japan": "🇯🇵",
        "South Korea": "🇰🇷", "North Korea": "🇰🇵", "India": "🇮🇳", "Pakistan": "🇵🇰",
        "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰", "Nepal": "🇳🇵", "Bhutan": "🇧🇹",
        "Myanmar": "🇲🇲", "Thailand": "🇹🇭", "Vietnam": "🇻🇳", "Malaysia": "🇲🇾",
        "Singapore": "🇸🇬", "Indonesia": "🇮🇩", "Philippines": "🇵🇭", "United Arab Emirates": "🇦🇪",
        "Saudi Arabia": "🇸🇦", "Qatar": "🇶🇦", "Kuwait": "🇰🇼", "Israel": "🇮🇱",
        "Iran": "🇮🇷", "Iraq": "🇮🇶", "Jordan": "🇯🇴", "Lebanon": "🇱🇧",
        "Oman": "🇴🇲", "Yemen": "🇾🇪", "Kazakhstan": "🇰🇿", "Uzbekistan": "🇺🇿",
        "Turkmenistan": "🇹🇲", "Azerbaijan": "🇦🇿", "Georgia": "🇬🇪", "Armenia": "🇦🇲",
        "Mongolia": "🇲🇳",

        # Oceanía
        "Australia": "🇦🇺", "New Zealand": "🇳🇿", "Fiji": "🇫🇯", "Papua New Guinea": "🇵🇬",
        "Samoa": "🇼🇸", "Tonga": "🇹🇴",

        # Otros / pequeños estados
        "Singapore Republic": "🇸🇬", "Vatican City": "🇻🇦", "San Marino": "🇸🇲",
        "Monaco": "🇲🇨", "Liechtenstein": "🇱🇮", "Andorra": "🇦🇩", "Kosovo": "🇽🇰",
        "Palestine": "🇵🇸", "Czechia": "🇨🇿", "Réunion": "🇷🇪",

        # Fallbacks comunes (variantes en inglés)
        "UK": "🇬🇧", "U.S.": "🇺🇸", "UAE": "🇦🇪", "S. Korea": "🇰🇷",
        "South Korea (Republic of Korea)": "🇰🇷", "United States of America": "🇺🇸"
    }
    return flags.get(country_name, "🌍")

def luhn_check(card_number: str) -> bool:
    """
    Verifica si un número de tarjeta cumple el algoritmo de Luhn.
    Implementación clara y segura: procesa cada dígito de derecha a izquierda.
    """
    card_number = ''.join(ch for ch in card_number if ch.isdigit())
    if not card_number:
        return False

    total = 0
    num_digits = len(card_number)
    parity = num_digits % 2

    for i, ch in enumerate(card_number):
        digit = ord(ch) - ord('0')
        if i % 2 == parity:
            d = digit * 2
            if d > 9:
                d -= 9
            total += d
        else:
            total += digit

    return (total % 10) == 0

def mask_card(card_number: str) -> str:
    """Devuelve el número enmascarado: **** **** **** 1234 (mantiene solo últimos 4)"""
    digits = ''.join(ch for ch in card_number if ch.isdigit())
    if len(digits) <= 4:
        return digits
    masked = '*' * (len(digits) - 4) + digits[-4:]
    groups = [masked[max(i-4,0):i] for i in range(len(masked), 0, -4)]
    groups.reverse()
    return ' '.join(groups)

def parse_card_input(text: str):
    """
    Espera formato: numero|mes|año|cvv
    Retorna dict con keys: card, month, year, cvv o None si inválido.
    """
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    card = parts[0].strip().replace(' ', '').replace('-', '')
    month = parts[1].strip()
    year = parts[2].strip()
    cvv = parts[3].strip()

    # Validaciones básicas
    if not card.isdigit() or len(card) < 12 or len(card) > 19:
        return None
    if not month.isdigit() or not (1 <= int(month) <= 12):
        return None
    if not year.isdigit() or not (0 <= int(year) <= 9999):
        return None
    if not cvv.isdigit() or not (3 <= len(cvv) <= 4):
        return None

    # Convertir año a 4 dígitos si el usuario puso 2 (ej: 25 -> 2025 asunción común)
    y = int(year)
    if len(year) == 2:
        current_year = datetime.datetime.now().year
        prefix = current_year // 100
        y = prefix * 100 + y
    return {
        "card": card,
        "month": int(month),
        "year": int(y),
        "cvv": cvv
    }

def format_card_output(card_number: str) -> str:
    """Formatea en bloques de 4 para salida legible: '1234 5678 9012 3456'"""
    digits = ''.join(ch for ch in card_number if ch.isdigit())
    groups = [digits[i:i+4] for i in range(0, len(digits), 4)]
    return ' '.join(groups)

def main():
    print(Fore.YELLOW + Style.BRIGHT + "🔐 Introduce tu token de Telegram:")
    TOKEN = input(Fore.GREEN + Style.BRIGHT + "> ").strip()

    bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

    from telebot import types

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📚 Comandos básicos", callback_data='help_basic'))
        markup.add(types.InlineKeyboardButton("💳 Validaciones", callback_data='help_luhn'))
        markup.add(types.InlineKeyboardButton("🔧 Utilidades", callback_data='help_utils'))
        markup.add(types.InlineKeyboardButton("ℹ️ Acerca del bot", callback_data='help_about'))
        bot.reply_to(message,
            "👋 *Bienvenido al Checker BIN*\n\n"
            "Usa el comando:\n"
            "`/bin 457173`\n\n"
            "También: pulsa los botones para ver ayuda avanzada.",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('help_'))
    def help_callback(call):
        if call.data == 'help_basic':
            msg = (
                "📚 *Comandos básicos:*\n"
                "`/start` — Iniciar bot\n"
                "`/bin <número>` — Consultar BIN\n"
                "`/status` — Ver estado de la API\n"
                "`/info` — Información general"
            )
        elif call.data == 'help_luhn':
            msg = (
                "💳 *Validaciones:*\n"
                "`/lunh <tarjeta|mes|año|cvv>` — Verifica si cumple el algoritmo de Luhn.\n"
                "`/help` — Muestra esta ayuda avanzada."
            )
        elif call.data == 'help_utils':
            msg = (
                "🔧 *Utilidades varias:*\n"
                "`/mask` — Enmascara un número de tarjeta.\n"
                "`/stats` — Estadísticas personales de uso.\n"
                "`/uptime` — Tiempo activo del bot."
            )
        elif call.data == 'help_about':
            msg = (
                "ℹ️ *Sobre este bot:*\n"
                "Desarrollado por: *𝐷𝑖𝑙𝑎𝑛𝐻𝑎𝑡*\n"
                "Versión: `2.0`\n"
                "Lenguaje: Python 🐍\n"
                "API: HandyAPI BIN Lookup\n"
                "Plataforma: Telegram + Termux\n\n"
                "© 2025 DilanHat"
            )
        else:
            msg = "❌ Categoría desconocida."

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')

    @bot.message_handler(commands=['info'])
    def info_cmd(message):
        bot.reply_to(message,
            "🤖 *Bot BIN Checker*\n"
            "Versión: `2.0`\n"
            "Desarrollado por: *𝐷𝑖𝑙𝑎𝑛𝐻𝑎𝑡*\n"
            "Lenguaje: Python 🐍\n"
            "Uso: `/bin <6+ dígitos>` para consultar.\n"
        )

    @bot.message_handler(commands=['about'])
    def about_cmd(message):
        """Información técnica y créditos"""
        now = time.time()
        uptime = uptime_str(now - start_time)
        bot.reply_to(message,
            "🤖 *Acerca de este bot*\n\n"
            "• Autor: *𝐷𝑖𝑙𝑎𝑛𝐻𝑎𝑡*\n"
            "• Lenguaje: Python 3 🐍\n"
            "• Framework: pyTelegramBotAPI\n"
            "• Funciones: BIN Lookup, Luhn Checker\n"
            f"• Uptime: `{uptime}`\n"
            f"• Consultas totales (desde inicio): `{total_queries}`\n\n"
            "✨ Este bot fue creado con fines educativos, para analizar BINs, "
            "entender el algoritmo de Luhn y practicar desarrollo de bots seguros."
        )

    @bot.message_handler(commands=['status'])
    def status_cmd(message):
        bot.send_chat_action(message.chat.id, 'typing')
        start_req = time.time()
        try:
            r = requests.get("https://data.handyapi.com/bin/457173", timeout=5)
            r.raise_for_status()
            latency = (time.time() - start_req) * 1000.0
            now = time.time()
            uptime = uptime_str(now - start_time)
            bot.reply_to(message, f"📊 *Estado del bot*\n\n✅ API en línea (`{latency:.0f} ms`)\n📦 Consultas totales: `{total_queries}`\n🕒 Uptime: `{uptime}`")
        except Exception as e:
            bot.reply_to(message, f"❌ *API Inactiva o sin respuesta.*\nDetalles: `{str(e)}`")

    @bot.message_handler(commands=['bin'])
    def handle_bin(message):
        # Soporta tanto '/bin 457173' como '/bin457173'
        payload = message.text[len("/bin"):].strip()
        bin_input = payload.replace(" ", "")

        if not (bin_input.isdigit() and len(bin_input) >= 6):
            bot.reply_to(message, "⚠️ Usa `/bin` seguido de un BIN numérico de al menos *6 dígitos*.")
            return

        bot.send_chat_action(message.chat.id, 'typing')
        api = get_bin_info(bin_input)

        if api.get("Status") == "SUCCESS":
            # Contar consultas del usuario
            user_id = message.from_user.id
            user_stats[user_id] = user_stats.get(user_id, 0) + 1

            country = api["Country"].get("Name") if isinstance(api["Country"], dict) else api["Country"]
            flag = get_flag(country or "")
            brand = api.get("Scheme")
            card_type = api.get("Type")
            level = api.get("CardTier")
            bank = api.get("Issuer")
            elapsed = api.get("elapsed_time", 0)

            msg = (
                f"💳 *BIN {bin_input}*\n\n"
                f"🏦 Banco: `{bank or 'No disponible'}`\n"
                f"{flag} País: `{country or 'Desconocido'}`\n"
                f"💠 Marca: `{brand or 'Desconocida'}`\n"
                f"💳 Tipo: `{card_type or 'No disponible'}`\n"
                f"⭐ Nivel: `{level or 'No disponible'}`\n\n"
                f"⏱️ Tiempo de respuesta: `{elapsed:.2f}s`\n"
                f"📈 Consultas totales tuyas: `{user_stats[user_id]}`"
            )
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, api.get("Message", "❌ BIN no válido o no encontrado."))

    @bot.message_handler(commands=['lunh'])
    def handle_lunh(message):
        """
        Espera: /lunh 4111111111111111|12|2026|123
        O bien: /lunh 4111111111111111 | 12 | 26 | 123
        """
        payload = message.text[len("/lunh"):].strip()
        if not payload:
            bot.reply_to(message, "⚠️ Debes enviar los datos en el formato:\n`/lunh numero|mes|año|cvv`\nEj: `/lunh 4111111111111111|12|2026|123`")
            return

        parsed = parse_card_input(payload)
        if not parsed:
            bot.reply_to(message, "❌ Formato inválido o datos fuera de rango. Asegúrate de usar:\n`numero|mes|año|cvv` (ej: `4111111111111111|12|2026|123`)\n- Número entre 12 y 19 dígitos\n- Mes entre 1 y 12\n- Año razonable (ej. 2026 o 26)\n- CVV de 3 o 4 dígitos")
            return

        card = parsed["card"]
        month = parsed["month"]
        year = parsed["year"]
        cvv = parsed["cvv"]

        # Contador y stats
        user_id = message.from_user.id
        user_stats[user_id] = user_stats.get(user_id, 0) + 1

        # Validar expiración (simple)
        now = datetime.datetime.now()
        try:
            if month == 12:
                next_month = datetime.datetime(year=year+1, month=1, day=1)
            else:
                next_month = datetime.datetime(year=year, month=month+1, day=1)
            last_day_of_month = next_month - datetime.timedelta(days=1)
            expired = last_day_of_month < now
        except Exception:
            expired = False

        # Luhn
        passes_luhn = luhn_check(card)

        masked = mask_card(card)
        luhn_text = "✅ *PASA Luhn*" if passes_luhn else "❌ *NO pasa Luhn*"
        exp_text = "✅ *No expirada*" if not expired else "❌ *Expirada*"

        # CVV length suggestion
        cvv_note = "CVV OK" if (3 <= len(cvv) <= 4) else "CVV inválido"

        # Respuesta final
        msg = (
            f"💳 *Comprobación Luhn*\n\n"
            f"Tarjeta: `{masked}`\n"
            f"{luhn_text}\n"
            f"Expiración: `{month:02d}/{year}` — {exp_text}\n"
            f"CVV: `{cvv}` ({cvv_note})\n\n"
            f"ℹ️ *Nota*: Esto solo valida el algoritmo de Luhn y formato básico. "
            "No verifica saldo, validez real con el emisor ni autorización."
        )

        bot.reply_to(message, msg)

    @bot.message_handler(commands=['stats'])
    def stats_cmd(message):
        user_id = message.from_user.id
        user_count = user_stats.get(user_id, 0)
        bot.reply_to(message, f"📊 *Tus estadísticas*\n\nConsultas realizadas por ti: `{user_count}`\nConsultas totales del bot: `{total_queries}`")

    @bot.message_handler(commands=['uptime'])
    def uptime_cmd(message):
        now = time.time()
        bot.reply_to(message, f"🕒 Uptime: `{uptime_str(now - start_time)}`")

    def start_bot():
        print(Fore.CYAN + Style.BRIGHT + "✅ Bot iniciado correctamente. Esperando comandos...")
        while True:
            try:
                bot.polling(non_stop=True, timeout=60)
            except Exception as e:
                print(Fore.MAGENTA + Style.BRIGHT + f"\n⚠️ Error en conexión: {e}")
                print(Fore.YELLOW + "Reintentando en 5 segundos...")
                time.sleep(5)

    start_bot()

if __name__ == "__main__":
    main()
