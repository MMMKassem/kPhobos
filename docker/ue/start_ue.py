import sys
import os
import subprocess
import time
import concurrent.futures
from multiprocessing import Process
import re

MOBILITY_FILE = 'mobility_scenario.txt'
TRAFFIC_FILE = 'traffic_scenario.txt'
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(ROOT_DIR, 'files')


def fetch_files():
    command = f'wget http://10.10.0.1:8000/{MOBILITY_FILE}'
    print(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    command = f'wget http://10.10.0.1:8000/{TRAFFIC_FILE}'
    print(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()


def generate_handover_table(ue_id) -> int:
        #files = [[] for _ in range(self.num_ues)]
        num_enbs = 1
        lines = []
        with open(os.path.join(ROOT_DIR, MOBILITY_FILE), 'r') as f:
            while True:
                raw_line = f.readline()
                if not raw_line:
                    break

                actions = raw_line.strip().split('|')  # Remove control characters and split
                start = actions[0].replace('UE', '').replace('eNB', '').split('-')
                assert start[0].isnumeric()
                ue_id_tmp = int(start[0])
                if ue_id_tmp != ue_id:
                    continue

                lines.append(f'{int(start[2]) - 1},0')
                for handover in actions[1:]:
                    if handover == '':
                        continue
                    data = handover.replace('HO-eNB', '').split('-')
                    lines.append(f'{int(data[0]) - 1},{data[1]}')
                
                # Hack until proxy is fixed
                if len(lines) > 1:
                    fake_target = lines[-2].split(',')[0]
                    lines.append(f'{fake_target},1000000')

        with open(os.path.join(ROOT_DIR, f'handover_table.csv'), 'w') as tmp_f:
            for line in lines:
                tmp_f.write(f'{line}\n')
            
        if len(lines) > 1:
            num_enbs = 2

        return num_enbs

def run_ue(num_enbs, ue_id):
    
    command = f'/openairinterface5g/cmake_targets/ran_build/build/oai_ue.sh {ue_id} {num_enbs} handover_table.csv'
    print(command)
    try:
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        pass
        print(f'Error executing command: {command}\n{e}')
    pass
    


def parse_traffic_commands(ue_id):
    filename = os.path.join(ROOT_DIR, f'traffic_scenario.txt')
    with open(filename, 'r') as file:
        lines = file.readlines()
        commands = []
        for line in lines:
            [ue, *sessions] = line.strip().split('|')
            id = int(ue.strip('UE'))
            if id != ue_id:
                continue
            for session in sessions:
                command, time_seconds = session.strip().split(',')
                time_seconds = int(time_seconds)
                #print(f'ID: {id}, Command: {command}, Time: {time_seconds}')
                commands.append((command, time_seconds))
    return commands
        


def execute_traffic_commands(commands):
    start_time = time.time()
    index = 0
    kill_cmd = 'pkill -2 -f iperf'.split(' ')
    while (index < len(commands)):
        current_time = time.time()
        command, delay = commands[index]

        if (start_time + delay > current_time):
            continue
        else:
            #print(current_time - start_time)
            try:
                process = subprocess.Popen(command, shell=True)
                if (index + 1 < len(commands)):
                    max_duration = commands[index + 1][1] - delay
                    print(f'Timeout is: {max_duration - 1}s')
                    time.sleep(max_duration - 1)
                    output, error = subprocess.Popen(kill_cmd).communicate()
                    process.wait()
                else:
                    print(f'Last traffic command')
                    process.wait()
            except Exception as e:
                print(f'Error executing command e: {command}\n{e}')
            index += 1


def is_interface_up(interface):
    for line in open('/proc/net/dev', 'r'):
        if interface in line:
            return True
    return False


def main():
    if (len(sys.argv) != 2):
        print('Use: python3 run_ues.py <ue_id>')
        exit()

    ue_id = int(sys.argv[1])
    
    fetch_files()
    num_enbs = generate_handover_table(ue_id)

    # Run
    run_ue(num_enbs, ue_id)

    print('Ue run thread is running...')

    print('Waiting for oai interface to be set up...')
    while not is_interface_up('oaitun_ue1'):
        time.sleep(0.1)
    print('Done')
    # Traffic
    traffic_commands = parse_traffic_commands(ue_id)
    traffic_process = Process(target=lambda: execute_traffic_commands(traffic_commands))
    traffic_process.start()
    print('Traffic thread is running...')


if __name__ == "__main__":
    main()