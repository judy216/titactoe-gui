#!/usr/bin/env python3.12
"""
Mosques Management System
A friendly desktop app for managing mosque records.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import difflib
import webbrowser
import os
import tempfile
import folium

from database import MosqueDatabase


# ── colour palette ─────────────────────────────────────────────────────────
BG_MAIN   = "#F5F0E8"   # warm ivory
BG_PANEL  = "#EDE8DC"   # slightly darker panel
ACCENT    = "#2E7D32"   # mosque green
ACCENT2   = "#1565C0"   # deep blue for map button
BTN_DEL   = "#C62828"   # red for delete
BTN_TXT   = "#FFFFFF"
HEADING   = "#1B5E20"
ENTRY_BG  = "#FFFFFF"
LIST_BG   = "#FAFAF5"
LIST_SEL  = "#C8E6C9"


class MosquesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mosques Management System")
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.minsize(900, 560)

        self.db = MosqueDatabase()
        self._build_ui()
        self._seed_demo_data()
        self._display_all()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        # ── title bar ──────────────────────────────────────────────────────
        title_frame = tk.Frame(self, bg=ACCENT, pady=8)
        title_frame.pack(fill=tk.X)
        tk.Label(
            title_frame, text="🕌  Mosques Management System",
            font=("Segoe UI", 16, "bold"), bg=ACCENT, fg=BTN_TXT
        ).pack()

        # ── main content ───────────────────────────────────────────────────
        content = tk.Frame(self, bg=BG_MAIN)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self._build_form(content)
        self._build_listbox(content)
        self._build_buttons(content)
        self._build_status_bar()

    def _build_form(self, parent):
        """Left-side input form (Part 1)."""
        form = tk.LabelFrame(
            parent, text="  Mosque Details  ", bg=BG_PANEL,
            fg=HEADING, font=("Segoe UI", 10, "bold"),
            relief=tk.GROOVE, bd=2, labelanchor="n"
        )
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        parent.columnconfigure(0, weight=2)
        parent.columnconfigure(1, weight=3)
        parent.rowconfigure(0, weight=1)

        fields = [
            ("ID",          "id"),
            ("Name",        "name"),
            ("Type",        "type"),
            ("Address",     "address"),
            ("Coordinates", "coordinates"),
            ("Imam Name",   "imam"),
        ]

        self.entries = {}
        for i, (label_text, key) in enumerate(fields):
            tk.Label(
                form, text=label_text + ":", bg=BG_PANEL, fg="#333",
                font=("Segoe UI", 10), anchor="e", width=12
            ).grid(row=i, column=0, sticky="e", padx=(10, 4), pady=6)

            if key == "type":
                var = tk.StringVar(value="Jami")
                widget = ttk.Combobox(
                    form, textvariable=var,
                    values=["Jami", "Masjid", "Friday Mosque", "Grand Mosque", "Historical"],
                    state="readonly", width=22, font=("Segoe UI", 10)
                )
                widget.grid(row=i, column=1, sticky="w", padx=(0, 10), pady=6)
                self.entries[key] = var
            else:
                var = tk.StringVar()
                entry = tk.Entry(
                    form, textvariable=var, width=24,
                    font=("Segoe UI", 10), bg=ENTRY_BG,
                    relief=tk.SOLID, bd=1
                )
                entry.grid(row=i, column=1, sticky="ew", padx=(0, 10), pady=6)
                self.entries[key] = var

        form.columnconfigure(1, weight=1)

    def _build_listbox(self, parent):
        """Right-side listbox (Part 2)."""
        list_frame = tk.LabelFrame(
            parent, text="  Mosque Records  ", bg=BG_PANEL,
            fg=HEADING, font=("Segoe UI", 10, "bold"),
            relief=tk.GROOVE, bd=2, labelanchor="n"
        )
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            list_frame, font=("Courier New", 9), bg=LIST_BG,
            selectbackground=LIST_SEL, selectforeground="#000",
            relief=tk.FLAT, bd=0, activestyle="none",
            highlightthickness=1, highlightcolor=ACCENT
        )
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=6)
        self.listbox.configure(yscrollcommand=scrollbar.set)

    def _build_buttons(self, parent):
        """Bottom button panel (Parts 3 & 4)."""
        btn_frame = tk.Frame(parent, bg=BG_MAIN, pady=10)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        # group 1 – primary actions
        g1 = tk.LabelFrame(btn_frame, text=" Core Actions ", bg=BG_MAIN, fg=HEADING,
                            font=("Segoe UI", 9, "bold"), relief=tk.GROOVE)
        g1.pack(side=tk.LEFT, padx=(0, 12))

        self._btn(g1, "Display All",   self._display_all,   ACCENT).grid(row=0, column=0, padx=6, pady=6)
        self._btn(g1, "Search",        self._search,        ACCENT).grid(row=0, column=1, padx=6, pady=6)
        self._btn(g1, "Add Entry",     self._add_entry,     ACCENT).grid(row=1, column=0, padx=6, pady=6)
        self._btn(g1, "Delete Entry",  self._delete_entry,  BTN_DEL).grid(row=1, column=1, padx=6, pady=6)

        # group 2 – extra features
        g2 = tk.LabelFrame(btn_frame, text=" Extra Features ", bg=BG_MAIN, fg=ACCENT2,
                            font=("Segoe UI", 9, "bold"), relief=tk.GROOVE)
        g2.pack(side=tk.LEFT, padx=(0, 12))

        self._btn(g2, "Update Imam",   self._update_imam,   ACCENT2).grid(row=0, column=0, padx=6, pady=6)
        self._btn(g2, "Display on Map",self._display_map,   ACCENT2).grid(row=0, column=1, padx=6, pady=6)

        # group 3 – utility
        g3 = tk.LabelFrame(btn_frame, text=" Utility ", bg=BG_MAIN, fg="#555",
                            font=("Segoe UI", 9, "bold"), relief=tk.GROOVE)
        g3.pack(side=tk.LEFT)

        self._btn(g3, "Clear Fields",  self._clear_fields,  "#757575").grid(row=0, column=0, padx=6, pady=6)

    def _btn(self, parent, text, command, color):
        return tk.Button(
            parent, text=text, command=command,
            bg=color, fg=BTN_TXT, font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            activebackground=color, activeforeground=BTN_TXT
        )

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Welcome! System ready.")
        bar = tk.Label(
            self, textvariable=self.status_var, bg=ACCENT, fg=BTN_TXT,
            font=("Segoe UI", 9), anchor="w", padx=10
        )
        bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ── helpers ─────────────────────────────────────────────────────────────

    def _set_status(self, msg):
        self.status_var.set(msg)

    def _clear_fields(self):
        for key, var in self.entries.items():
            if key == "type":
                var.set("Jami")
            else:
                var.set("")
        self._set_status("Fields cleared.")

    def _populate_form(self, mosque):
        """Fill the input fields from a Mosque object."""
        self.entries["id"].set(mosque.mosque_id)
        self.entries["name"].set(mosque.name)
        self.entries["type"].set(mosque.mosque_type)
        self.entries["address"].set(mosque.address)
        self.entries["coordinates"].set(mosque.coordinates)
        self.entries["imam"].set(mosque.imam_name)

    def _on_select(self, event):
        """Populate form fields when user clicks a listbox row."""
        selection = self.listbox.curselection()
        if not selection:
            return
        text = self.listbox.get(selection[0])
        # parse the ID from "ID: X  |  ..."
        try:
            mosque_id = int(text.split("|")[0].replace("ID:", "").strip())
            results = self.db.Display()
            for m in results:
                if m.mosque_id == mosque_id:
                    self._populate_form(m)
                    self._set_status(f"Selected: {m.name}")
                    break
        except (ValueError, IndexError):
            pass

    def _refresh_listbox(self, mosques):
        self.listbox.delete(0, tk.END)
        if not mosques:
            self.listbox.insert(tk.END, "  — No records found —")
            return
        for m in mosques:
            self.listbox.insert(tk.END, f"  {m}")

    # ── core operations ─────────────────────────────────────────────────────

    def _display_all(self):
        mosques = self.db.Display()
        self._refresh_listbox(mosques)
        self._set_status(f"Displaying all {len(mosques)} mosque(s).")

    def _search(self):
        name = self.entries["name"].get().strip()
        if not name:
            messagebox.showwarning("Missing Input", "Please enter a mosque name to search.")
            return

        # exact / substring match first
        results = self.db.SearchAll(name)

        if results:
            self._refresh_listbox(results)
            if len(results) == 1:
                self._populate_form(results[0])
            self._set_status(f"Found {len(results)} match(es) for '{name}'.")
        else:
            # fuzzy fallback using difflib
            all_names = self.db.GetAllNames()
            close = difflib.get_close_matches(name, all_names, n=5, cutoff=0.4)

            if close:
                self._show_fuzzy_dialog(name, close)
            else:
                messagebox.showinfo(
                    "Not Found",
                    f"No mosque named '{name}' was found, and no similar names exist in the database."
                )
                self._set_status(f"No results for '{name}'.")

    def _show_fuzzy_dialog(self, original, suggestions):
        """Let the user pick from fuzzy-matched name suggestions."""
        dialog = tk.Toplevel(self)
        dialog.title("Did you mean…?")
        dialog.configure(bg=BG_MAIN)
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=f"No exact match for  \"{original}\".\nDid you mean one of these?",
            bg=BG_MAIN, fg="#333", font=("Segoe UI", 10), justify="left", pady=8
        ).pack(padx=20, pady=(14, 4))

        chosen = tk.StringVar()

        for name in suggestions:
            rb = tk.Radiobutton(
                dialog, text=name, variable=chosen, value=name,
                bg=BG_MAIN, font=("Segoe UI", 10), activebackground=BG_MAIN
            )
            rb.pack(anchor="w", padx=30, pady=2)

        chosen.set(suggestions[0])

        def confirm():
            selected = chosen.get()
            dialog.destroy()
            results = self.db.SearchAll(selected)
            self._refresh_listbox(results)
            if results:
                self._populate_form(results[0])
            self._set_status(f"Showing results for '{selected}' (fuzzy match).")

        btn_frame = tk.Frame(dialog, bg=BG_MAIN)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Search", command=confirm,
                  bg=ACCENT, fg=BTN_TXT, font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                  bg="#757575", fg=BTN_TXT, font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=6)

    def _add_entry(self):
        try:
            mosque_id = int(self.entries["id"].get().strip())
        except ValueError:
            messagebox.showerror("Invalid ID", "ID must be a whole number (e.g. 101).")
            return

        name        = self.entries["name"].get().strip()
        mosque_type = self.entries["type"].get().strip()
        address     = self.entries["address"].get().strip()
        coordinates = self.entries["coordinates"].get().strip()
        imam_name   = self.entries["imam"].get().strip()

        if not name:
            messagebox.showerror("Missing Name", "The mosque must have a name.")
            return

        try:
            self.db.Insert(mosque_id, name, mosque_type, address, coordinates, imam_name)
            self._set_status(f"✓ '{name}' added successfully (ID {mosque_id}).")
            self._display_all()
            self._clear_fields()
        except Exception as e:
            if "UNIQUE" in str(e) or "PRIMARY KEY" in str(e):
                messagebox.showerror("Duplicate ID", f"A mosque with ID {mosque_id} already exists.")
            else:
                messagebox.showerror("Database Error", str(e))

    def _delete_entry(self):
        try:
            mosque_id = int(self.entries["id"].get().strip())
        except ValueError:
            messagebox.showerror("Invalid ID", "Please enter a valid numeric ID to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete mosque ID {mosque_id}?\nThis cannot be undone."
        )
        if not confirm:
            return

        if self.db.Delete(mosque_id):
            self._set_status(f"✓ Mosque ID {mosque_id} deleted.")
            self._clear_fields()
            self._display_all()
        else:
            messagebox.showwarning("Not Found", f"No mosque with ID {mosque_id} exists in the database.")

    # ── extra features ──────────────────────────────────────────────────────

    def _update_imam(self):
        """Update the Imam name of a mosque after the user searches for it."""
        try:
            mosque_id = int(self.entries["id"].get().strip())
        except ValueError:
            messagebox.showerror(
                "No Mosque Selected",
                "Please search for a mosque first (the form will fill in its details), then click Update Imam."
            )
            return

        current_imam = self.entries["imam"].get().strip()
        new_imam = simpledialog.askstring(
            "Update Imam Name",
            f"Enter the new Imam name for mosque ID {mosque_id}:",
            initialvalue=current_imam,
            parent=self
        )

        if new_imam is None:
            return  # user cancelled
        new_imam = new_imam.strip()
        if not new_imam:
            messagebox.showerror("Empty Name", "Imam name cannot be empty.")
            return

        if self.db.Update(mosque_id, new_imam):
            self.entries["imam"].set(new_imam)
            self._set_status(f"✓ Imam for mosque ID {mosque_id} updated to '{new_imam}'.")
            self._display_all()
        else:
            messagebox.showwarning("Not Found", f"No mosque with ID {mosque_id} was found.")

    def _display_map(self):
        """Show the mosque's location on an interactive map using folium."""
        coords_str = self.entries["coordinates"].get().strip()
        name       = self.entries["name"].get().strip() or "Mosque"

        if not coords_str:
            messagebox.showwarning(
                "No Coordinates",
                "Please search for a mosque first so its coordinates are loaded into the form."
            )
            return

        # accept "lat,lon" or "lat lon" or "(lat, lon)"
        coords_str = coords_str.replace("(", "").replace(")", "").replace(",", " ")
        parts = coords_str.split()
        if len(parts) != 2:
            messagebox.showerror(
                "Invalid Coordinates",
                f"Expected 'latitude, longitude' (e.g. 21.3891, 39.8579), got: {coords_str}"
            )
            return

        try:
            lat, lon = float(parts[0]), float(parts[1])
        except ValueError:
            messagebox.showerror("Invalid Coordinates", "Coordinates must be numeric decimal values.")
            return

        # build folium map
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="OpenStreetMap")
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(
                f"<b>{name}</b><br>Type: {self.entries['type'].get()}<br>"
                f"Address: {self.entries['address'].get()}<br>"
                f"Imam: {self.entries['imam'].get()}",
                max_width=250
            ),
            tooltip=name,
            icon=folium.Icon(color="green", icon="star")
        ).add_to(m)

        # save to temp file and open in browser
        tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        m.save(tmp.name)
        webbrowser.open(f"file://{tmp.name}")
        self._set_status(f"🗺  Map opened for '{name}' ({lat}, {lon}).")

    # ── demo data (pre-load a few mosques so the app isn't empty) ───────────

    def _seed_demo_data(self):
        if self.db.Display():
            return  # already has data

        sample = [
            (1, "Al-Haram Mosque",     "Grand Mosque",   "Mecca, Saudi Arabia",       "21.4225, 39.8262",  "Sheikh Abdulrahman Al-Sudais"),
            (2, "Al-Masjid an-Nabawi", "Grand Mosque",   "Medina, Saudi Arabia",      "24.4672, 39.6112",  "Sheikh Ali Al-Hudhaify"),
            (3, "Al-Aqsa Mosque",      "Historical",     "Jerusalem, Palestine",      "31.7781, 35.2354",  "Sheikh Muhammad Hussein"),
            (4, "Sultan Ahmed Mosque", "Historical",     "Istanbul, Turkey",          "41.0054, 28.9768",  "Sheikh Mustafa Cagrici"),
            (5, "Istiqlal Mosque",     "Jami",           "Jakarta, Indonesia",        "-6.1702, 106.8330", "Sheikh Nasaruddin Umar"),
        ]
        for row in sample:
            self.db.Insert(*row)


# ── entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MosquesApp()
    app.mainloop()
