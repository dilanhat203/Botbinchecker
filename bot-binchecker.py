import telebot
import requests
import json
import sys
import time
from colorama import init, Fore, Style

# Inicializa colorama
init(autoreset=True)

# Diccionario para guardar estadísticas por usuario
user_stats = {}

def get_bin_info(bin_number: str):
    """Obtiene la información del BIN desde la API y mide el tiempo de respuesta."""
    start_time = time.time()
    try:
        response = requests.get(f"https://data.handyapi.com/bin/{bin_number}", timeout=10)
        response.raise_for_status()
        elapsed = time.time() - start_time
        api = response.json()
        api["elapsed_time"] = elapsed
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
        "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Chile": "🇨🇱", "United States": "🇺🇸", 
        "Mexico": "🇲🇽", "Spain": "🇪🇸", "France": "🇫🇷", "Italy": "🇮🇹", 
        "Germany": "🇩🇪", "United Kingdom": "🇬🇧", "Canada": "🇨🇦"
    }
    return flags.get(country_name, "🌍")

def main():
    print(Fore.YELLOW + Style.BRIGHT + "🔐 Introduce tu token de Telegram:")
    TOKEN = input(Fore.GREEN + Style.BRIGHT + "> ").strip()

    bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, 
            "👋 *Bienvenido al Checker BIN*\n\n"
            "Usa el comando:\n"
            "`/bin 457173`\n\n"
            "para obtener la información del BIN solicitado.\n\n"
            "Otros comandos útiles:\n"
            "`/info` – Sobre el bot\n"
            "`/status` – Estado de la API\n"
        )

    @bot.message_handler(commands=['info'])
    def info_cmd(message):
        bot.reply_to(message,
            "🤖 *Bot BIN Checker*\n"
            "Versión: `2.0`\n"
            "Desarrollado por: *𝐷𝑖𝑙𝑎𝑛𝐻𝑎𝑡*\n"
            "Lenguaje: Python 🐍\n"
            "Uso: `/bin <6+ dígitos>` para consultar.\n"
        )

    @bot.message_handler(commands=['status'])
    def status_cmd(message):
        bot.send_chat_action(message.chat.id, 'typing')
        start = time.time()
        try:
            r = requests.get("https://data.handyapi.com/bin/457173", timeout=5)
            r.raise_for_status()
            latency = time.time() - start
            bot.reply_to(message, f"✅ *API Activa*\nTiempo de respuesta: `{latency:.2f} segundos` ⚡")
        except Exception as e:
            bot.reply_to(message, f"❌ *API Inactiva o sin respuesta.*\nDetalles: `{str(e)}`")

    @bot.message_handler(commands=['bin'])
    def handle_bin(message):
        bin_input = message.text[len("/bin "):].strip().replace(" ", "")

        if not (bin_input.isdigit() and len(bin_input) >= 6):
            bot.reply_to(message, "⚠️ Usa `/bin` seguido de un BIN numérico de al menos *6 dígitos*.")
            return

        bot.send_chat_action(message.chat.id, 'typing')
        api = get_bin_info(bin_input)

        if api.get("Status") == "SUCCESS":
            # Contar consultas del usuario
            user_id = message.from_user.id
            user_stats[user_id] = user_stats.get(user_id, 0) + 1

            country = api["Country"]["Name"]
            flag = get_flag(country)
            brand = api["Scheme"]
            card_type = api["Type"]
            level = api["CardTier"]
            bank = api["Issuer"]
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
