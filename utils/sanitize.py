# %%
import re
# %%
def sanitize_namespace(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\-_.@+~:]", "_", name)
