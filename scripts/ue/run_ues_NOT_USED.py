import sys
import os
import subprocess
import time
import concurrent.futures
from multiprocessing import Process

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(ROOT_DIR, 'files')

def send_ue_files(num_ues):
    for i in range(1, num_ues + 1):
        filename = os.path.join(FILES_DIR, f'mobility_file_ue{i}.csv')
        if ( not os.path.isfile(filename)):
            print(f"{filename} does not exist, skipping")
            continue

        command = f'kubectl cp {filename} ue{i}:/openairinterface5g/cmake_targets/ran_build/build/handover_table.csv'
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if process.returncode != 0:
                print(f'Error executing command: {command}\n{error.decode()}')
                pass
            else:
                print(f'Success executing command: {command}\n{output.decode()}')
                pass
        except Exception as e:
            pass
            print(f'Error executing command: {command}\n{e}')
        pass


def get_ue_params(num_ues):
    params = []
    for i in range(1, num_ues + 1):
        filename = os.path.join(FILES_DIR, f'mobility_file_ue{i}.csv')
        print(os.path.isfile(filename))
        if (not os.path.isfile(filename)):
            print(f'{filename} does not exist, skipping')
            continue
        source = '0'
        target = '0'
        with open(filename, 'r') as f:
            source = f.readline().strip().split(',')[0]
            target = f.readline().strip().split(',')[0]
            if not target:
                target = '0'
            
            params.append((source, target))
    print(params)
    return params

def run_ues(num_enbs, ue_params):
    for i, (source, target) in enumerate(ue_params):
        command = f'kubectl exec ue{i + 1} -- /openairinterface5g/cmake_targets/ran_build/build/oai_ue.sh {i + 1} {num_enbs} {str(int(source) + 1)}'
        print(command)
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if process.returncode != 0:
                print(f'Error executing command: {command}\n{error.decode()}')
                pass
            else:
                print(f'Success executing command: {command}\n{output.decode()}')
                pass
        except Exception as e:
            pass
            print(f'Error executing command: {command}\n{e}')
        pass
    pass

def execute_traffic_commands():
    with open(os.path.join(FILES_DIR, 'traffic_scenario.txt'), 'r') as file:
        lines = file.readlines()
        command_lists = []
        for line in lines:
            ue_commands = []
            [ue, *sessions] = line.strip().split('|')
            id = int(ue.strip('UE'))
            for session in sessions:
                command, time_seconds = session.strip().split(',')
                time_seconds = int(time_seconds)
                #print(f'ID: {id}, Command: {command}, Time: {time_seconds}')
                ue_commands.append([id, time_seconds, command])
            command_lists.append(ue_commands)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for commands in command_lists:
                futures.append(executor.submit(execute_commands, commands))

            # for future in concurrent.futures.as_completed(futures):
            #     result = future.result()
            #     if result is not None:
            #         print(result)
        print('Traffic commands finished')


def execute_commands(commands):
    tmp = 0
    start_time = time.time()
    done = False
    index = 0
    while (index < len(commands)):
        current_time = time.time()
        ue_id, delay, command = commands[index]
        kube_cmd = f'kubectl exec ue{ue_id} -- {command}'
        
        if (start_time + delay > current_time):
            continue
        else:
            print(kube_cmd)
            #print(current_time - start_time)
            try:
                process = subprocess.Popen(kube_cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if (index + 1 < len(commands)):
                    max_duration = commands[index + 1][1] - delay
                    print(f'Timeout is: {max_duration - 1}s')
                    time.sleep(max_duration - 1)
                    output, error = subprocess.Popen(f'kubectl exec ue{ue_id} -- pkill -9 -f iperf'.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    o ,e = process.communicate()
                else:
                    pass
                    print(f'Last traffic command for ue {ue_id}')
                    output, error = process.communicate()
                if process.returncode == 137: # SIGKILL code
                    print(f'Command killed successfully: {command}')
                    pass
                elif process.returncode != 0:
                    print(process.returncode)
                    print(f'Error executing command: {command}\n{error.decode()}')
                    pass
                else:
                    print(f'Success executing command: {command}\n{output.decode()}')
                    pass
            except Exception as e:
                pass
                print(f'Error executing command e: {command}\n{e}')
            index += 1

def main():
    if (len(sys.argv) != 3):
        print('Use: python3 run_ues.py <num_ues> <num_enbs>')
        exit()

    num_ues = int(sys.argv[1])
    num_enbs = int(sys.argv[2])

    print('Copying mobility files to UE pods...')
    #send_ue_files(num_ues)

    # Run
    ue_params = get_ue_params(num_ues)
    ues_process = Process(target=lambda: run_ues(num_enbs, ue_params))
    #ues_process.start()
    print('Ue run thread is running...')

    # Traffic
    traffic_process = Process(target=lambda: execute_traffic_commands())
    #traffic_process.start()
    print('Traffic thread is running...')



if __name__ == "__main__":
    main()
