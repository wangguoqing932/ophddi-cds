"""Check LightRAG API structure."""
from __future__ import annotations
import inspect
import lightrag

print("LightRAG version:", lightrag.__version__)
print("LightRAG type:", type(lightrag.LightRAG))
print("=== LightRAG class members ===")
for name, cls in inspect.getmembers(lightrag):
    if inspect.isclass(cls) and not name.startswith("_"):
        print(f"  {name}")
print()
print("=== LightRAG.LightRAG init ===")
sig = inspect.signature(lightrag.LightRAG.__init__)
print(f"  Signature: {sig}")
print()
# Check llm submodule
try:
    import lightrag.llm as llm
    print("=== lightrag.llm members ===")
    print([x for x in dir(llm) if not x.startswith("_")])
except Exception as e:
    print(f"llm import error: {e}")

# Check if there's a base module
try:
    import lightrag.base as base
    print("=== lightrag.base members ===")
    print([x for x in dir(base) if not x.startswith("_")])
except Exception as e:
    print(f"base import error: {e}")
