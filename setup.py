"""
اسکریپت نصب و راه‌اندازی اولیه
Setup and Initialization Script
"""

import os
import json
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'data/uploads',
        'data/whiteboards',
        'data/screen_share',
        'modules'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ پوشه {directory} ایجاد شد")

def create_initial_data_files():
    """Create initial data files"""
    
    # Users file
    users_file = Path('data/users.json')
    if not users_file.exists():
        default_users = {
            "admin": {
                "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # admin123
                "role": "مدرس",
                "full_name": "مدیر سیستم"
            },
            "teacher1": {
                "password": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",  # teacher123
                "role": "مدرس",
                "full_name": "معلم اول"
            },
            "student1": {
                "password": "53d024d60e9ab2b2cc6a7f4c4b8a3b8a6b31d62cf3a91c6f4a04e4e5b5e60e3f",  # student123
                "role": "دانش‌آموز",
                "full_name": "دانش‌آموز اول"
            }
        }
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)
        print("✓ فایل کاربران ایجاد شد")
    
    # Other data files
    data_files = [
        'data/rooms.json',
        'data/chats.json',
        'data/files.json',
        'data/polls.json',
        'data/breakout_rooms.json',
        'data/recordings.json'
    ]
    
    for file_path in data_files:
        file = Path(file_path)
        if not file.exists():
            with open(file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)
            print(f"✓ فایل {file.name} ایجاد شد")

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 بررسی وابستگی‌ها...")
    
    required_packages = [
        'streamlit',
        'streamlit_drawable_canvas',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} نصب شده است")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} نصب نشده است")
    
    if missing_packages:
        print("\n⚠️ لطفاً ابتدا وابستگی‌ها را نصب کنید:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("راه‌اندازی پلتفرم آموزش آنلاین")
    print("Online Teaching Platform Setup")
    print("=" * 60)
    print()
    
    print("📁 ایجاد ساختار پوشه‌ها...")
    create_directories()
    
    print("\n📄 ایجاد فایل‌های اولیه...")
    create_initial_data_files()
    
    if check_dependencies():
        print("\n" + "=" * 60)
        print("✅ راه‌اندازی با موفقیت انجام شد!")
        print("=" * 60)
        print("\nبرای اجرای برنامه دستور زیر را وارد کنید:")
        print("streamlit run main.py")
        print("\nاطلاعات ورود پیش‌فرض:")
        print("مدرس: admin / admin123")
        print("دانش‌آموز: student1 / student123")
        print("\n" + "=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ راه‌اندازی ناقص است")
        print("=" * 60)
        print("\nلطفاً ابتدا وابستگی‌ها را نصب کنید:")
        print("pip install -r requirements.txt")
        print("\nسپس دوباره این اسکریپت را اجرا کنید:")
        print("python setup.py")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
