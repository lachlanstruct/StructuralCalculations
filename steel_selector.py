import os
import pandas as pd
import ipywidgets as widgets
from IPython.display import display

class SteelSelector:
    def __init__(self, library_folder="SteelLibrary/Members/Main", display_geom_props=None):
        self.library_folder = library_folder
        self.csv_files = [f for f in os.listdir(library_folder) if f.endswith(".csv")]
        self.section_types = sorted(set(f[:3] for f in self.csv_files))
        self.section_props = {}
        self.display_geom_props = display_geom_props or []

        # Auto-definition settings
        self.auto_define_props = []         # List of keys to auto-define as variables
        self.auto_define_suffix = ""        # Suffix to append (e.g., '1' for Ix1)

        # Widgets
        self.section_type_dropdown = widgets.Dropdown(
            options=self.section_types, description="Section Type:", layout=widgets.Layout(width="250px")
        )
        self.series_dropdown = widgets.Dropdown(options=[], description="Series:", layout=widgets.Layout(width="250px"))
        self.member_dropdown = widgets.Dropdown(options=[], description="Member:", layout=widgets.Layout(width="350px"))
        self.material_output = widgets.Output()
        self.geometry_output = widgets.Output()
        self.current_df = pd.DataFrame()

        # Event bindings
        self.section_type_dropdown.observe(self.update_series, names="value")
        self.series_dropdown.observe(self.update_member_list, names="value")
        self.member_dropdown.observe(self.display_properties, names="value")

        # UI container
        self.selector_ui = widgets.VBox([
            self.section_type_dropdown,
            self.series_dropdown,
            self.member_dropdown,
            widgets.HTML("<b>Material Properties</b>"),
            self.material_output,
            widgets.HTML("<b>Geometric Properties</b>"),
            self.geometry_output
        ])

    def get_grade_from_series(self, series_name):
        try:
            return int(''.join(filter(str.isdigit, series_name))) * 10
        except:
            return "Unknown"

    def update_series(self, change):
        section_type = change['new']
        options = sorted([f.replace(".csv", "") for f in self.csv_files if f.startswith(section_type)])
        self.series_dropdown.options = options
        self.member_dropdown.options = []
        self.material_output.clear_output()

    def update_member_list(self, change):
        full_path = os.path.join(self.library_folder, f"{change['new']}.csv")
        try:
            df = pd.read_csv(full_path, skiprows=[1])
            self.current_df = df
            self.member_dropdown.options = df["Description"].dropna().tolist()
        except Exception as e:
            self.current_df = pd.DataFrame()
            self.member_dropdown.options = []
            with self.material_output:
                print(f"❌ Error reading file: {e}")

    def display_properties(self, change):
        self.material_output.clear_output()
        member = change['new']

        if self.current_df.empty or member not in self.current_df["Description"].values:
            return

        row = self.current_df[self.current_df["Description"] == member].iloc[0]
        series = self.series_dropdown.value
        grade = self.get_grade_from_series(series)
        E = 200_000

        self.section_props.clear()
        self.section_props['E'] = E * 1e6
        print(f"✅ Selected: {member}")
        print(f"🟦 Grade: {grade}")
        print(f"📐 E: {E} MPa")

        if self.display_geom_props:
            filtered = row[self.display_geom_props].to_frame(name='Value')
            with self.geometry_output:
                display(filtered)

        # ✅ Correctly scaled values
        scaling = {
            "Ix": 1e6, "Zx": 1e3, "Sx": 1e3, "Iy": 1e6,
            "Zy": 1e3, "Sy": 1e3, "J": 1e3, "Iw": 1e9,
            "Zex": 1e3, "Zey": 1e3
        }

        # Build scaled section_props
        for col in row.index:
            val = row[col]
            if pd.notna(val) and (
                isinstance(val, (int, float)) or 
                (isinstance(val, str) and val.replace('.', '', 1).isdigit())
            ):
                try:
                    scaled = float(val) * scaling.get(col, 1)
                    self.section_props[col] = scaled
                except:
                    self.section_props[col] = None

        # ✅ Define globals after selection
        if self.auto_define_props:
            for key in self.auto_define_props:
                val = self.section_props.get(key)
                if val is not None:
                    varname = f"{key}{self.auto_define_suffix or ''}"
                    globals()[varname] = val
                    print(f"📌 {varname} = {val:.3g}")
                else:
                    print(f"⚠️ {key} not available or not numeric")


    def launch(self):
        display(self.selector_ui)
        self.update_series({'new': self.section_type_dropdown.value})

    def get_properties(self, keys=None):
        """Return selected section properties, optionally filtered by key list."""
        if keys is None:
            return self.section_props.copy()
        return {k: self.section_props.get(k) for k in keys}

    def define_properties(self, name_suffix="", props=None, display=True):
        """
        Defines variables like Ix1, Zx1, etc. using the selected section's properties.
        Arguments:
            name_suffix: string to append (e.g., '1' → Ix1)
            props: list of properties to extract
            display: whether to print the values with units
        Returns:
            Dictionary {variable_name: value}
        """
        if not self.section_props:
            raise ValueError("No section selected yet. Please choose a member first.")

        scaling = {
            "Ix": 1e6, "Zx": 1e3, "Sx": 1e3, "Iy": 1e6,
            "Zy": 1e3, "Sy": 1e3, "J": 1e3, "Iw": 1e9,
            "Zex": 1e3, "Zey": 1e3
        }

        results = {}
        for key in props or []:
            raw_val = self.section_props.get(key)
            if raw_val is None:
                print(f"❌ {key} not found.")
                continue
            scaled_val = raw_val * scaling.get(key, 1)
            varname = f"{key}{name_suffix}"
            globals()[varname] = scaled_val
            results[varname] = scaled_val
            if display:
                print(f"📌 {varname} = {scaled_val:.3g} ({'scaled' if key in scaling else 'raw'})")
        return results
