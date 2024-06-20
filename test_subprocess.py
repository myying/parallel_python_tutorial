import subprocess

p_list = []
for i in range(5):
    p = subprocess.Popen("sleep 10", shell=True)
    p_list.append(p)

for p in p_list:
    p.wait()
