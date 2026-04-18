import os, subprocess
out=subprocess.check_output('netstat -ano | findstr :8000', shell=True).decode()
pids={line.strip().split()[-1] for line in out.splitlines() if 'LISTENING' in line}
for p in pids: os.system(f'taskkill /F /PID {p}')
