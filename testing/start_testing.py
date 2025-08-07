#!/usr/bin/env python3
"""
Скрипт для запуска тестирования чат-бота
"""

import subprocess
import time
import sys
import os
import signal
import psutil
from pathlib import Path

def kill_process_on_port(port):
    """Убивает процесс на указанном порту"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        print(f"🔄 Останавливаю процесс на порту {port} (PID: {proc.pid})")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except Exception as e:
        print(f"⚠️ Не удалось остановить процесс на порту {port}: {e}")
    return False

def check_dependencies():
    """Проверка зависимостей"""
    try:
        import fastapi
        import streamlit
        import uvicorn
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: uv sync")
        return False

def start_api():
    """Запуск API сервера"""
    print("🚀 Запуск API сервера...")
    
    # Проверяем и освобождаем порт 8000
    if kill_process_on_port(8000):
        time.sleep(2)
    
    try:
        # Запускаем API в фоновом режиме
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "testing.api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], cwd=Path(__file__).parent.parent)
        
        # Ждем запуска
        time.sleep(5)
        
        # Проверяем что API работает
        import requests
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("✅ API сервер запущен на http://localhost:8000")
                return api_process
            else:
                print("❌ API сервер не отвечает")
                api_process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ API сервер не отвечает")
            api_process.terminate()
            return None
    except Exception as e:
        print(f"❌ Ошибка запуска API: {e}")
        return None

def start_ui():
    """Запуск Streamlit UI"""
    print("🎨 Запуск Streamlit UI...")
    
    # Проверяем и освобождаем порт 8501
    if kill_process_on_port(8501):
        time.sleep(2)
    
    try:
        # Запускаем Streamlit
        ui_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "testing/ui.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ], cwd=Path(__file__).parent.parent)
        
        # Ждем запуска
        time.sleep(8)
        
        # Проверяем что UI работает
        import requests
        try:
            response = requests.get("http://localhost:8501", timeout=10)
            if response.status_code == 200:
                print("✅ Streamlit UI запущен на http://localhost:8501")
                return ui_process
            else:
                print("❌ Streamlit UI не отвечает")
                ui_process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ Streamlit UI не отвечает")
            ui_process.terminate()
            return None
    except Exception as e:
        print(f"❌ Ошибка запуска UI: {e}")
        return None

def cleanup_processes():
    """Очистка процессов при завершении"""
    print("\n🛑 Остановка сервисов...")
    
    # Убиваем процессы на наших портах
    kill_process_on_port(8000)
    kill_process_on_port(8501)
    
    print("✅ Сервисы остановлены")

def main():
    """Основная функция"""
    print("🤖 Foster Family Resource Bot Testing")
    print("=" * 50)
    
    # Регистрируем обработчик для graceful shutdown
    def signal_handler(signum, frame):
        cleanup_processes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Проверяем зависимости
    if not check_dependencies():
        return
    
    # Запускаем API
    api_process = start_api()
    if not api_process:
        print("❌ Не удалось запустить API")
        return
    
    # Запускаем UI
    ui_process = start_ui()
    if not ui_process:
        print("❌ Не удалось запустить UI")
        api_process.terminate()
        return
    
    print("\n🎉 Тестирование готово!")
    print("📋 Доступные URL:")
    print("   • API: http://localhost:8000")
    print("   • UI: http://localhost:8501")
    print("   • API Docs: http://localhost:8000/docs")
    print("\n💡 Для остановки нажмите Ctrl+C")
    
    try:
        # Ждем завершения
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main() 