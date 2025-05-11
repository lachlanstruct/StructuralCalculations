# %%
# @title 📦 Imports and Setup
import os
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output

# @title 📁 Set Library Directory and List CSVs
# Define the folder containing section CSVs
library_folder = "SteelLibrary/Members/Main"

# List all relevant CSV files
csv_files = [f for f in os.listdir(library_folder) if f.endswith(".csv")]
section_types = sorted(set(f[:3] for f in csv_files))  # e.g., "PFC", "UB", "RHS"


# %% [markdown]
# ## Define Dropdown Widgets

# %%

# @title 🔽 Define Dropdown Widgets
section_type_dropdown = widgets.Dropdown(
    options=section_types,
    description="Section Type:",
    layout=widgets.Layout(width="300px")
)

series_dropdown = widgets.Dropdown(
    options=[],
    description="Series:",
    layout=widgets.Layout(width="300px")
)

member_dropdown = widgets.Dropdown(
    options=[],
    description="Member:",
    layout=widgets.Layout(width="400px")
)

output = widgets.Output()

# @title 🧠 Global Data and Event Handlers
current_df = pd.DataFrame()

# Update Series dropdown
def update_series(change):
    section_type = change['new']
    series = sorted([f.replace(".csv", "") for f in csv_files if f.startswith(section_type)])
    series_dropdown.options = series
    member_dropdown.options = []
    output.clear_output()

# Update Member dropdown
def update_member_list(change):
    global current_df
    series_file = f"{change['new']}.csv"
    full_path = os.path.join(library_folder, series_file)
    try:
        df = pd.read_csv(full_path, skiprows=[1])  # Skip unit row
        current_df = df
        members = df["Description"].dropna().tolist()
        member_dropdown.options = members
    except Exception as e:
        current_df = pd.DataFrame()
        member_dropdown.options = []
        with output:
            print(f"❌ Error reading {series_file}: {e}")

# Display selected member properties
def display_properties(change):
    output.clear_output()
    member = change['new']
    if current_df.empty or member not in current_df["Description"].values:
        return
    row = current_df[current_df["Description"] == member].iloc[0]

    # Extract grade from description, fallback to Unknown
    grade = member.split("(GR")[-1].replace(")", "") if "(GR" in member else "Unknown"
    mat_type = row.get("Type", "Unknown")

    # Basic grade-to-modulus map
    E_lookup = {"350": 200000, "300": 200000, "250": 200000}
    E = E_lookup.get(grade, "Unknown")

    Ix = row.get("Ix", "N/A")

    with output:
        print(f"✅ Selected: {member}\n")
        print(f"🟦 Grade: {grade}")
        print(f"🔩 Material Type: {mat_type}")
        print(f"📐 Young's Modulus (E): {E} MPa")
        print(f"📘 Moment of Inertia (Ix): {Ix} ×10⁶ mm⁴")

# @title 🔗 Connect Events and Display UI
section_type_dropdown.observe(update_series, names="value")
series_dropdown.observe(update_member_list, names="value")
member_dropdown.observe(display_properties, names="value")

ui = widgets.VBox([
    section_type_dropdown,
    series_dropdown,
    member_dropdown,
    output
])
display(ui)

# Trigger first update
update_series({'new': section_type_dropdown.value})



