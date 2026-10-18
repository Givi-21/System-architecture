#/*
#   ** Writen by Givi **
#
#   This code works for composing and managing docker containers only.
#
#   This program requires you to install only one external library - psutil, which's responsible,
#   in this case for identifying if docker desktop pocess is running.
#*/

#!/usr/bin/evn python3
import subprocess
import shutil
import time
import argparse
import inspect
import platform
import sys
import json

try:
    import psutil
except ModuleNotFoundError:
    print("One external library is needed to be intaslled.\nRun -> pip install psutil")
    sys.exit(1)

def get_version():
    print("version 1.2")
    return

def is_process_running(process):
    for proc in psutil.process_iter(["name"]):
        try:
            if process.lower() in proc.info["name"].lower():
                return True

        except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    return False


def run_all_containers(containers, exec_path):
    try:
        for cont_name, path in containers.items():
            running_container = subprocess.run([exec_path, "compose", "-f", path, "up", "-d"],
                capture_output=True
            )

            if running_container.returncode == 0:
                print(f"[INFO] Container '{cont_name}' started successufully.")

            else:
                print(f"[ERROR] Failed to start '{cont_name}: {running_container.stderr.strip()}'")

    except (FileNotFoundError, PermissionError) as err:
        return f"[SYSTEM ERROR] {err}"


def run_container(args, exec_path, containers):
    try:
        path = containers[args.container]

        # Checking if docker saved compose file paths as WSL type path.
        running_container = subprocess.run([exec_path, "compose", "-f", path, "up", "-d"],
            capture_output=True, text=True
        )

        if running_container.returncode == 0:
            print(f"[INFO] Container '{args.container}' started successufully.")
            return

        else:
            return f"[ERROR] Failed to start '{args.container}: {running_container.stderr.strip()}'"

    except (FileNotFoundError, PermissionError, KeyError) as err:
        return f"[SYSTEM ERROR] {err}"
    

def check_status(args, exec_path, containers):

    # Ensure the container is part of your tracking framework list
    if args.container not in containers:
        return f"[ERROR] Container '{args.container}' doesn't exist in configuration."

    metadata = get_container_metadata(exec_path, args.container)

    if metadata is None:
        return f"[ERROR] Container '{args.container}' could not be inspected by engine."

    is_running = metadata.get("State", {}).get("Running", False)

    if is_running and args.container in containers:
        print(f"[INFO] Container '{args.container}' is running.")
        return True
    else:
        print(f"[INFO] Container '{args.container}' is inactive.")
        return False


def stop_container(args, exec_path, containers):
    try:
        stopped_container = subprocess.run([exec_path, "stop", args.container],
            capture_output=True
        )

        if stopped_container.returncode == 0:
            return f"[INFO] Container '{args.container}' has stopped."

    except (FileNotFoundError, PermissionError, KeyError) as err:
        return f"[ERROR] {err}"


def remove_container(args, exec_path, containers):
    try:
        metadata = get_container_metadata(exec_path, args.container)
        if metadata is None:
            print(f"[ERROR] Container {args.container} doesn't exist.'")

        #status_result = "".join(container_status.stdout.splitlines()).replace("'", '')
        is_running = metadata.get("State").get("Running", False)
        if is_running:
            subprocess.run([exec_path, "stop", args.container], capture_output=True)

        print("[INFO] Removing the container...")
        removed_container = subprocess.run([exec_path, "rm", args.container], capture_output=True)

        if removed_container.returncode == 0:
            return f"[INFO] Container {args.container} has been removed."
        else:
            error_msg = removed_container.stderr().decode().strip()
            return f"[ERROR] Error has occured: {error_msg}"

    except (FileNotFoundError, PermissionError, subprocess.SubprocessError) as err:
        return f"[SYSTEM ERROR] {err}"


def remove_all_containers(exec_path, containers):
    try:
        for cont_name, path in containers.items():
            metadata = get_container_metadata(exec_path, cont_name)

            is_running = metadata.get("State").get("Running", False)
            if is_running:
                subprocess.run([exec_path, "stop", cont_name], capture_output=True)

                removed_container = subprocess.run([exec_path, "rm", cont_name],
                    capture_output=True
                )

                if removed_container.returncode == 0:
                    print(f"[INFO] Container '{cont_name}' has been removed.")

                else:
                    print(f"[ERROR] Failed to remove '{cont_name}: {removed_container.stderr.strip()}'")
        return

    except (FileNotFoundError, PermissionError) as err:
        return f"[SYSTEM ERROR] {err}"



def stop_all_containers(containers, exec_path):
    for cont_name, path in containers.items():
        try:
            stopped_container = subprocess.run([exec_path, "stop", cont_name],
                capture_output=True
            )

            if stopped_container.returncode == 0:
                print(f"[INFO] Container '{cont_name}' has stoped.")

        except (FileNotFoundError, PermissionError) as err:
            return f"[ERROR] {err}"


