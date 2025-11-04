
"""
Patient Health Monitoring System
Built with Tkinter, Pandas, Matplotlib, and Seaborn
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns

class PatientHealthMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Patient Health Monitoring System")
        self.root.geometry("1400x830")
        self.root.configure(bg='#eafaf1')
        self.df = None
        self.filtered_df = None
        self.patients = []
        self.create_widgets()

    def create_widgets(self):
        # Title Bar
        title_frame = tk.Frame(self.root, bg='#168aad', height=80)
        title_frame.pack(fill='x')
        title_label = tk.Label(
            title_frame, text="🏥 Patient Health Monitoring System", font=('Bahnschrift', 28, 'bold'),
            bg='#168aad', fg='white')
        title_label.pack(pady=25)

        # Layout: left controls, right notebook
        main_frame = tk.Frame(self.root, bg='#eafaf1')
        main_frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Controls Section
        left_panel = tk.Frame(main_frame, bg='#f4f9fb', width=320, relief='sunken', borderwidth=2)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.pack_propagate(False)

        # File Upload
        upload_btn = tk.Button(
            left_panel, text='📂 Upload CSV', command=self.upload_file, bg='#1b6ca8', fg='white',
            font=('Arial Rounded MT Bold', 12, 'bold'), pady=14, width=22)
        upload_btn.pack(pady=(35, 10))

        # Patient Selection Dropdown (after upload)
        self.patient_var = tk.StringVar()
        self.patient_dropdown = ttk.Combobox(
            left_panel, textvariable=self.patient_var, state='disabled',
            font=('Arial', 11), width=19)
        self.patient_dropdown.pack(pady=(8, 10))
        self.patient_dropdown.bind('<<ComboboxSelected>>', lambda e: self.load_patient())

        # Button Bar
        btn_frame = tk.Frame(left_panel, bg='#f4f9fb')
        btn_frame.pack(pady=(14, 8))
        self.analyze_btn = tk.Button(btn_frame, text='📝 Analyze', command=self.analyze_data,
                                     state='disabled', bg='#29ddb7', fg='black',
                                     font=('Bahnschrift', 11,'bold'), width=11, relief='ridge')
        self.analyze_btn.grid(row=0, column=0, padx=8, pady=8)
        self.visualize_btn = tk.Button(btn_frame, text='📈 Visualize', command=self.visualize_data,
                                       state='disabled', bg='#ffc93c', fg='black',
                                       font=('Bahnschrift', 11,'bold'), width=11, relief='ridge')
        self.visualize_btn.grid(row=0, column=1, padx=8, pady=8)
        self.reset_btn = tk.Button(left_panel, text='🔄 Reset', command=self.reset_app,
                                  bg='#e94f37', fg='white', font=('Bahnschrift',11,'bold'),
                                  width=24, relief='ridge')
        self.reset_btn.pack(pady=(10,8))

        # Status/Text
        self.status_lbl = tk.Label(left_panel, text='No file loaded.', bg='#f4f9fb', fg='#138d75', font=('Arial',10), wraplength=280)
        self.status_lbl.pack(pady=8)

        self.summary_txt = tk.Text(left_panel, height=20, font=('Consolas',10), wrap='word',
                                   bg='#f3f7fa', fg='#262626', borderwidth=2, relief='sunken')
        self.summary_txt.pack(fill='both', expand=True, padx=15, pady=10)

        # Right: Notebook
        right_panel = tk.Frame(main_frame, bg='#f4f9fb', borderwidth=2, relief='sunken')
        right_panel.pack(side='right', fill='both', expand=True)
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill='both', expand=True, padx=8, pady=8)
        # Analysis tab
        self.analysis_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.analysis_tab, text="📝 Analysis")
        self.analysis_text = tk.Text(self.analysis_tab, font=('Consolas',12), bg='#f6fff9', fg='#222', wrap='word')
        self.analysis_text.pack(fill='both', expand=True, padx=10, pady=10)
        # Visualization tab
        self.viz_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.viz_tab, text="📈 Visualizations")

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select Patient Health CSV", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.df = pd.read_csv(file_path)
            # Clean data
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
            num_cols = ['HeartRate','BP_Systolic','BP_Diastolic','Temp','Glucose','O2Sat']
            for col in num_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.df.dropna(subset=['PatientID','Date'], inplace=True)
            self.filtered_df = None
            # Populate patient dropdown
            self.patients = self.df['PatientID'].astype(str) + ' - ' + self.df['Name']
            unique_patients = self.patients.drop_duplicates().tolist()
            self.patient_dropdown['values'] = unique_patients
            self.patient_dropdown.config(state='readonly')
            if unique_patients:
                self.patient_var.set(unique_patients[0])
            self.status_lbl.config(text=f"✅ Loaded: {file_path.split('/')[-1]} | {len(self.df)} records", fg='#168aad')
            self.analyze_btn.config(state='normal')
            self.visualize_btn.config(state='normal')
            self.show_summary()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load file:\n{e}')
            self.status_lbl.config(text="❌ Error loading file.", fg='#e94f37')

    def show_summary(self):
        if self.df is None or self.df.empty:
            self.summary_txt.delete(1.0, tk.END)
            self.summary_txt.insert(1.0, "No data available.")
            return
        df = self.df.copy()
        summary = []
        summary.append(f"Patients: {df['PatientID'].nunique()}")
        try:
            date_min = df['Date'].min().date()
            date_max = df['Date'].max().date()
            summary.append(f"Date range: {date_min} to {date_max}")
        except Exception:
            summary.append("Date range: N/A")
        summary.append(f"Records: {len(df)}")
        summary.append(f"Avg HR: {df['HeartRate'].mean():.1f} | BP sys/diast: {df['BP_Systolic'].mean():.1f}/{df['BP_Diastolic'].mean():.1f}")
        summary.append(f"Avg Temp: {df['Temp'].mean():.1f} F | Avg Glucose: {df['Glucose'].mean():.1f} mg/dL")
        summary.append(f"Avg O2Sat: {df['O2Sat'].mean():.1f} %")
        self.summary_txt.delete(1.0, tk.END)
        self.summary_txt.insert(1.0,'\n'.join(summary))

    def load_patient(self):
        if self.df is None:
            return
        sel = self.patient_var.get()
        if ' - ' in sel:
            selpid = sel.split(' - ')[0]
        else:
            selpid = sel
        self.filtered_df = self.df[self.df['PatientID'] == selpid].copy()
        self.status_lbl.config(text=f"Selected: {self.patient_var.get()}", fg='#337a5b')
        self.show_patient_summary()

    def show_patient_summary(self):
        df = self.filtered_df if self.filtered_df is not None and not self.filtered_df.empty else self.df
        if df is None or df.empty:
            self.summary_txt.delete(1.0, tk.END)
            self.summary_txt.insert(1.0, "No patient data available.")
            return
        summary = []
        summary.append(f"Patient: {df['PatientID'].iloc[0]} - {df['Name'].iloc[0]}")
        try:
            days = df['Date'].dt.date.nunique()
        except Exception:
            days = 'N/A'
        summary.append(f"Records: {len(df)} | Days: {days}")
        summary.append(f"Avg HR: {df['HeartRate'].mean():.1f}")
        summary.append(f"BP sys/diast: {df['BP_Systolic'].mean():.1f}/{df['BP_Diastolic'].mean():.1f}")
        summary.append(f"Avg Temp: {df['Temp'].mean():.1f} F")
        summary.append(f"Avg Glucose: {df['Glucose'].mean():.1f} mg/dL")
        summary.append(f"Avg O2Sat: {df['O2Sat'].mean():.1f}%")
        self.summary_txt.delete(1.0, tk.END)
        self.summary_txt.insert(1.0, '\n'.join(summary))

    def analyze_data(self):
        df = self.filtered_df if self.filtered_df is not None else self.df
        if df is None or df.empty:
            messagebox.showinfo('Info', 'No data to analyze.')
            return
        self.analysis_text.delete(1.0, tk.END)
        # Overall stats
        results = []
        results.append('='*75)
        results.append(f"{'PATIENT HEALTH ANALYSIS REPORT':^75}")
        results.append('='*75 + '\n')
        results.append(f"Patient: {df['PatientID'].iloc[0]} - {df['Name'].iloc[0]}")
        results.append(f"Records: {len(df)}")
        try:
            results.append(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        except Exception:
            results.append("Date range: N/A")
        results.append('-'*50)
        # Averages
        metrics = ['HeartRate','BP_Systolic','BP_Diastolic','Temp','Glucose','O2Sat']
        units = ['bpm','mmHg','mmHg','F','mg/dL','%']
        means = [f"{df[c].mean():.1f} {u}" for c,u in zip(metrics,units)]
        results.append(f"Averages: HR {means[0]}, BP {means[1]}/{means[2]}, Temp {means[3]}, Glucose {means[4]}, O2Sat {means[5]}")
        # Alerts
        alerts = []
        try:
            if df['HeartRate'].max() > 100 or df['HeartRate'].min() < 55:
                alerts.append('Abnormal heart rate detected.')
            if df['BP_Systolic'].max() > 135 or df['BP_Systolic'].min() < 105 or df['BP_Diastolic'].max() > 90:
                alerts.append('Abnormal blood pressure detected.')
            if df['Temp'].max() > 100.5 or df['Temp'].min() < 96.5:
                alerts.append('Abnormal temperature readings.')
            if df['Glucose'].max() > 160 or df['Glucose'].min() < 65:
                alerts.append('Possible glucose issues detected.')
            if df['O2Sat'].min() < 94:
                alerts.append('Low O2 saturation detected.')
        except Exception:
            pass
        results.append('-'*50)
        results.append('Alerts/Risks: '+ (', '.join(alerts) if alerts else 'None'))
        # Extremes/latest
        try:
            latest = df.sort_values('Date',ascending=False).iloc[0]
            results.append(f"Latest Data: {latest['Date'].date()} | HR {latest['HeartRate']} | BP {latest['BP_Systolic']}/{latest['BP_Diastolic']} | Temp {latest['Temp']} | Glucose {latest['Glucose']} | O2Sat {latest['O2Sat']}")
        except Exception:
            results.append("Latest Data: N/A")
        try:
            max_glucose = df['Glucose'].max(); min_oxy = df['O2Sat'].min()
            results.append(f"Max glucose: {max_glucose} mg/dL | Min O2Sat: {min_oxy}%")
        except Exception:
            pass
        results.append('='*75 + '\n')
        self.analysis_text.insert(1.0, '\n'.join(results))
        self.notebook.select(0)

    def visualize_data(self):
        df = self.filtered_df if self.filtered_df is not None else self.df
        if df is None or df.empty:
            messagebox.showinfo('Info', 'No data to visualize.')
            return
        for widget in self.viz_tab.winfo_children():
            widget.destroy()
        try:
            fig, axes = plt.subplots(2,2, figsize=(12,8), dpi=95)
            plt.subplots_adjust(hspace=0.3, wspace=0.2, top=0.94)
            sns.set_palette('muted')
            # Ensure dates are sorted
            df = df.sort_values('Date')
            # (1) Heart Rate Trend
            sns.lineplot(ax=axes[0,0], data=df, x='Date', y='HeartRate', marker='o',label='Heart Rate (bpm)')
            axes[0,0].set_title('Heart Rate Trend', fontsize=12, fontweight='bold', color='#168aad')
            axes[0,0].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[0,0].grid(True, alpha=0.3, linestyle='--')
            # (2) BP Trend
            df = df.copy()
            df['BPS'] = df['BP_Systolic'].fillna(0).astype(int)
            df['BPD'] = df['BP_Diastolic'].fillna(0).astype(int)
            axes[0,1].plot(df['Date'], df['BPS'], marker='o', c='#22577a', label='Systolic')
            axes[0,1].plot(df['Date'], df['BPD'], marker='s', c='#91c788', label='Diastolic')
            axes[0,1].set_title('Blood Pressure Trend', fontsize=12, fontweight='bold', color='#168aad')
            axes[0,1].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[0,1].grid(True, alpha=0.3, linestyle='--')
            axes[0,1].legend()
            # (3) Temperature & O2 Saturation
            ax3 = axes[1,0]
            ax3.plot(df['Date'], df['Temp'],color='#ffa502', linewidth=2, marker='v', label='Temp (F)')
            ax3_twin = ax3.twinx()
            ax3_twin.bar(df['Date'], df['O2Sat'], color='#38a3a5', alpha=0.25, width=0.4, label='O2Sat (%)')
            ax3.set_title('Temperature & Oxygen Saturation', fontsize=11, fontweight='bold', color='#168aad')
            ax3.set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            ax3.grid(True, alpha=0.3, linestyle='--')
            # (4) Glucose Trend
            sns.lineplot(ax=axes[1,1], x='Date', y='Glucose',data=df, marker='p',color='#ff6f3c')
            axes[1,1].set_title('Glucose Level Trend', fontsize=12, fontweight='bold', color='#168aad')
            axes[1,1].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[1,1].grid(True, alpha=0.3, linestyle='--')

            # Tighten layout
            try:
                title = f"Patient: {df['PatientID'].iloc[0]} - {df['Name'].iloc[0]}"
            except Exception:
                title = "Patient Data"
            fig.suptitle(title, fontsize=15,weight='bold',color='#3498db')
            canvas = FigureCanvasTkAgg(fig, master=self.viz_tab)
            canvas.draw()
            toolbar_frame = tk.Frame(self.viz_tab)
            toolbar_frame.pack(side='top', fill='x')
            NavigationToolbar2Tk(canvas, toolbar_frame)
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)
            self.notebook.select(1)
        except Exception as e:
            messagebox.showerror('Error', f'Visualization failed:\\n{e}')

    def reset_app(self):
        self.df = None
        self.filtered_df = None
        self.patient_dropdown.config(state='disabled')
        self.status_lbl.config(text="No file loaded.", fg='#138d75')
        self.summary_txt.delete(1.0,tk.END)
        self.analysis_text.delete(1.0,tk.END)
        for widget in self.viz_tab.winfo_children():
            widget.destroy()
        messagebox.showinfo('Reset', 'Application has been reset!')
        self.notebook.select(0)

def main():
    root = tk.Tk()
    app = PatientHealthMonitor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
