import os
import sys
import lupa

def Test_Lua():
    from lupa import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)

    # 실행 파일이든 소스 실행이든 상관없이 현재 실행 위치 기준
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    script_path = os.path.join(base_dir, "scripts", "logger.lua")

    with open(script_path, "r", encoding="utf-8") as f:
        logger = f.read()

    lua.execute(logger)
    run_print = lua.eval("Print_Lua")
    run_print("하하호호즐겁다")
