import importlib.util
import sys

spec = importlib.util.spec_from_file_location("main", "app.py")
main = importlib.util.module_from_spec(spec)
sys.modules["main"] = main
spec.loader.exec_module(main)

main.init_db()
