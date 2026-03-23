import streamlit as st
import pandas as pd

st.set_page_config(page_title="SPMT-AI Tool", layout="wide")

# ===== SAFE DIVISION =====
def safe_div(num, den):
    return num / den if abs(den) > 1e-6 else 0

# ===== PCI FUNCTIONS =====
def pci_cracking(x):
    return safe_div(-0.5662*x**3 + 85.14*x**2 - 3377*x + 51820,
                    x**2 - 29.31*x + 523.4)

def pci_ravelling(x):
    return safe_div(-0.5662*x**3 + 85.14*x**2 - 3377*x + 51820,
                    x**2 - 29.31*x + 523.4)

def pci_pothole(x):
    return (0.1204*x**3 - 1.5385*x**2 - 6.519*x + 99.231)

def pci_patching(x):
    return safe_div(-1.723e-5*x - 0.0073*x**2 + 21.39*x + 419.1,
                    x + 4.267)

def pci_rutting(x):
    return safe_div(-0.5662*x**3 + 85.14*x**2 - 3377*x + 51820,
                    x**2 - 29.31*x + 523.4)

def pci_roughness(x):
    return safe_div(25.16*x + 48.45,
                    x**2 - 5.079*x + 7.595)

def get_level(sev, ext):
    sev = "low" if sev <= 3 else "moderate" if sev <= 6 else "high"
    ext = "low" if ext <= 9 else "moderate" if ext <= 24 else "high"
    return "high" if "high" in (sev, ext) else "moderate" if "moderate" in (sev, ext) else "low"

# ===== TITLE =====
st.title("🛣️ Pavement Assessment Dashboard")

# ===== PCI INPUT =====
st.header("📊 PCI Inputs")

col1, col2, col3 = st.columns(3)

with col1:
    CE = st.number_input("Cracking %", min_value=0.0)
    RE = st.number_input("Ravelling %", min_value=0.0)

with col2:
    PN = st.number_input("Potholes", min_value=0.0)
    PE = st.number_input("Patching %", min_value=0.0)

with col3:
    RD = st.number_input("Rut Depth", min_value=0.0)
    IRI = st.number_input("IRI", min_value=0.0)

# ===== CALCULATE PCI =====
if st.button("Calculate PCI"):

    pc_values = {
        "Cracking": pci_cracking(CE),
        "Ravelling": pci_ravelling(RE),
        "Potholes": pci_pothole(PN),
        "Patching": pci_patching(PE),
        "Rutting": pci_rutting(RD),
        "IRI": pci_roughness(IRI)
    }

    PCI = (pc_values["Cracking"]*0.12 +
           pc_values["Ravelling"]*0.10 +
           pc_values["Potholes"]*0.16 +
           pc_values["Patching"]*0.08 +
           pc_values["Rutting"]*0.14 +
           pc_values["IRI"]*0.4)

    st.session_state.PCI = PCI
    st.session_state.pc_values = pc_values

# ===== DISPLAY PCI =====
if "PCI" in st.session_state:

    PCI = st.session_state.PCI
    pc_values = st.session_state.pc_values

    st.subheader("📈 PCI Result")

    colA, colB = st.columns([1,2])

    with colA:
        st.metric("PCI Score", f"{PCI:.2f}")

        if PCI >= 85:
            condition, action = "Excellent", "Do Nothing"
        elif PCI >= 70:
            condition, action = "Good", "Preventive Maintenance"
        elif PCI >= 55:
            condition, action = "Fair", "Minor Rehabilitation"
        elif PCI >= 40:
            condition, action = "Poor", "Major Maintenance"
        else:
            condition, action = "Very Poor", "Reconstruction"

        st.info(f"{condition} — {action}")

    with colB:
        df = pd.DataFrame({
            "Component": list(pc_values.keys()),
            "PCI Value": list(pc_values.values())
        })
        st.bar_chart(df.set_index("Component"))

