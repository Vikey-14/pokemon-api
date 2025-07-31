import os
import shutil

# 🗂️ Mapping of environments to corresponding files
ENV_MAP = {
    "local": ".env.local",
    "test": ".env.test",
    "prod": ".env.prod"
}

def set_env(target_env: str):
    target_env = target_env.lower()
    
    if target_env not in ENV_MAP:
        print(f"❌ Invalid environment '{target_env}'. Choose from: local, test, prod.")
        return

    src_file = ENV_MAP[target_env]
    dest_file = ".env"

    try:
        shutil.copyfile(src_file, dest_file)
        print(f"✅ Environment switched to '{target_env}' — '{src_file}' → '.env'")
    except Exception as e:
        print(f"❌ Failed to switch environment: {str(e)}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("❗ Usage: python set_env.py [local|test|prod]")
    else:
        set_env(sys.argv[1])
