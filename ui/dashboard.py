import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import sys
import os
import psutil
import signal

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.system_info import get_memory_info, get_disk_info, get_network_info, get_cpu_info, get_uptime_info, get_top_processes

class SystemHealthDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("System Health Checker Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage for charts
        self.cpu_history = deque(maxlen=50)
        self.memory_history = deque(maxlen=50)
        self.time_history = deque(maxlen=50)
        
        # Setup UI
        self.setup_ui()
        self.setup_charts()
        
        # Start real-time updates
        self.update_data()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="System Health Dashboard", 
                              font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        self.overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.overview_frame, text="Overview")
        
        # Processes tab
        self.processes_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.processes_frame, text="Processes")
        
        # Setup overview tab
        self.setup_overview_tab()
        
        # Setup processes tab
        self.setup_processes_tab()
        
    def setup_overview_tab(self):
        # System info frame
        info_frame = tk.Frame(self.overview_frame, bg='white')
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # CPU Info
        cpu_frame = tk.LabelFrame(info_frame, text="CPU Information", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.cpu_usage_label = tk.Label(cpu_frame, text="CPU Usage: --%", font=('Arial', 14), bg='white', fg='#2c3e50')
        self.cpu_usage_label.pack(pady=10)
        
        self.cpu_cores_label = tk.Label(cpu_frame, text="Cores: --", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.cpu_cores_label.pack()
        
        self.cpu_freq_label = tk.Label(cpu_frame, text="Frequency: -- MHz", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.cpu_freq_label.pack(pady=(0, 10))
        
        # Memory Info
        memory_frame = tk.LabelFrame(info_frame, text="Memory Information", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        memory_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.memory_usage_label = tk.Label(memory_frame, text="Memory Usage: --%", font=('Arial', 14), bg='white', fg='#2c3e50')
        self.memory_usage_label.pack(pady=10)
        
        self.memory_total_label = tk.Label(memory_frame, text="Total: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.memory_total_label.pack()
        
        self.memory_used_label = tk.Label(memory_frame, text="Used: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.memory_used_label.pack()
        
        self.memory_free_label = tk.Label(memory_frame, text="Free: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.memory_free_label.pack(pady=(0, 10))
        
        # Disk Info
        disk_frame = tk.LabelFrame(info_frame, text="Disk Information", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        disk_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.disk_usage_label = tk.Label(disk_frame, text="Disk Usage: --%", font=('Arial', 14), bg='white', fg='#2c3e50')
        self.disk_usage_label.pack(pady=10)
        
        self.disk_total_label = tk.Label(disk_frame, text="Total: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.disk_total_label.pack()
        
        self.disk_used_label = tk.Label(disk_frame, text="Used: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.disk_used_label.pack()
        
        self.disk_free_label = tk.Label(disk_frame, text="Free: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.disk_free_label.pack(pady=(0, 10))
        
        # Network Info
        network_frame = tk.LabelFrame(self.overview_frame, text="Network Information", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        network_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.network_sent_label = tk.Label(network_frame, text="Bytes Sent: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.network_sent_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.network_recv_label = tk.Label(network_frame, text="Bytes Received: -- GB", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.network_recv_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Uptime Info
        uptime_frame = tk.LabelFrame(self.overview_frame, text="System Uptime", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        uptime_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.uptime_label = tk.Label(uptime_frame, text="Uptime: --", font=('Arial', 12), bg='white', fg='#2c3e50')
        self.uptime_label.pack(pady=10)
        
        # Charts frame
        charts_frame = tk.Frame(self.overview_frame, bg='white')
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # CPU Chart
        cpu_chart_frame = tk.LabelFrame(charts_frame, text="CPU Usage Over Time", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        cpu_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.cpu_figure = Figure(figsize=(6, 4), facecolor='white')
        self.cpu_ax = self.cpu_figure.add_subplot(111)
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_figure, cpu_chart_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Memory Chart
        memory_chart_frame = tk.LabelFrame(charts_frame, text="Memory Usage Over Time", font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        memory_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.memory_figure = Figure(figsize=(6, 4), facecolor='white')
        self.memory_ax = self.memory_figure.add_subplot(111)
        self.memory_canvas = FigureCanvasTkAgg(self.memory_figure, memory_chart_frame)
        self.memory_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_processes_tab(self):
        # Top processes frame
        processes_container = tk.Frame(self.processes_frame, bg='white')
        processes_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # CPU Processes
        cpu_processes_frame = tk.LabelFrame(processes_container, text="Top Processes by CPU Usage (Right-click to kill)", 
                                          font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        cpu_processes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview for CPU processes
        self.cpu_tree = ttk.Treeview(cpu_processes_frame, columns=('PID', 'Name', 'CPU%', 'Memory%', 'Memory(MB)'), 
         show='headings', height=8)
        
        self.cpu_tree.heading('PID', text='PID')
        self.cpu_tree.heading('Name', text='Name')
        self.cpu_tree.heading('CPU%', text='CPU %')
        self.cpu_tree.heading('Memory%', text='Memory %')
        self.cpu_tree.heading('Memory(MB)', text='Memory (MB)')
        
        self.cpu_tree.column('PID', width=80, anchor='center')
        self.cpu_tree.column('Name', width=200, anchor='w')
        self.cpu_tree.column('CPU%', width=80, anchor='center')
        self.cpu_tree.column('Memory%', width=100, anchor='center')
        self.cpu_tree.column('Memory(MB)', width=120, anchor='center')
        
        self.cpu_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Memory Processes
        memory_processes_frame = tk.LabelFrame(processes_container, text="Top Processes by Memory Usage (Right-click to kill)", 
                                             font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        memory_processes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for Memory processes
        self.memory_tree = ttk.Treeview(memory_processes_frame, columns=('PID', 'Name', 'Memory%', 'Memory(MB)', 'CPU%'), 
                                       show='headings', height=8)
        
        self.memory_tree.heading('PID', text='PID')
        self.memory_tree.heading('Name', text='Name')
        self.memory_tree.heading('Memory%', text='Memory %')
        self.memory_tree.heading('Memory(MB)', text='Memory (MB)')
        self.memory_tree.heading('CPU%', text='CPU %')
        
        self.memory_tree.column('PID', width=80, anchor='center')
        self.memory_tree.column('Name', width=200, anchor='w')
        self.memory_tree.column('Memory%', width=100, anchor='center')
        self.memory_tree.column('Memory(MB)', width=120, anchor='center')
        self.memory_tree.column('CPU%', width=80, anchor='center')
        
        self.memory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind right-click events for context menus (cross-platform)
        if sys.platform == "darwin":  # macOS
            self.cpu_tree.bind("<Button-2>", self.show_cpu_context_menu)
            self.cpu_tree.bind("<Control-Button-1>", self.show_cpu_context_menu)
            self.memory_tree.bind("<Button-2>", self.show_memory_context_menu)
            self.memory_tree.bind("<Control-Button-1>", self.show_memory_context_menu)
        else:  # Windows/Linux
            self.cpu_tree.bind("<Button-3>", self.show_cpu_context_menu)
            self.memory_tree.bind("<Button-3>", self.show_memory_context_menu)
        
        # Create context menus
        self.cpu_context_menu = tk.Menu(self.root, tearoff=0)
        self.cpu_context_menu.add_command(label="Kill Process", command=self.kill_cpu_process)
        self.cpu_context_menu.add_separator()
        self.cpu_context_menu.add_command(label="Refresh", command=self.update_data)
        
        self.memory_context_menu = tk.Menu(self.root, tearoff=0)
        self.memory_context_menu.add_command(label="Kill Process", command=self.kill_memory_process)
        self.memory_context_menu.add_separator()
        self.memory_context_menu.add_command(label="Refresh", command=self.update_data)
        
    def show_cpu_context_menu(self, event):
        """Show context menu for CPU process tree"""
        try:
            # Select the item that was right-clicked
            item = self.cpu_tree.identify_row(event.y)
            if item:
                self.cpu_tree.selection_set(item)
                self.cpu_context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing CPU context menu: {e}")
    
    def show_memory_context_menu(self, event):
        """Show context menu for Memory process tree"""
        try:
            # Select the item that was right-clicked
            item = self.memory_tree.identify_row(event.y)
            if item:
                self.memory_tree.selection_set(item)
                self.memory_context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing Memory context menu: {e}")
    
    def kill_cpu_process(self):
        """Kill the selected process from CPU tree"""
        try:
            selected_item = self.cpu_tree.selection()[0]
            values = self.cpu_tree.item(selected_item, 'values')
            pid = int(values[0])
            process_name = values[1]
            self.kill_process(pid, process_name)
        except (IndexError, ValueError) as e:
            messagebox.showerror("Error", "Please select a process to kill.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill process: {str(e)}")
    
    def kill_memory_process(self):
        """Kill the selected process from Memory tree"""
        try:
            selected_item = self.memory_tree.selection()[0]
            values = self.memory_tree.item(selected_item, 'values')
            pid = int(values[0])
            process_name = values[1]
            self.kill_process(pid, process_name)
        except (IndexError, ValueError) as e:
            messagebox.showerror("Error", "Please select a process to kill.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill process: {str(e)}")
    
    def kill_process(self, pid, process_name):
        """Kill a process by PID with confirmation dialog"""
        try:
            # Show confirmation dialog
            result = messagebox.askyesno(
                "Confirm Process Termination",
                f"Are you sure you want to kill the following process?\n\n"
                f"PID: {pid}\n"
                f"Name: {process_name}\n\n"
                f"Warning: This action cannot be undone and may cause data loss!",
                icon='warning'
            )
            
            if not result:
                return
            
            # Check if process exists
            try:
                process = psutil.Process(pid)
                
                # Try graceful termination first
                process.terminate()
                
                # Wait a bit for graceful termination
                try:
                    process.wait(timeout=3)
                    messagebox.showinfo("Success", f"Process {process_name} (PID: {pid}) terminated successfully.")
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination didn't work
                    process.kill()
                    messagebox.showinfo("Success", f"Process {process_name} (PID: {pid}) forcefully killed.")
                    
            except psutil.NoSuchProcess:
                messagebox.showwarning("Warning", f"Process {process_name} (PID: {pid}) no longer exists.")
            except psutil.AccessDenied:
                messagebox.showerror("Access Denied", 
                                   f"Permission denied to kill process {process_name} (PID: {pid}).\n"
                                   f"Try running the application as administrator/root.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill process: {str(e)}")
                
            # Refresh the process list
            self.update_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        
    def setup_charts(self):
        # Setup CPU chart
        self.cpu_ax.set_title('CPU Usage (%)', fontsize=12, fontweight='bold', color='#2c3e50')
        self.cpu_ax.set_ylabel('CPU %', fontsize=10, color='#2c3e50')
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.grid(True, alpha=0.3, color='#bdc3c7')
        self.cpu_ax.set_facecolor('#f8f9fa')
        self.cpu_ax.tick_params(colors='#2c3e50')
        
        # Setup Memory chart
        self.memory_ax.set_title('Memory Usage (%)', fontsize=12, fontweight='bold', color='#2c3e50')
        self.memory_ax.set_ylabel('Memory %', fontsize=10, color='#2c3e50')
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.grid(True, alpha=0.3, color='#bdc3c7')
        self.memory_ax.set_facecolor('#f8f9fa')
        self.memory_ax.tick_params(colors='#2c3e50')
        
        # Adjust figure layout to prevent label overlap
        self.cpu_figure.tight_layout()
        self.memory_figure.tight_layout()
        
    def update_charts(self):
        if len(self.time_history) > 1:
            # Update CPU chart
            self.cpu_ax.clear()
            self.cpu_ax.plot(list(self.time_history), list(self.cpu_history), linewidth=2, color='#007bff')
            self.cpu_ax.fill_between(list(self.time_history), list(self.cpu_history), alpha=0.3, color='#007bff')
            self.cpu_ax.set_title('CPU Usage (%)', fontsize=12, fontweight='bold', color='#2c3e50')
            self.cpu_ax.set_ylabel('CPU %', fontsize=10, color='#2c3e50')
            self.cpu_ax.set_ylim(0, 100)
            self.cpu_ax.grid(True, alpha=0.3, color='#bdc3c7')
            self.cpu_ax.set_facecolor('#f8f9fa')
            self.cpu_ax.tick_params(colors='#2c3e50')
            
            # Format x-axis to show fewer time labels
            if len(self.time_history) > 10:
                # Show every 5th time label to prevent overlapping
                step = len(self.time_history) // 5
                x_ticks = list(self.time_history)[::step]
                self.cpu_ax.set_xticks(range(0, len(self.time_history), step))
                self.cpu_ax.set_xticklabels(x_ticks, rotation=45, ha='right')
            else:
                self.cpu_ax.set_xticks(range(len(self.time_history)))
                self.cpu_ax.set_xticklabels(list(self.time_history), rotation=45, ha='right')
            
            # Update Memory chart
            self.memory_ax.clear()
            self.memory_ax.plot(list(self.time_history), list(self.memory_history), linewidth=2, color='#dc3545')
            self.memory_ax.fill_between(list(self.time_history), list(self.memory_history), alpha=0.3, color='#dc3545')
            self.memory_ax.set_title('Memory Usage (%)', fontsize=12, fontweight='bold', color='#2c3e50')
            self.memory_ax.set_ylabel('Memory %', fontsize=10, color='#2c3e50')
            self.memory_ax.set_ylim(0, 100)
            self.memory_ax.grid(True, alpha=0.3, color='#bdc3c7')
            self.memory_ax.set_facecolor('#f8f9fa')
            self.memory_ax.tick_params(colors='#2c3e50')
            
            # Format x-axis for memory chart
            if len(self.time_history) > 10:
                # Show every 5th time label to prevent overlapping
                step = len(self.time_history) // 5
                x_ticks = list(self.time_history)[::step]
                self.memory_ax.set_xticks(range(0, len(self.time_history), step))
                self.memory_ax.set_xticklabels(x_ticks, rotation=45, ha='right')
            else:
                self.memory_ax.set_xticks(range(len(self.time_history)))
                self.memory_ax.set_xticklabels(list(self.time_history), rotation=45, ha='right')
            
            # Adjust layout to prevent overlap
            self.cpu_figure.tight_layout()
            self.memory_figure.tight_layout()
            
            self.cpu_canvas.draw()
            self.memory_canvas.draw()
    
    def update_data(self):
        try:
            # Get system information
            cpu_info = get_cpu_info()
            memory_info = get_memory_info()
            disk_info = get_disk_info()
            network_info = get_network_info()
            uptime_info = get_uptime_info()
            processes = get_top_processes(limit=10)
            
            # Validate that we got valid data
            if not all([cpu_info, memory_info, disk_info, network_info, uptime_info]):
                raise ValueError("Failed to get system information")
            
            # Update labels
            self.cpu_usage_label.config(text=f"CPU Usage: {cpu_info['CPU Usage (%)']:.1f}%")
            self.cpu_cores_label.config(text=f"Cores: {cpu_info['Logical Cores']} Logical, {cpu_info['Physical Cores']} Physical")
            freq_text = f"Frequency: {cpu_info['Frequency (MHz)']:.0f} MHz" if cpu_info['Frequency (MHz)'] > 0 else "Frequency: N/A"
            self.cpu_freq_label.config(text=freq_text)
            
            self.memory_usage_label.config(text=f"Memory Usage: {memory_info['Memory Usage (%)']:.1f}%")
            self.memory_total_label.config(text=f"Total: {memory_info['Total Memory (GB)']:.1f} GB")
            self.memory_used_label.config(text=f"Used: {memory_info['Used Memory (GB)']:.1f} GB")
            self.memory_free_label.config(text=f"Free: {memory_info['Free Memory (GB)']:.1f} GB")
            
            self.disk_usage_label.config(text=f"Disk Usage: {disk_info['Disk Usage (%)']:.1f}%")
            self.disk_total_label.config(text=f"Total: {disk_info['Total Disk (GB)']:.1f} GB")
            self.disk_used_label.config(text=f"Used: {disk_info['Used Disk (GB)']:.1f} GB")
            self.disk_free_label.config(text=f"Free: {disk_info['Free Disk (GB)']:.1f} GB")
            
            self.network_sent_label.config(text=f"Bytes Sent: {network_info['Total Network Sent (GB)']:.2f} GB")
            self.network_recv_label.config(text=f"Bytes Received: {network_info['Total Network Received (GB)']:.2f} GB")
            
            # Format uptime
            uptime_seconds = uptime_info['Uptime (seconds)'].total_seconds()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            self.uptime_label.config(text=f"Uptime: {days}d {hours}h {minutes}m")
            
            # Update charts data
            current_time = datetime.now().strftime('%H:%M:%S')
            self.cpu_history.append(cpu_info['CPU Usage (%)'])
            self.memory_history.append(memory_info['Memory Usage (%)'])
            self.time_history.append(current_time)
            
            # Update charts
            self.update_charts()
            
            # Update process lists
            if 'error' not in processes:
                # Clear existing items
                for item in self.cpu_tree.get_children():
                    self.cpu_tree.delete(item)
                for item in self.memory_tree.get_children():
                    self.memory_tree.delete(item)
                
                # Add CPU processes
                for proc in processes['top_cpu_processes']:
                    self.cpu_tree.insert('', 'end', values=(
                        proc['pid'],
                        proc['name'][:30],
                        f"{proc['cpu_percent']:.1f}",
                        f"{proc['memory_percent']:.1f}",
                        f"{proc['memory_mb']:.1f}"
                    ))
                
                # Add Memory processes
                for proc in processes['top_memory_processes']:
                    self.memory_tree.insert('', 'end', values=(
                        proc['pid'],
                        proc['name'][:30],
                        f"{proc['memory_percent']:.1f}",
                        f"{proc['memory_mb']:.1f}",
                        f"{proc['cpu_percent']:.1f}"
                    ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update data: {str(e)}")
        
        # Schedule next update (every 2 seconds)
        self.root.after(2000, self.update_data)

def main():
    root = tk.Tk()
    app = SystemHealthDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