# ===== DISTRESS =====
if "PCI" in st.session_state and st.session_state.PCI < 85:

    st.header("🛠️ Distress Evaluation")

    fog = chip = micro = slurry = thmo = 0

    col1, col2 = st.columns(2)

    # ===== CRACKS =====
    with col1:
        cracks = st.checkbox("Cracks")

        if cracks:
            c_val = st.number_input("Severity", key="c1")
            c_unit = st.selectbox("Unit", ["mm", "cm"], key="c1u")
            c_ext = st.number_input("Extent (%)", key="c2")

            if c_unit == "cm":
                c_val *= 10

            lvl = get_level(c_val, c_ext)

            if lvl == "low":
                fog += 1; micro += 1
            elif lvl == "moderate":
                chip += 1; slurry += 1
            else:
                thmo += 1

    # ===== ALLIGATOR =====
    with col1:
        alligator = st.checkbox("Alligator Cracking")

        if alligator:
            a_val = st.number_input("Severity", key="a1")
            a_unit = st.selectbox("Unit", ["mm", "cm"], key="a1u")
            a_ext = st.number_input("Extent (%)", key="a2")

            if a_unit == "cm":
                a_val *= 10

            lvl = get_level(a_val, a_ext)

            if lvl == "low":
                fog += 1; micro += 1
            elif lvl == "moderate":
                chip += 1; slurry += 1; micro += 1
            else:
                thmo += 2

    # ===== STRIPING =====
    with col2:
        strip_val = st.number_input("Striping Value")
        strip_unit = st.selectbox("Unit", ["%", "fraction"])

        if strip_unit == "fraction":
            strip_val *= 100

        if strip_val > 0:
            if strip_val < 25:
                fog += 1
            else:
                chip += 1

    # ===== RUTTING =====
    with col2:
        rut_val = st.number_input("Rutting Depth")
        rut_unit = st.selectbox("Unit", ["mm", "cm"])

        if rut_unit == "cm":
            rut_val *= 10

        if rut_val > 0:
            if rut_val < 20:
                micro += 1
            else:
                thmo += 1

    # ===== OTHER DISTRESSES =====
    st.subheader("Other Distresses")

    col3, col4 = st.columns(2)

    with col3:
        if st.checkbox("Bleeding"):
            fog += 1
        if st.checkbox("Corrugation"):
            chip += 1
        if st.checkbox("Block Cracking"):
            chip += 1

    with col4:
        if st.checkbox("Hungry Surface"):
            slurry += 1
        if st.checkbox("Polished Aggregates"):
            slurry += 1

    # ===== EVALUATE =====
    if st.button("Evaluate Distress"):

        treatments = {
            "Fog Seal": fog + 0.218,
            "Slurry Seal": slurry + 0.178,
            "Micro Surfacing": micro + 0.191,
            "Chip Seal": chip + 0.181,
            "Thin Hot Mix Overlay": thmo + 0.200
        }

        best = max(treatments, key=treatments.get)
        score = treatments[best]

        st.subheader("📋 Results")

        st.write(f"Fog Seal: {fog}")
        st.write(f"Chip Seal: {chip}")
        st.write(f"Micro Surfacing: {micro}")
        st.write(f"Slurry Seal: {slurry}")
        st.write(f"Thin Hot Mix Overlay: {thmo}")

        df = pd.DataFrame({
            "Treatment": list(treatments.keys()),
            "Score": list(treatments.values())
        })

        st.bar_chart(df.set_index("Treatment"))

        st.success(f"Recommended Treatment: {best} (Score: {score:.3f})")

        # ===== DESCRIPTION =====
        if best == "Fog Seal":
            st.write("Fog seal for surface rejuvenation")
        elif best == "Chip Seal":
            st.write("Chip seal recommended")
        elif best == "Micro Surfacing":
            st.write("Microsurfacing with thickness of 4–6 mm")
        elif best == "Slurry Seal":
            st.write("Slurry seal recommended")
        elif best == "Thin Hot Mix Overlay":
            st.write("Overlay thickness 20–30 mm")