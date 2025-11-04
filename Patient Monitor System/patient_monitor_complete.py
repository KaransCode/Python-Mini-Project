
"""
Patient Health Monitoring System - Enhanced Version
Built with Tkinter, Pandas, Matplotlib, and Seaborn
Now with individual chart buttons to view each vital sign separately!
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
        self.chart_btn_frame = None
        self.create_widgets()

    def create_widgets(self):
        # Title Bar
        title_frame = tk.Frame(self.root, bg='#168aad', height=80)
        title_frame.pack(fill='x')
        title_label = tk.Label(
            title_frame, text="🏥 Patient Health Monitoring System", 
            font=('Bahnschrift', 28, 'bold'),
            bg='#168aad', fg='white')
        title_label.pack(pady=25)

        # Layout: left controls, right notebook
        main_frame = tk.Frame(self.root, bg='#eafaf1')
        main_frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Controls Section (Left Panel)
        left_panel = tk.Frame(main_frame, bg='#f4f9fb', width=320, relief='sunken', borderwidth=2)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.pack_propagate(False)

        # File Upload Button
        upload_btn = tk.Button(
            left_panel, text='📂 Upload CSV', command=self.upload_file, bg='#1b6ca8', fg='white',
            font=('Arial Rounded MT Bold', 12, 'bold'), pady=14, width=22)
        upload_btn.pack(pady=(35, 10))

        # Patient Selection Dropdown
        self.patient_var = tk.StringVar()
        self.patient_dropdown = ttk.Combobox(
            left_panel, textvariable=self.patient_var, state='disabled',
            font=('Arial', 11), width=19)
        self.patient_dropdown.pack(pady=(8, 10))
        self.patient_dropdown.bind('<<ComboboxSelected>>', lambda e: self.load_patient())

        # Button Bar
        btn_frame = tk.Frame(left_panel, bg='#f4f9fb')
        btn_frame.pack(pady=(14, 8))

        self.analyze_btn = tk.Button(
            btn_frame, text='📝 Analyze', command=self.analyze_data,
            state='disabled', bg='#29ddb7', fg='black',
            font=('Bahnschrift', 11,'bold'), width=11, relief='ridge')
        self.analyze_btn.grid(row=0, column=0, padx=8, pady=8)

        self.visualize_btn = tk.Button(
            btn_frame, text='📈 All Charts', command=self.visualize_data,
            state='disabled', bg='#ffc93c', fg='black',
            font=('Bahnschrift', 11,'bold'), width=11, relief='ridge')
        self.visualize_btn.grid(row=0, column=1, padx=8, pady=8)

        self.reset_btn = tk.Button(
            left_panel, text='🔄 Reset', command=self.reset_app,
            bg='#e94f37', fg='white', font=('Bahnschrift',11,'bold'),
            width=24, relief='ridge')
        self.reset_btn.pack(pady=(10,8))

        # Status Label
        self.status_lbl = tk.Label(
            left_panel, text='No file loaded.', bg='#f4f9fb', fg='#138d75', 
            font=('Arial',10), wraplength=280)
        self.status_lbl.pack(pady=8)

        # Summary Text Box
        self.summary_txt = tk.Text(
            left_panel, height=20, font=('Consolas',10), wrap='word',
            bg='#f3f7fa', fg='#262626', borderwidth=2, relief='sunken')
        self.summary_txt.pack(fill='both', expand=True, padx=15, pady=10)

        # Right Panel: Notebook
        right_panel = tk.Frame(main_frame, bg='#f4f9fb', borderwidth=2, relief='sunken')
        right_panel.pack(side='right', fill='both', expand=True)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill='both', expand=True, padx=8, pady=8)

        # Analysis Tab
        self.analysis_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.analysis_tab, text="📝 Analysis")

        self.analysis_text = tk.Text(
            self.analysis_tab, font=('Consolas',12), bg='#f6fff9', fg='#222', wrap='word')
        self.analysis_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Visualization Tab
        self.viz_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.viz_tab, text="📈 Visualizations")

        # Chart Selection Buttons (in viz_tab)
        self.chart_btn_frame = tk.Frame(self.viz_tab, bg='white')
        self.chart_btn_frame.pack(side='top', pady=12)

        tk.Button(
            self.chart_btn_frame, text="❤️ Heart Rate", bg='#51cf66', fg='black',
            font=('Arial Rounded MT Bold', 11), command=self.show_heart_rate_chart,
            padx=10, pady=8).pack(side='left', padx=8)

        tk.Button(
            self.chart_btn_frame, text="💉 Blood Pressure", bg='#339af0', fg='white',
            font=('Arial Rounded MT Bold', 11), command=self.show_bp_chart,
            padx=10, pady=8).pack(side='left', padx=8)

        tk.Button(
            self.chart_btn_frame, text="🌡️ Temp & O2", bg='#ffd43b', fg='black',
            font=('Arial Rounded MT Bold', 11), command=self.show_temp_o2_chart,
            padx=10, pady=8).pack(side='left', padx=8)

        tk.Button(
            self.chart_btn_frame, text="🍬 Glucose", bg='#f08080', fg='white',
            font=('Arial Rounded MT Bold', 11), command=self.show_glucose_chart,
            padx=10, pady=8).pack(side='left', padx=8)

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Patient Health CSV", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.df = pd.read_csv(file_path)
            # Clean data
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
            num_cols = ['HeartRate','BP_Systolic','BP_Diastolic','Temp','Glucose','O2Sat']
            for col in num_cols:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.df.dropna(subset=['PatientID','Date'], inplace=True)
            self.filtered_df = None

            # Populate patient dropdown
            self.patients = self.df['PatientID'].astype(str) + ' - ' + self.df['Name']
            unique_patients = self.patients.drop_duplicates().tolist()
            self.patient_dropdown['values'] = unique_patients
            self.patient_dropdown.config(state='readonly')
            self.patient_var.set(unique_patients[0])

            self.status_lbl.config(
                text=f"✅ Loaded: {file_path.split('/')[-1]} | {len(self.df)} records", 
                fg='#168aad')
            self.analyze_btn.config(state='normal')
            self.visualize_btn.config(state='normal')
            self.show_summary()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load file:\n{e}')
            self.status_lbl.config(text="❌ Error loading file.", fg='#e94f37')

    def show_summary(self):
        df = self.df.copy()
        summary = []
        summary.append(f"Patients: {df['PatientID'].nunique()}")
        summary.append(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        summary.append(f"Records: {len(df)}")
        summary.append(f"Avg HR: {df['HeartRate'].mean():.1f}")
        summary.append(f"Avg BP: {df['BP_Systolic'].mean():.1f}/{df['BP_Diastolic'].mean():.1f}")
        summary.append(f"Avg Temp: {df['Temp'].mean():.1f} F")
        summary.append(f"Avg Glucose: {df['Glucose'].mean():.1f} mg/dL")
        summary.append(f"Avg O2Sat: {df['O2Sat'].mean():.1f}%")
        self.summary_txt.delete(1.0, tk.END)
        self.summary_txt.insert(1.0,'\n'.join(summary))

    def load_patient(self):
        if self.df is None:
            return
        selpid = self.patient_var.get().split(' - ')[0]
        self.filtered_df = self.df[self.df['PatientID'] == selpid].copy()
        self.status_lbl.config(text=f"Selected: {self.patient_var.get()}", fg='#337a5b')
        self.show_patient_summary()

    def show_patient_summary(self):
        df = self.filtered_df if self.filtered_df is not None else self.df
        summary = []
        summary.append(f"Patient: {df['PatientID'].iloc[0]} - {df['Name'].iloc[0]}")
        summary.append(f"Records: {len(df)} | Days: {df['Date'].dt.date.nunique()}")
        summary.append(f"Avg HR: {df['HeartRate'].mean():.1f}")
        summary.append(f"BP: {df['BP_Systolic'].mean():.1f}/{df['BP_Diastolic'].mean():.1f}")
        summary.append(f"Avg Temp: {df['Temp'].mean():.1f} F")
        summary.append(f"Avg Glucose: {df['Glucose'].mean():.1f} mg/dL")
        summary.append(f"Avg O2Sat: {df['O2Sat'].mean():.1f}%")
        self.summary_txt.delete(1.0, tk.END)
        self.summary_txt.insert(1.0, '\n'.join(summary))

    def analyze_data(self):
        df = self.filtered_df if self.filtered_df is not None else self.df
        self.analysis_text.delete(1.0, tk.END)

        results = []
        results.append('='*75)
        results.append(f"{'PATIENT HEALTH ANALYSIS REPORT':^75}")
        results.append('='*75+'\n')
        results.append(f"Patient: {df['PatientID'].iloc[0]} - {df['Name'].iloc[0]}")
        results.append(f"Records: {len(df)}")
        results.append(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        results.append('-'*50)

        # Averages
        metrics = ['HeartRate','BP_Systolic','BP_Diastolic','Temp','Glucose','O2Sat']
        units = ['bpm','mmHg','mmHg','F','mg/dL','%']
        means = [f"{df[c].mean():.1f} {u}" for c,u in zip(metrics,units)]
        results.append(f"Averages: HR {means[0]}, BP {means[1]}/{means[2]}, Temp {means[3]}, Glucose {means[4]}, O2 {means[5]}")

        # Alerts
        alerts = []
        if df['HeartRate'].max() > 100 or df['HeartRate'].min() < 55:
            alerts.append('Abnormal heart rate detected.')
        if df['BP_Systolic'].max() > 135 or df['BP_Diastolic'].max() > 90:
            alerts.append('Abnormal blood pressure detected.')
        if df['Temp'].max() > 100.5 or df['Temp'].min() < 96.5:
            alerts.append('Abnormal temperature readings.')
        if df['Glucose'].max() > 160 or df['Glucose'].min() < 65:
            alerts.append('Possible glucose issues detected.')
        if df['O2Sat'].min() < 94:
            alerts.append('Low O2 saturation detected.')

        results.append('-'*50)
        results.append('Alerts/Risks: '+ (', '.join(alerts) if alerts else 'None'))

        # Latest reading
        latest = df.sort_values('Date',ascending=False).iloc[0]
        results.append(f"Latest: {latest['Date'].date()} | HR {latest['HeartRate']} | BP {latest['BP_Systolic']}/{latest['BP_Diastolic']} | Temp {latest['Temp']} | Glucose {latest['Glucose']} | O2 {latest['O2Sat']}")
        results.append('='*75+'\n')

        self.analysis_text.insert(1.0, '\n'.join(results))
        self.notebook.select(0)

    def visualize_data(self):
        """Show all 4 charts in a 2x2 grid"""
        df = self.filtered_df if self.filtered_df is not None else self.df
        self.clear_viz_tab()

        try:
            fig, axes = plt.subplots(2,2, figsize=(12,8), dpi=95)
            plt.subplots_adjust(hspace=0.3, wspace=0.25, top=0.94)

            # (1) Heart Rate
            sns.lineplot(ax=axes[0,0], data=df, x='Date', y='HeartRate', marker='o',color='#168aad')
            axes[0,0].set_title('Heart Rate Trend', fontsize=12, fontweight='bold')
            axes[0,0].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[0,0].grid(True, alpha=0.3, linestyle='--')

            # (2) BP
            axes[0,1].plot(df['Date'], df['BP_Systolic'], marker='o', c='#22577a', label='Systolic')
            axes[0,1].plot(df['Date'], df['BP_Diastolic'], marker='s', c='#91c788', label='Diastolic')
            axes[0,1].set_title('Blood Pressure Trend', fontsize=12, fontweight='bold')
            axes[0,1].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[0,1].grid(True, alpha=0.3, linestyle='--')
            axes[0,1].legend()

            # (3) Temp & O2
            axes[1,0].plot(df['Date'], df['Temp'],color='#ffa502', linewidth=2, marker='v')
            axes[1,0].set_title('Temperature & O2 Saturation', fontsize=11, fontweight='bold')
            axes[1,0].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[1,0].grid(True, alpha=0.3, linestyle='--')

            # (4) Glucose
            sns.lineplot(ax=axes[1,1], x='Date', y='Glucose',data=df, marker='p',color='#ff6f3c')
            axes[1,1].set_title('Glucose Level Trend', fontsize=12, fontweight='bold')
            axes[1,1].set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
            axes[1,1].grid(True, alpha=0.3, linestyle='--')

            fig.suptitle(f"Patient: {df['PatientID'].iloc[0]} - {df['Name'].iloc[0]}", 
                        fontsize=15,weight='bold',color='#168aad')

            canvas = FigureCanvasTkAgg(fig, master=self.viz_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)
            self.notebook.select(1)
        except Exception as e:
            messagebox.showerror('Error', f'Visualization failed:\n{e}')

    def clear_viz_tab(self):
        """Clear visualization tab except button frame"""
        for widget in self.viz_tab.winfo_children():
            if widget is self.chart_btn_frame:
                continue
            widget.destroy()

    def show_heart_rate_chart(self):
        self.clear_viz_tab()
        df = self.filtered_df if self.filtered_df is not None else self.df
        if df is None or df.empty:
            return

        fig, ax = plt.subplots(figsize=(11,5), dpi=95)
        sns.lineplot(ax=ax, data=df, x='Date', y='HeartRate', marker='o', color='#168aad', linewidth=2.5)
        ax.set_title('❤️ Heart Rate Trend', fontsize=14, fontweight='bold', color='#168aad')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Heart Rate (bpm)', fontweight='bold')
        ax.set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
        ax.grid(True, alpha=0.3, linestyle='--')

        canvas = FigureCanvasTkAgg(fig, master=self.viz_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)
        self.notebook.select(1)

    def show_bp_chart(self):
        self.clear_viz_tab()
        df = self.filtered_df if self.filtered_df is not None else self.df
        if df is None or df.empty:
            return

        fig, ax = plt.subplots(figsize=(11,5), dpi=95)
        ax.plot(df['Date'], df['BP_Systolic'], marker='o', c='#22577a', label='Systolic', linewidth=2.5)
        ax.plot(df['Date'], df['BP_Diastolic'], marker='s', c='#91c788', label='Diastolic', linewidth=2.5)
        ax.set_title('💉 Blood Pressure Trend', fontsize=14, fontweight='bold', color='#168aad')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('BP (mmHg)', fontweight='bold')
        ax.set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11)

        canvas = FigureCanvasTkAgg(fig, master=self.viz_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)
        self.notebook.select(1)

    def show_temp_o2_chart(self):
        self.clear_viz_tab()
        df = self.filtered_df if self.filtered_df is not None else self.df
        if df is None or df.empty:
            return

        fig, ax1 = plt.subplots(figsize=(11,5), dpi=95)
        ax1.plot(df['Date'], df['Temp'], color='#ffa502', linewidth=2.5, marker='v', label='Temperature (F)')
        ax1.set_ylabel('Temperature (F)', color='#ffa502', fontweight='bold')
        ax1.set_xlabel('Date', fontweight='bold')
        ax1.set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
        ax1.set_title('🌡️ Temperature & Oxygen Saturation', fontsize=14, fontweight='bold', color='#168aad')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.tick_params(axis='y', labelcolor='#ffa502')

        ax2 = ax1.twinx()
        ax2.bar(df['Date'], df['O2Sat'], color='#38a3a5', alpha=0.3, width=0.5, label='O2 Sat (%)')
        ax2.set_ylabel('Oxygen Saturation (%)', color='#38a3a5', fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='#38a3a5')

        canvas = FigureCanvasTkAgg(fig, master=self.viz_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)
        self.notebook.select(1)

    def show_glucose_chart(self):
        self.clear_viz_tab()
        df = self.filtered_df if self.filtered_df is not None else self.df
        if df is None or df.empty:
            return

        fig, ax = plt.subplots(figsize=(11,5), dpi=95)
        sns.lineplot(ax=ax, x='Date', y='Glucose', data=df, marker='p', color='#ff6f3c', linewidth=2.5)
        ax.set_title('🍬 Glucose Level Trend', fontsize=14, fontweight='bold', color='#168aad')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Glucose (mg/dL)', fontweight='bold')
        ax.set_xticklabels(df['Date'].dt.strftime('%b %d'),rotation=25)
        ax.grid(True, alpha=0.3, linestyle='--')

        canvas = FigureCanvasTkAgg(fig, master=self.viz_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)
        self.notebook.select(1)

    def reset_app(self):
        self.df = None
        self.filtered_df = None
        self.patient_dropdown.set('')
        self.patient_dropdown['values'] = []
        self.patient_dropdown.config(state='disabled')
        self.status_lbl.config(text="No file loaded.", fg='#138d75')
        self.summary_txt.delete(1.0,tk.END)
        self.analysis_text.delete(1.0,tk.END)
        self.clear_viz_tab()
        self.analyze_btn.config(state='disabled')
        self.visualize_btn.config(state='disabled')
        messagebox.showinfo('Reset', 'Application has been reset!')
        self.notebook.select(0)

def main():
    root = tk.Tk()
    app = PatientHealthMonitor(root)
    root.mainloop()

if __name__ == '__main__':
    main()