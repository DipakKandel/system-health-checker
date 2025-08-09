import psutil
import datetime
import time

# Global variables for caching CPU data
_cpu_cache = None
_last_cpu_update = 0

def get_cpu_info():
    global _cpu_cache, _last_cpu_update
    current_time = time.time()
    
    # Use cached value if recent (within 1 second)
    if _cpu_cache is not None and current_time - _last_cpu_update < 1:
        cpu_usage_percentage = _cpu_cache
    else:
        # Get fresh CPU reading
        cpu_usage_percentage = psutil.cpu_percent(interval=0.1)
        _cpu_cache = cpu_usage_percentage
        _last_cpu_update = current_time
    
    logical_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)
    
    # Handle CPU frequency (not available on all systems like macOS)
    try:
        cpu_freq = psutil.cpu_freq()
        frequency_mhz = cpu_freq.current if cpu_freq else 0
    except (AttributeError, FileNotFoundError, OSError):
        frequency_mhz = 0  # CPU frequency not available on this system
    
    return {
        "CPU Usage (%)": cpu_usage_percentage,
        "Logical Cores": logical_cores,
        "Physical Cores": physical_cores,
        "Frequency (MHz)": frequency_mhz
    }

def get_memory_info():
    total_memory = psutil.virtual_memory().total / (1024 ** 3)
    used_memory = psutil.virtual_memory().used / (1024 ** 3)
    free_memory = psutil.virtual_memory().free / (1024 ** 3)
    memory_usage = psutil.virtual_memory().percent
    return {
        "Total Memory (GB)": total_memory,
        "Used Memory (GB)": used_memory,
        "Free Memory (GB)": free_memory,
        "Memory Usage (%)": memory_usage
    }

def get_disk_info():    
    total_disk = psutil.disk_usage('/').total / (1024 ** 3)
    used_disk = psutil.disk_usage('/').used / (1024 ** 3)
    free_disk = psutil.disk_usage('/').free / (1024 ** 3)
    disk_usage = psutil.disk_usage('/').percent

    return {
        "Total Disk (GB)": total_disk,
        "Used Disk (GB)": used_disk,
        "Free Disk (GB)": free_disk,
        "Disk Usage (%)": disk_usage
    }

def get_network_info():
    total_network_sent = psutil.net_io_counters().bytes_sent / (1024 ** 3)
    total_network_recv = psutil.net_io_counters().bytes_recv / (1024 ** 3)
    network_usage = (psutil.net_io_counters().bytes_sent / (1024 ** 3) + psutil.net_io_counters().bytes_recv / (1024 ** 3))

    return {
        "Total Network Sent (GB)": total_network_sent,
        "Total Network Received (GB)": total_network_recv,
        "Network Usage (%)": network_usage
    }

def get_uptime_info():
    current_time = datetime.datetime.now()
    uptime = current_time - datetime.datetime.fromtimestamp(psutil.boot_time())
    return {
        "Uptime (seconds)": uptime
    }

def get_top_processes(limit=10):
    try:
        # Get all processes with their CPU and memory info (fast approach for GUI)
        process_list = []
        
        # Get CPU percentages for all processes without blocking
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
            try:
                process_info = proc.info
                if process_info['memory_percent'] is not None:
                    # Get CPU percentage without blocking for GUI
                    cpu_percent = proc.cpu_percent()
                    
                    process_list.append({
                        'pid': process_info['pid'],
                        'name': process_info['name'],
                        'cpu_percent': cpu_percent,
                        'memory_percent': process_info['memory_percent'],
                        'memory_mb': process_info['memory_info'].rss / (1024 * 1024) if process_info['memory_info'] else 0
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by CPU usage (descending)
        top_cpu_processes = sorted(process_list, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        
        # Sort by memory usage (descending)
        top_memory_processes = sorted(process_list, key=lambda x: x['memory_percent'], reverse=True)[:limit]
        
        return {
            "top_cpu_processes": top_cpu_processes,
            "top_memory_processes": top_memory_processes,
            "total_processes": len(process_list)
        }
    except Exception as e:
        return {
            "error": f"Failed to get top processes: {str(e)}",
            "top_cpu_processes": [],
            "top_memory_processes": [],
            "total_processes": 0
        }

def get_temperature_info():
    temperature = psutil.sensors_temperatures()
    return {
        "Temperature (C)": temperature
    }