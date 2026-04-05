import subprocess
import time

def get_active_app():
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "window", "windows"],
        capture_output=True, text=True
    )
    lines = result.stdout.split("\n")
    resultss = []
    resultso = []
    resultsm = []
    for i in range(len(lines)):
        if "mSurface" in lines[i]:
            resultss.append(f"{i}:{lines[i]}")
        if "mOwnerUid" in lines[i]:
            resultso.append(f"{i}:{lines[i]}")
        if "mBaseLayer" in lines[i]:
            resultsm.append(f"{i}:{lines[i]}")
    return resultss, resultso, resultsm
            
if "absbs" in "adjfjenduskwabsbsfikekwoakd":
  print("yes")
print("switch")
time.sleep(5)
for group in get_active_app():
    for line in group:
      if "com.termux" in line or "com.google" in line or "com.ChillyRoom" in line:
        print(line)
print("done")