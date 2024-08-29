import os
import subprocess
import sys


def main():
    if (len(sys.argv) != 2):
        print('Use: python3 run_iperf_servers.py <num_ues>')
        exit()

    num_ues = int(sys.argv[1])
    log_path = '/local/repository/scripts/core/logs'
    cmd = f'rm {os.path.join(log_path, "*")}'
    p = subprocess.Popen(cmd, shell=True)
    p.wait()
    for i in range(1, num_ues + 1):
        cmd = f'iperf3 -s 10.45.0.1 -p {5000 + i} --logfile {log_path}/iperf_up{i}.log &'
        subprocess.Popen(cmd.split())
        cmd = f'iperf3 -s 10.45.0.1 -p {7000 + i} --logfile {log_path}/iperf_down{i}.log'
        subprocess.Popen(cmd.split())
    print('OK')
    

if __name__ == "__main__":
    main()