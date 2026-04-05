#!/usr/bin/env python3
"""
Quick verification script for Save-Restricted-Bot setup
"""
import json
import sys
import os

def check_config():
    """Check if config.json exists and is properly formatted"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required = ['TOKEN', 'ID', 'HASH', 'STRING']
        missing = [k for k in required if k not in config]
        
        print("\n📋 Configuration Status:")
        print("-" * 50)
        
        if missing:
            print(f"❌ Missing keys: {', '.join(missing)}")
            return False
        
        for key in required:
            value = config.get(key)
            if value:
                # Show masked values for security
                if key == 'TOKEN':
                    display = value[:10] + "..." if len(value) > 10 else value
                elif key == 'STRING' and value:
                    display = value[:15] + "..." if len(value) > 15 else value
                else:
                    display = str(value)
                print(f"✓ {key}: {display}")
            else:
                print(f"⚠️  {key}: Not set (required for bot to work)")
        
        return all(config.get(k) for k in ['TOKEN', 'ID', 'HASH'])
    
    except FileNotFoundError:
        print("❌ config.json not found!")
        return False
    except json.JSONDecodeError:
        print("❌ config.json is not valid JSON!")
        return False

def check_imports():
    """Check if required packages are installed"""
    print("\n📦 Dependency Status:")
    print("-" * 50)
    
    required = ['pyrogram', 'flask']
    all_ok = True
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            all_ok = False
    
    # Check optional
    try:
        import tgcrypto
        print(f"✓ tgcrypto (optional, for speed)")
    except ImportError:
        print(f"⚠️  tgcrypto not installed (optional but recommended)")
    
    return all_ok

def main():
    print("\n" + "=" * 50)
    print("Save-Restricted-Bot Setup Verification")
    print("=" * 50)
    
    imports_ok = check_imports()
    config_ok = check_config()
    
    print("\n" + "=" * 50)
    if imports_ok:
        print("✅ Dependencies: OK")
    else:
        print("❌ Dependencies: FAILED - Run: pip install -r requirements.txt")
    
    if config_ok:
        print("✅ Configuration: READY TO RUN")
        print("\n🚀 To start the bot, run:")
        print("   python main.py")
    else:
        print("❌ Configuration: INCOMPLETE")
        print("\n📝 Edit config.json with your Telegram credentials:")
        print("   1. Get API ID/Hash from: https://my.telegram.org/apps")
        print("   2. Get Bot Token from: @BotFather on Telegram")
        print("   3. Get Session String from: https://gist.github.com/bipinkrish/0940b30ed66a5537ae1b5aaaee716897#file-main-py")
    
    print("=" * 50 + "\n")

if __name__ == '__main__':
    main()
