import json
from pathlib import Path

from app.main import app

backend_root = Path(__file__).resolve().parents[1]
output = backend_root / "openapi.json"
output.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
print(output)
