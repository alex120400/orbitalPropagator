import shutil

try:
    # import sys
    import os
    # import threading
    import tkinter as tk
    from tkinter import messagebox as mbox
    from tkinter import filedialog
    from tkinter import scrolledtext as st
    import tkinter.ttk as ttk
    import numpy as np

    # import scipy.fft as fft
    # from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
    # import matplotlib.pyplot as plt
    from skyfield.api import load as sky_load

    from utils.configManager import MISSION_PLAN_PATH, EPHEMERIDES_PATH, OGS_TLE_FILE
    import preprocessing as pre
    import freeflyer as ff
    import tracking

except ModuleNotFoundError as msg:
    print('Failed to load modules. \n' + str(msg))

class APP(tk.Tk):
    """Builds the GUI"""

    def __init__(self):
        """initialises the GUI and starts the build up process

        defines all relevant varibles for the main window of the GUI
        """
        super().__init__()
        # ATTRIBUTES
        self.icon = "saturn_icon.ico"
        # Some window parameters
        self.WIN_SIZE_POS = '780x580'
        self.PLOT_WIDTH = 5.5
        self.PLOT_HEIGHT = 2.5
        # Padding for all containers to uniformize the look
        self.CONTAINER_PADX = 10
        self.CONTAINER_PADY = 6.5
        # Padding for all widgets inside a container
        self.WIDGET_PADX = 2.5
        self.WIDGET_PADY = 2.5

        # tab structure & frames
        self.master_tab_holder_frame = ttk.Frame(self, relief='groove')
        self.master_tab_holder = ttk.Notebook(self.master_tab_holder_frame)
        self.preprocessing_tab = ttk.Frame(self.master_tab_holder)
        self.camera_tab = ttk.Frame(self.master_tab_holder)
        self.tracking_tab = ttk.Frame(self.master_tab_holder)
        self.postprocessing_tab = ttk.Frame(self.master_tab_holder)

        # important variables
        self.ts = sky_load.timescale()
        self.startup_time = self.ts.now()
        self.year = tk.IntVar(value=self.startup_time.utc.year)
        self.month = tk.IntVar(value=self.startup_time.utc.month)
        self.day = tk.IntVar(value=self.startup_time.utc.day)
        self.hour = tk.IntVar(value=self.startup_time.utc.hour)
        self.minute = tk.IntVar(value=self.startup_time.utc.minute)
        self.dr_hour = tk.IntVar(value=1)
        self.dr_minute = tk.IntVar(value=30)
        self.use_ogs_TLEs = tk.BooleanVar(value=False)
        self.use_spaceTrack_TLEs = tk.BooleanVar(value=True)
        self.sat_tree = None # will be ttk.Treeview
        self.mission_runner = ff.MissionPlanRunner()
        self.eph_preview = None # will be st.ScrolledText
        self.eph_file = None # will be string of filepath
        self.tle_age_info = tk.StringVar(value=f"TLE sources are {pre.get_TLE_data_aga(ogs_flag=False)} days old")
        self.tel_conn_status_label = None # will be tk.Label (tk instead of ttk because coloring is easier)
        self.telescope = tracking.TelescopeWrapper()
        self.tracking_status_label = None # will be tk.Label (tk instead of ttk because coloring is easier)

        # # threads
        # self.timing_thread = None  # will be a new thread each time there is a new measurement started
        # self.measuring_thread = None  # will be a new thread each time there is a new measurement started
        # self.converting_thread = None  # will be a new thread each time there is a new measurement started

        # # plotting
        # self.canvas = None  # drawing area
        # self.fig = None  # configured in respective frame creation function
        # self.ax = None  # configured in respective frame creation function
        # self.pickradius = 5  # Points (Pt). How close the click needs to be to trigger an event.

        # Allows root window to be closed by the closing icon.
        self.protocol('WM_DELETE_WINDOW', self._app_quit)

        # Set up the layout of the main window.
        self._window_setup()

    def _app_quit(self):
        """ Quit application """
        err_msg = None
        if self.telescope.connected_flag: # disconnect telescope
            err_msg = self.telescope.disconnect_telescope()
        if err_msg is None:
            self.destroy()
        else:
            mbox.showerror(title="Error while exiting -> aborted", message=err_msg)

    def _window_setup(self):
        """ Some basic setup is done on the GUI """
        # WINDOW
        self.title('Tracking application')
        self.geometry(self.WIN_SIZE_POS)
        self.iconbitmap(self.icon)

        # tab like structure will be used on top, below sensor status field
        self.master_tab_holder_frame.pack(fill='both', expand=True, padx=self.CONTAINER_PADX, pady=self.CONTAINER_PADY)
        self.master_tab_holder.pack(fill='both', expand=True, padx=self.WIDGET_PADX, pady=self.WIDGET_PADY)

        # add tabs and status frame
        self._create_preprocessing_tab()
        self._create_camera_tab()
        self._create_tracking_tab()
        self._create_postprocessing_tab()

    def _create_preprocessing_tab(self):
        self.preprocessing_tab.columnconfigure(0, weight=1)
        self.preprocessing_tab.columnconfigure(1, weight=1)

        # four distinct zones: time conf, tle sources, satellite summary, freeflyer execution
        self.watch_window_frame = ttk.LabelFrame(self.preprocessing_tab, text="Watch Window Configuration")
        self.satellite_summary_frame = ttk.LabelFrame(self.preprocessing_tab, text="Satellite Summary")
        self.tle_sources_frame = ttk.LabelFrame(self.preprocessing_tab, text="TLE Sources")
        self.freeFlyer_frame = ttk.LabelFrame(self.preprocessing_tab, text="FreeFlyer Execution")

        # watch window setup
        for i in range(6):
            self.watch_window_frame.columnconfigure(i, weight=1)
        ttk.Entry(self.watch_window_frame, textvariable=self.year, width=10, justify="center").grid(row=2, column=0)
        ttk.Entry(self.watch_window_frame, textvariable=self.month, width=10, justify="center").grid(row=2, column=1)
        ttk.Entry(self.watch_window_frame, textvariable=self.day, width=10, justify="center").grid(row=2, column=2)
        ttk.Entry(self.watch_window_frame, textvariable=self.hour, width=10, justify="center").grid(row=4, column=0)
        ttk.Entry(self.watch_window_frame, textvariable=self.minute, width=10, justify="center").grid(row=4, column=1)
        ttk.Entry(self.watch_window_frame, textvariable=self.dr_hour, width=10, justify="center").grid(row=2, column=4)
        ttk.Entry(self.watch_window_frame, textvariable=self.dr_minute, width=10, justify="center").grid(row=2, column=5)
        for widget in self.watch_window_frame.winfo_children():
            widget.grid_configure(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky="nesw")
        ttk.Label(self.watch_window_frame, text="Start:", justify="center").grid(row=0, column=0, columnspan=3)
        ttk.Label(self.watch_window_frame, text="Duration:", justify="center").grid(row=0, column=4, columnspan=2)
        for txt, rw in zip(["Year:", "Month:", "Day:", "Hour:", "Minute:", "Hour:", "Minute:"],
                            [(1, 0), (1, 1), (1, 2), (3, 0), (3, 1), (1, 4), (1, 5)]):
            ttk.Label(self.watch_window_frame, text=txt, justify="center").grid(row=rw[0], column=rw[1])
        ttk.Separator(self.watch_window_frame, orient="vertical").grid(row=0, rowspan=5,column=3, sticky="ns")
        self.watch_window_frame.grid(row=0, column=0)

        # tle sources setup
        self.tle_sources_frame.columnconfigure(0, weight=1)
        ttk.Checkbutton(self.tle_sources_frame, variable=self.use_ogs_TLEs, text="CelesTrack data (OGS)", onvalue=True,
                        offvalue=False, command= lambda: self._toggle_tle_source(self.use_spaceTrack_TLEs))\
            .grid(row=0, column=0)
        ttk.Checkbutton(self.tle_sources_frame, variable=self.use_spaceTrack_TLEs, text="SpaceTrack data (LEO)",
                        onvalue=True, offvalue=False, command= lambda: self._toggle_tle_source(self.use_ogs_TLEs))\
            .grid(row=1, column=0)
        ttk.Label(self.tle_sources_frame, textvariable=self.tle_age_info).grid(row=2, column=0)
        ttk.Button(self.tle_sources_frame, command=self._update_tle_sources, text="Update TLE Source")\
            .grid(row=3, column=0)
        for widget in self.tle_sources_frame.winfo_children():
            widget.grid_configure(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky="NESW")
        self.tle_sources_frame.grid(row=0, column=1)

        # satellite list
        self.satellite_summary_frame.columnconfigure(0, weight=1)
        self.satellite_summary_frame.columnconfigure(1, weight=1)
        ttk.Button(self.satellite_summary_frame, text="Update Satellite List",
                   command=self._update_satellite_list).grid(row=0, column=0)
        ttk.Button(self.satellite_summary_frame, text="Export TLE data for selected satellites",
                   command=self._export_satellites).grid(row=0, column=1)
        self._tree_frame = ttk.Frame(self.satellite_summary_frame)
        scrollbar = ttk.Scrollbar(self._tree_frame)
        scrollbar.pack(side='right', fill='y')

        columns = ('name', 'norad', 'timeToRise', 'visibleTime',
                   'sunlit', 'height', 'elev')

        self.sat_tree = ttk.Treeview(self._tree_frame, columns=columns,
                                    show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(orient=tk.VERTICAL, command=self.sat_tree.yview)

        self.sat_tree.heading('name', text='Name')
        self.sat_tree.heading('norad', text="Norad-ID")
        self.sat_tree.heading('timeToRise', text="Time to rising")
        self.sat_tree.heading('visibleTime', text="Time visible")
        self.sat_tree.heading('sunlit', text="Sunlit")
        self.sat_tree.heading('height', text="Height")
        self.sat_tree.heading('elev', text="Max. Elevation")

        # name column receives the most space and can stretch
        for id_, width in zip(columns, [140, 80, 110, 110, 80, 80, 110]):
            self.sat_tree.column(id_, width=width)

        self.sat_tree.pack(side='left', fill='both', expand=True,
                       padx=self.WIDGET_PADX, pady=self.WIDGET_PADY)

        self._tree_frame.grid(row=1, column=0, columnspan=2)
        for widget in self.satellite_summary_frame.winfo_children():
            widget.grid_configure(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky="NESW")

        self.satellite_summary_frame.grid(row=1, column=0, columnspan=2)

        # satellite list setup
        self.freeFlyer_frame.columnconfigure(0, weight=1)
        self.freeFlyer_frame.columnconfigure(1, weight=1)
        ttk.Button(self.freeFlyer_frame, text="Generate Ephemerides based on SGP4",
                   command=self._ff_sgp4_eph).grid(row=0, column=0, padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky="NESW")
        ttk.Button(self.freeFlyer_frame, text="Generate Ephemerides based on Orbit Determination",
                   command=self._ff_od_eph).grid(row=0, column=1, padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky="NESW")
        self.freeFlyer_frame.grid(row=2, column=0, columnspan=2)

        # tab layout
        for widget in self.preprocessing_tab.winfo_children():
            widget.grid_configure(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky='NESW')
        self.master_tab_holder.add(self.preprocessing_tab, text='Preprocessing', sticky='NSEW')

    def _toggle_tle_source(self, tk_bool_var:tk.BooleanVar):
        tk_bool_var.set(False) # needed at the beginning for logic to work
        if self.use_ogs_TLEs.get() is True:
            self.tle_age_info.set(f"TLE sources are {pre.get_TLE_data_aga(ogs_flag=True)} days old")
        elif self.use_spaceTrack_TLEs.get() is True:
            self.tle_age_info.set(f"TLE sources are {pre.get_TLE_data_aga(ogs_flag=False)} days old")
        else:
            self.tle_age_info.set("Select TLE Source")

    def _update_tle_sources(self):
        if self.use_ogs_TLEs.get() is True:
            if sky_load.days_old(OGS_TLE_FILE) > 0.01:
                if pre.update_ogs_TLE_data() is True: # allow updates every 15 min
                    mbox.showinfo(title="Info", message="Updated CelesTrack (OGS) TLE sources!")
                    self.tle_age_info.set(f"TLE sources are {pre.get_TLE_data_aga(ogs_flag=True)} days old")
                    return
                else:
                    mbox.showerror(title="Error", message="Could not update CelesTack (OGS) TLE sources, check log!")
                    return
            else:
                mbox.showwarning(title="Warning", message="Updates only possible every 15 minutes!")
        elif self.use_spaceTrack_TLEs.get() is True:
            if sky_load.days_old(pre.LEO_TLE_FILE) > 0.01: # allow updates every 15 min
                if pre.update_LEO_TLE_data() is True:
                    mbox.showinfo(title="Info", message="Updated SpaceTrack (LEO) TLE sources!")
                    self.tle_age_info.set(f"TLE sources are {pre.get_TLE_data_aga(ogs_flag=False)} days old")
                    return
                else:
                    mbox.showerror(title="Error", message="Could not update SpaceTrack (LEO) TLE sources, check log!")
                    return
            else:
                mbox.showwarning(title="Warning", message="Updates only possible every 15 minutes!")
        else:
            mbox.showerror(title="Error", message="Select TLE Source first!")
            return

    def _update_satellite_list(self):
        start_time = self.ts.utc(self.year.get(),
                                 self.month.get(),
                                 self.day.get(),
                                 self.hour.get(),
                                 self.minute.get())
        duration = self.dr_hour.get() * 60 + self.dr_minute.get()

        print(start_time)
        self.sat_data_list, self.sat_tle_dict = pre.create_satellite_data_list(start_time, duration,
                                                                               ogs_flag=self.use_ogs_TLEs.get())

        # sort by time to rise, item = x.y min
        self.sat_data_list.sort(key = lambda item: float(item[2].strip().split()[0]))

        self.sat_tree.delete(*self.sat_tree.get_children())  # clears table before refill
        for sat_data in self.sat_data_list:  # refill
            self.sat_tree.insert('', tk.END, values=sat_data)
        return


    def _export_satellites(self):
        selected_items = self.sat_tree.selection()
        if len(selected_items) > 0:
            with open(os.path.join(MISSION_PLAN_PATH, "TLE_export.tle"), "w", encoding='utf-8') as f:
                for _id in selected_items:
                    sat_key = self.sat_tree.item(_id).get("values")[1]  # NoradID
                    for line in self.sat_tle_dict[sat_key]:
                        f.write(line)
        mbox.showinfo("Info", "Exported selected TLE data!")

    def _ff_sgp4_eph(self):
        start_time = self.ts.utc(self.year.get(),
                                 self.month.get(),
                                 self.day.get(),
                                 self.hour.get(),
                                 self.minute.get())
        durationMin = self.dr_hour.get() * 60 + self.dr_minute.get()
        startTimeString = start_time.utc_strftime("%b %d %Y %H:%M:%S")
        os.mkdir(os.path.join(MISSION_PLAN_PATH, "tmp")) # eph files will be put there
        self.mission_runner.run_SGP4_EPH_plan(durationMin, startTimeString)
        if self.mission_runner.missionplan_success_flag:
            # now there exist files called "ASATrackingData_xy.txt"
            eph_dir = os.path.join(EPHEMERIDES_PATH, start_time.utc_strftime(f"%Y%b%d__%H_%M__{durationMin}"))
            # check if dir exits:
            if not os.path.isdir(eph_dir):
                os.mkdir(eph_dir) # create if non-existing
            for eph_file in os.listdir(os.path.join(MISSION_PLAN_PATH, "tmp")):
                if eph_file.startswith("ASATrackingData"):
                    shutil.move(os.path.join(MISSION_PLAN_PATH, "tmp", eph_file), str(eph_dir))
            # moved all eph files
            mbox.showinfo("Info", "Generated Ephemerides!")
        else:
            mbox.showerror("Error", message=
                            f"There was an error while executing the missionplan:\n{self.mission_runner.error_msg}")
        shutil.rmtree(os.path.join(MISSION_PLAN_PATH, "tmp"), ignore_errors=False)


    def _ff_od_eph(self):
        pass


    def _create_camera_tab(self):
        pass

    def _create_tracking_tab(self):
        #self.tracking_tab.columnconfigure(0, weight=1)
        self.tracking_tab.rowconfigure(0, weight=0)

        # will have two zones: eph selection and telescope
        ## eph selection and preview setup
        self.eph_frame = ttk.LabelFrame(self.tracking_tab, text="Ephemeris selection and inspection")
        ttk.Button(self.eph_frame, text="Select Ephemeris file", command=self._select_eph_file) \
            .pack(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, expand=True, fill='x')
        self.eph_preview = st.ScrolledText(self.eph_frame, width=90, height=20)
        self.eph_preview.pack(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, fill='x')
        self.eph_frame.grid(row=0, column=0, columnspan=2)

        # tracking & telescope options
        self.telescope_frame = ttk.LabelFrame(self.tracking_tab, text="Telescope setup & tracking")
        ttk.Button(self.telescope_frame, text="Toggle telescope connection", command=self._toggle_telescope_conn) \
            .grid(row=0, column=0)
        self.tel_conn_status_label = tk.Label(self.telescope_frame, text="Disconnected", bg="red")
        self.tel_conn_status_label.grid(row=0, column=1)
        ttk.Button(self.telescope_frame, text="Start tracking", command=self._start_tracking) \
            .grid(row=1, column=0)
        self.tracking_status_label = tk.Label(self.telescope_frame, text="Not Tracking", bg="red")
        self.tracking_status_label.grid(row=1, column=1)
        ttk.Button(self.telescope_frame, text="Request Telescope Status", command=self._get_telescope_status) \
            .grid(row=2, column=0)


        # layout
        for widget in self.tracking_tab.winfo_children():
            widget.grid_configure(padx=self.WIDGET_PADX, pady=self.WIDGET_PADY, sticky='NESW')
        self.master_tab_holder.add(self.tracking_tab, text='Tracking', sticky='NSEW')

    def _select_eph_file(self):
        self.eph_preview.configure(state="normal")
        self.eph_preview.delete("1.0", "end")
        self.eph_file = filedialog.askopenfilename(title="Select ephemeris file",
                                                   filetypes=[("Ephemeris Files", ".eph")])

        if os.path.exists(self.eph_file): # check if file has been chosen
            # Inserting eph data which is read only
            with open(self.eph_file) as f:
                self.eph_preview.insert("1.0", f.read())
        # Making the text read only
        self.eph_preview.configure(state='disabled')

    def _toggle_telescope_conn(self):
        if self.telescope.connected_flag:
            # telescope is connected, -> disconnect
            err_msg = self.telescope.disconnect_telescope()
        else:
            # telescope not yet connected -> connect
            err_msg = self.telescope.connect_telescope()

        if err_msg is None:
            if self.telescope.connected_flag:
                self.tel_conn_status_label.config(text="Connected", bg="green")
            else:
                self.tel_conn_status_label.config(text="Disconnected", bg="red")
        else:
            mbox.showerror(title="Error", message=err_msg)

    def _start_tracking(self):
        if self.eph_file is not None and os.path.exists(self.eph_file):
            err_msg = self.telescope.start_track(self.eph_file)

            if err_msg is not None:
                mbox.showerror(title="Error", message=err_msg)
            else:
                self.tracking_status_label.config(text="Tracking", bg="green")
        else:
            mbox.showerror(title="Error", message="Ephemeris File not configured correctly!")

    def _get_telescope_status(self):
        err_msg = self.telescope.get_status()
        if err_msg is not None:
            mbox.showerror(title="Error", message=err_msg)


    def _create_postprocessing_tab(self):
        pass


if __name__ == "__main__":
    app = APP()
    app.mainloop()
