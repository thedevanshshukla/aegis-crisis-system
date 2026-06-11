import os
import sys
import uvicorn

# Resolve root and backend paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

# Append backend directory to system path so Python can resolve app imports
sys.path.insert(0, BACKEND_DIR)

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8086))

    print("--------------------------------------------------")
    print("   AEGIS: Autonomous Crisis Intelligence System   ")
    print("--------------------------------------------------")
    print(f"Backend API & Frontend host launching on http://{host}:{port}")
    print("Press Ctrl+C to shutdown.")
    print("--------------------------------------------------")
    
    # Enable reload only in local development
    reload_mode = True if host == "127.0.0.1" else False
    uvicorn.run("app.main:app", host=host, port=port, reload=reload_mode)