def run_base_process(containers, cli_exec_path, desktop_exec_path):
    start_time = time.time()
    max_time = 30

    exec_path_ready = False

    if not exec_path_ready:
        while time.time() - start_time < 30:
            process = subprocess.Popen([desktop_exec_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            process_status = process.poll()

            if process_status is not None:
                print("[ERROR] Failed to start docker...")
                break

            result = subprocess.run([cli_exec_path, "info"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                exec_path_ready = True
                print("[INFO] Docker is ready to work!")
                break

            # Wait a bit just in case before checking again
            time.sleep(0.5)
    else:
        print("[INFO] The process is already running.")


def list_containers(containers):
    for cont_name, path in containers.items():
        print(f"{cont_name}\n    |__{path}")
    return


# If you compose a docker file using WSL, docker saves path to the compose file
# in WSL path format(e.g. C:\ -> /mnt/c). This function manually converts WSL path format
# to standard Windows path.
def wsl_to_windows(path):
    if path.startswith("/mnt/"):
        drive = path[5].upper()

        remaining_path = path[7:].replace('/', "\\")
        return f"{drive}:\\{remaining_path}"

    return path


# "Containers" must be a dictionary.
def get_container_info():
    get_ids = subprocess.run(["docker", "ps", "-q", "-a"], text=True, capture_output=True)
    if get_ids.stdout is None:
        print("[ERROR] There are no containers to get IDs from.")
        return

    container_ids = get_ids.stdout.split()

    # Getting container names by ids.
    cont_names = []
    for cid in container_ids:
        if cid is not None:
            info = subprocess.run(["docker", "inspect", "--format", "'{{.Name}}'", cid],
                text=True, capture_output=True
            )
            if info.returncode == 0:
                cont_names.append(info.stdout.strip().replace("'", "").lstrip("/"))
            else:
                return f"[SYSTEM ERROR] {info.stderr}"

    # Getting compose file paths by container names.
    containers = {}
    for name in cont_names:
        if name is not None:
            info = subprocess.run(
                ["docker", "inspect", "--format", "'{{index .Config.Labels \"com.docker.compose.project.config_files\"}}'", name],
                text=True,
                capture_output=True
            )
            formated_compose_paths = info.stdout.strip().replace("'", "").split()
            if info.returncode == 0 and formated_compose_paths:
                for path in formated_compose_paths:
                    formated_path = wsl_to_windows(path)
                    containers[name] = formated_path
            else:
                return f"[SYSTEM ERROR] {info.stdout}"

    return containers


def main(args):
    cli_exec_path = shutil.which("docker")

    # Default docker-desktop paths.
    system_desktop_exec_paths = {
        "Linux": "/opt/docker-desktop/bin/com.docker.backend",
        "Darwin": "/Applications/Docker.app",
        "Windows": "C:\\Users\\user\\AppData\\Local\\Programs\\DockerDesktop\\Docker Desktop.exe"
    }

    desktop_exec_path = ""
    system = platform.system()

    try:
        if system in system_desktop_exec_paths:
            desktop_exec_path = system_desktop_exec_paths[system]
    except FileNotFoundError:
        print(f"{desktop_exec_path} couldn't be found...")

    containers = get_container_info()

    # All arguments needed for functions.
    available_args = {
        "args": args,
        "exec_path": cli_exec_path,
        "containers": containers,
        "desktop_exec_path": desktop_exec_path,
    }

    # Aggregate all commands and relate to functions.
    functions = {
        "status": check_status,
        "start_all": run_all_containers,
        "start": run_container,
        "list": list_containers,
        "stop": stop_container,
        "stop_all": stop_all_containers,
        "rm": remove_container,
        "rm_all": remove_all_containers,
        "version": get_version
    }

    # Docker Desktop process
    running = is_process_running(system_desktop_exec_paths[system])

    # If no arguments were provided, run docker desktop by default.
    if args.command is None and not running:
        run_base_process(containers, cli_exec_path, desktop_exec_path)

    else:
        # Dynamically identifying which function runs and which arguemnts will be used for that function.
        func_pointer = functions[args.command] # Getting pointer to the function.
        func_signature = inspect.signature(func_pointer) # Getting parameters of the function.

        kwargs = {}
        for params in func_signature.parameters:
            if params in available_args:
                kwargs[params] = available_args[params]

        # Unpacking parameters for chosen function.
        result = func_pointer(**kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Custom script to safely run all containers and check for applied security settings.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Main parser
    #parser.add_argument("container", nargs="?", default=None, type=str, help="Name of a container.")
    subparsers = parser.add_subparsers(dest="command", required=False) # 'command' is a placeholder of a user's subcommand.

    base_argument = argparse.ArgumentParser(add_help=False)
    base_argument.add_argument(
        "container",
        nargs="?",
        default=None,
        help="Target container."
    )

    # All subcommands.
    show_version = subparsers.add_parser("version", help="Get current version of the program")
    show_version.set_defaults(func=get_version)

    start_all_parser = subparsers.add_parser("start_all", help="Run all containers sequentially.")
    start_all_parser.set_defaults(func=run_all_containers)

    list_objects = subparsers.add_parser("list", help="List all available containers.")
    list_objects.set_defaults(func=list_containers)

    stop_object = subparsers.add_parser("stop", parents=[base_argument], help="Stop a container.")
    stop_object.set_defaults(func=stop_container)

    remove_object = subparsers.add_parser("rm", parents=[base_argument], help="Remove a container.")
    remove_object.set_defaults(func=remove_container)

    remove_all_objects = subparsers.add_parser("rm_all", help="Remove all containers.")
    remove_all_objects.set_defaults(func=remove_all_containers)

    stop_all_object = subparsers.add_parser("stop_all", help="Stop a container.")
    stop_all_object.set_defaults(func=stop_all_containers)

    start_single_process = subparsers.add_parser("start", parents=[base_argument], help="Start a container.")
    status = subparsers.add_parser("status", parents=[base_argument], help="Check the status of a container.")

    args = parser.parse_args()
    main(args)
