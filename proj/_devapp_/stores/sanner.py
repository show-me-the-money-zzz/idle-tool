from core.config import DEFAULT_LOOP_INTERVAL
from grinder_utils.system import Calc_MS
from stores.task_manager import RunningTask

Loop_Interval = DEFAULT_LOOP_INTERVAL
def Get_LoopInterval_MS(): return Calc_MS(Loop_Interval)

_runnging_task = RunningTask("")
SetKey_RunningTask = _runnging_task.set_key
ResetKey_RunningTask = _runnging_task.reset_key
Get_RunningTask = _runnging_task.get

# start step
SetKey_StartStep = _runnging_task.set_startstep
GetKey_StartStep = _runnging_task.get_startstep