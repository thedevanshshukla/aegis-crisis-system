import os
import sys
import uvicorn

# Resolve root and backend paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

# Append backend directory to system path so Python can resolve app imports
sys.path.insert(0, BACKEND_DIR)

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("   AEGIS: Autonomous Crisis Intelligence System   ")
    print("--------------------------------------------------")
    print("Backend API & Frontend host launching on http://127.0.0.1:8086")
    print("Press Ctrl+C to shutdown.")
    print("--------------------------------------------------")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8086, reload=True)
