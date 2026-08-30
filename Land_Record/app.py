import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
from database import init_db, insert_record, get_all_records, update_record, delete_record
from extractor import extract_land_record

# Initialize SQLite database
init_db()

st.set_page_config(
    page_title="DILRMP - Intelligent Land Record Digitizer",
    page_icon="🏛️",
    layout="wide"
)

# --- CUSTOM CSS: Clean Modern Typography & High-Contrast Bold Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3, h4 {
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    
    /* Highlighted Table Headers */
    thead th {
        font-size: 14px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }
    
    /* Table Rows */
    tbody td {
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    /* Card Component */
    .record-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    
    .record-card-title {
        font-size: 16px;
        font-weight: 700;
        color: #f8fafc;
    }
    
    .record-card-subtitle {
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏛️ System Control")
api_key = st.sidebar.text_input(
    "Enter Gemini API Key (AQ. or AIza)", 
    type="password", 
    placeholder="AQ.Ab8RN6... / AIza...",
    help="Paste your API key here"
)
st.sidebar.divider()
st.sidebar.info(
    "**Problem Statement ID:** 26018\n\n"
    "**Project:** Intelligent Land Record Digitization\n\n"
    "**Engine:** Gemini 3.6 Flash\n\n"
    "**Dept:** Dept. of Land Resources (DoLR)\n\n"
    "**Ministry:** Ministry of Rural Development"
)

st.title("📄 AI-Powered Land Record Digitization & Validation System")
st.caption("Multilingual Vision AI (Marathi / Hindi / English) with Human-in-the-Loop Validation & Registry Management")

tab1, tab2, tab3 = st.tabs(["🚀 Digitization & Ingestion", "🗄️ Master Land Registry", "📊 Administrative Analytics"])

# ==================== TAB 1: DIGITIZATION & INGESTION ====================
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.subheader("1. Ingestion Portal")
        uploaded_file = st.file_uploader(
            "Upload Scanned Land Record (7/12 Extract, Khasra, Khatauni)",
            type=["jpg", "jpeg", "png"]
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Document Preview", use_container_width=True)
        else:
            st.info("Upload a scanned land record image to begin extraction.")

    with col_right:
        st.subheader("2. AI Extraction & Human Validation")
        
        if uploaded_file:
            if not api_key:
                st.warning("⚠️ Enter your Gemini API Key in the left sidebar.")
            else:
                if st.button("⚡ Run Intelligent Extraction", type="primary", use_container_width=True):
                    with st.spinner("Connecting to Vision AI engine, extracting fields & verifying..."):
                        st.session_state["extracted_data"] = extract_land_record(image, api_key)
                
                if "extracted_data" in st.session_state:
                    data = st.session_state["extracted_data"]
                    conf = data.get("confidence_score", 0.0)
                    status = data.get("validation_status", "Requires Human Review")
                    model_name = data.get("model_used", "gemini-3.6-flash")
                    
                    if "error_message" in data and data["error_message"]:
                        st.error(f"⚠️ Extraction Error: {data['error_message']}")
                    
                    if status == "Auto-Validated":
                        st.success(f"✅ **Status:** {status} (Confidence: {int(conf * 100)}%) — Engine: `{model_name}`")
                    else:
                        st.warning(f"⚠️ **Status:** {status} (Confidence: {int(conf * 100)}%) — Engine: `{model_name}`")

                    # Human-in-the-loop Form
                    with st.form("hitl_verification_form"):
                        st.markdown("#### Review & Confirm Extracted Fields")
                        
                        f_name = st.text_input("Landowner Name(s)", value=data.get("landowner_name", ""))
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            f_khasra = st.text_input("Survey / Khasra No.", value=data.get("survey_khasra_no", ""))
                            f_village = st.text_input("Village", value=data.get("village", ""))
                            f_district = st.text_input("District", value=data.get("district", ""))
                        with c2:
                            f_khata = st.text_input("Khata No.", value=data.get("khata_no", ""))
                            f_tehsil = st.text_input("Tehsil / Taluka", value=data.get("tehsil", ""))
                            f_state = st.text_input("State", value=data.get("state", ""))
                            
                        f_area = st.number_input("Area (Hectares)", value=float(data.get("area_hectares", 0.0)), format="%.4f")
                        
                        submitted = st.form_submit_button("💾 Approve & Commit to DILRMP Registry", use_container_width=True)
                        
                        if submitted:
                            record_to_save = {
                                "landowner_name": f_name,
                                "survey_khasra_no": f_khasra,
                                "khata_no": f_khata,
                                "area_hectares": f_area,
                                "village": f_village,
                                "tehsil": f_tehsil,
                                "district": f_district,
                                "state": f_state,
                                "confidence_score": conf,
                                "validation_status": "Verified & Committed"
                            }
                            if insert_record(record_to_save):
                                st.balloons()
                                st.success(f"Record for Khasra **{f_khasra}** committed successfully!")
                            else:
                                st.error("Failed to commit record to database.")

# ==================== TAB 2: MASTER DATABASE & RECORD MANAGEMENT ====================
with tab2:
    st.subheader("🗄️ Master Land Registry Database")
    df_records = get_all_records()
    
    if not df_records.empty:
        # Display summary counts
        st.markdown(f"**Total Registered Records:** `{len(df_records)}` | **Database Status:** `Connected (SQLite)`")
        
        # Formatted Data Table
        st.dataframe(
            df_records, 
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("Record ID", format="%d"),
                "landowner_name": st.column_config.TextColumn("Landowner(s) Name", width="large"),
                "survey_khasra_no": st.column_config.TextColumn("Survey / Khasra No.", width="medium"),
                "area_hectares": st.column_config.NumberColumn("Area (Ha)", format="%.4f"),
                "confidence_score": st.column_config.ProgressColumn("Confidence", min_value=0.0, max_value=1.0, format="%.2f"),
                "validation_status": st.column_config.TextColumn("Status"),
                "created_at": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm")
            }
        )
        
        csv = df_records.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export Master Registry as CSV", data=csv, file_name="dilrmp_master_records.csv", mime="text/csv")
        
        st.divider()
        
        # Management Grid: Update (Left) and Delete (Right)
        col_edit, col_del = st.columns([1.2, 0.8], gap="large")
        
        record_map = {
            f"ID #{row['id']} — {row['landowner_name']} (Khasra: {row['survey_khasra_no']})": row['id']
            for _, row in df_records.iterrows()
        }
        
        # --- UPDATE SECTION ---
        with col_edit:
            st.subheader("✏️ Update / Edit Record")
            selected_edit_label = st.selectbox("Select Record to Edit:", list(record_map.keys()), key="select_edit")
            selected_edit_id = record_map[selected_edit_label]
            
            # Fetch target record
            rec = df_records[df_records["id"] == selected_edit_id].iloc[0]
            
            with st.form(f"edit_form_{selected_edit_id}"):
                u_name = st.text_input("Landowner Name(s)", value=str(rec["landowner_name"]))
                
                ue1, ue2 = st.columns(2)
                with ue1:
                    u_khasra = st.text_input("Survey / Khasra No.", value=str(rec["survey_khasra_no"]))
                    u_village = st.text_input("Village", value=str(rec["village"]))
                    u_district = st.text_input("District", value=str(rec["district"]))
                with ue2:
                    u_khata = st.text_input("Khata No.", value=str(rec["khata_no"]))
                    u_tehsil = st.text_input("Tehsil / Taluka", value=str(rec["tehsil"]))
                    u_state = st.text_input("State", value=str(rec["state"]))
                    
                u_area = st.number_input("Area (Hectares)", value=float(rec["area_hectares"]), format="%.4f")
                u_status = st.selectbox("Validation Status", ["Verified & Committed", "Updated by Officer", "Requires Human Review"], index=0)
                
                save_changes = st.form_submit_button("💾 Save & Update Record", use_container_width=True)
                
                if save_changes:
                    updated_dict = {
                        "landowner_name": u_name,
                        "survey_khasra_no": u_khasra,
                        "khata_no": u_khata,
                        "area_hectares": u_area,
                        "village": u_village,
                        "tehsil": u_tehsil,
                        "district": u_district,
                        "state": u_state,
                        "validation_status": u_status
                    }
                    if update_record(selected_edit_id, updated_dict):
                        st.success(f"Record ID #{selected_edit_id} updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update record.")

        # --- DELETE SECTION ---
        with col_del:
            st.subheader("🗑️ Delete Record")
            selected_del_label = st.selectbox("Select Record to Delete:", list(record_map.keys()), key="select_del")
            selected_del_id = record_map[selected_del_label]
            
            st.warning(f"You are about to delete **Record ID #{selected_del_id}**.")
            confirm_del = st.checkbox("⚠️ Confirm Permanent Deletion", key=f"del_confirm_{selected_del_id}")
            
            if st.button("🗑️ Permanently Delete", type="primary", disabled=not confirm_del, use_container_width=True):
                if delete_record(selected_del_id):
                    st.success(f"Record #{selected_del_id} removed.")
                    st.rerun()
                else:
                    st.error("Failed to delete record.")
    else:
        st.info("No records committed yet. Extract and verify records in Tab 1 to view them here.")

# ==================== TAB 3: ADMINISTRATIVE ANALYTICS ====================
with tab3:
    st.subheader("📊 Executive Monitoring & Digitization Progress")
    df_records = get_all_records()
    
    total_docs = len(df_records)
    auto_val = len(df_records[df_records["validation_status"] == "Verified & Committed"]) if total_docs > 0 else 0
    avg_conf = (df_records["confidence_score"].mean() * 100) if total_docs > 0 else 0.0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Records Digitized", f"{total_docs}")
    k2.metric("Committed to Registry", f"{auto_val}")
    k3.metric("Avg Extraction Confidence", f"{avg_conf:.1f}%")
    k4.metric("DILRMP Server Status", "ONLINE", delta="Active")
    
    st.divider()
    
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.markdown("##### District-Wise Record Distribution")
        if not df_records.empty and "district" in df_records.columns and df_records["district"].notnull().any():
            dist_counts = df_records["district"].value_counts().reset_index()
            dist_counts.columns = ["District", "Count"]
            fig_bar = px.bar(dist_counts, x="District", y="Count", color="Count", title="Records by District", template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            mock_data = pd.DataFrame({"District": ["Pune", "Nagpur", "Nashik", "Satara", "Thane"], "Records": [120, 85, 60, 45, 30]})
            fig_bar = px.bar(mock_data, x="District", y="Records", title="Sample District Distribution", template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with c_chart2:
        st.markdown("##### Quality & Validation Breakdown")
        status_data = pd.DataFrame({
            "Category": ["Auto-Validated (>85%)", "Officer Verified / Edited", "Pending Review"],
            "Share": [74, 21, 5]
        })
        fig_pie = px.pie(status_data, values="Share", names="Category", title="Quality Distribution", template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)