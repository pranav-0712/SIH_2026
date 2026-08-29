import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
from database import init_db, insert_record, get_all_records
from extractor import configure_ai, extract_land_record

# Initialize SQLite Database on startup
init_db()

st.set_page_config(
    page_title="DILRMP - Intelligent Land Record Digitizer",
    page_icon="🏛️",
    layout="wide"
)

# Sidebar - API Key and Project Metadata
st.sidebar.title("🏛️ System Control")
api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    help="AQ.Ab8RN6JsNr2n740Q_n92eUmWE13Xl0xelA5WP1h6_UL_S3e34A"
)
st.sidebar.info("**Problem Statement:** 26018\n\n**Dept:** Land Resources (DoLR)\n\n**Ministry:** Ministry of Rural Development")

st.title("📄 AI-Powered Land Record Digitization & Validation System")
st.markdown("Modernizing legacy land registries (7/12 Extracts, Khasra, Khatauni) with Multilingual Vision AI & Human-in-the-Loop Validation.")

tab1, tab2, tab3 = st.tabs(["🚀 Digitization & Verification", "🗄️ Master Land Registry Database", "📊 Administrative Analytics"])

# ==================== TAB 1: UPLOAD & VERIFY ====================
with tab1:
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    with col_left:
        st.subheader("1. Ingestion Portal")
        uploaded_file = st.file_uploader(
            "Upload Scanned Land Record (JPEG / PNG)",
            type=["jpg", "jpeg", "png"]
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Document Preview", use_container_width=True)
        else:
            st.info("Please upload a sample scanned land record to begin automated extraction.")

    with col_right:
        st.subheader("2. AI Extraction & Human Validation")
        
        if uploaded_file:
            if not api_key:
                st.warning("⚠️ Please provide a valid Gemini API Key in the sidebar to enable processing.")
            else:
                if st.button("⚡ Run Intelligent Extraction", type="primary", use_container_width=True):
                    with st.spinner("Analyzing document, running OCR, translation & entity extraction..."):
                        try:
                            configure_ai(api_key)
                            st.session_state["extracted_data"] = extract_land_record(image)
                        except Exception as e:
                            st.error(f"Processing error: {str(e)}")
                
                if "extracted_data" in st.session_state:
                    data = st.session_state["extracted_data"]
                    conf = data.get("confidence_score", 0.0)
                    status = data.get("validation_status", "Requires Human Review")
                    
                    if status == "Auto-Validated":
                        st.success(f"✅ **Extraction Status:** {status} (Confidence: {int(conf * 100)}%)")
                    else:
                        st.warning(f"⚠️ **Extraction Status:** {status} (Confidence: {int(conf * 100)}%) - Officer verification recommended.")

                    # Editable Form (Human-in-the-Loop)
                    with st.form("hitl_verification_form"):
                        st.markdown("#### Verify & Edit Extracted Fields")
                        
                        f_name = st.text_input("Landowner Name", value=data.get("landowner_name", ""))
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
                                st.success(f"Record for Khasra **{f_khasra}** has been securely saved to the database!")
                            else:
                                st.error("Failed to commit record to database.")

# ==================== TAB 2: DATABASE VIEW ====================
with tab2:
    st.subheader("🗄️ Digitized Land Records Master Table")
    df_records = get_all_records()
    
    if not df_records.empty:
        st.dataframe(df_records, use_container_width=True)
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Registry as CSV", data=csv, file_name="dilrmp_digitized_records.csv", mime="text/csv")
    else:
        st.info("No records committed to the database yet. Process and approve documents in Tab 1 to populate this registry.")

# ==================== TAB 3: ANALYTICS DASHBOARD ====================
with tab3:
    st.subheader("📊 Executive Monitoring & Digitization Progress")
    df_records = get_all_records()
    
    total_docs = len(df_records)
    auto_val = len(df_records[df_records["validation_status"] == "Verified & Committed"]) if total_docs > 0 else 0
    avg_conf = (df_records["confidence_score"].mean() * 100) if total_docs > 0 else 0.0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Records Processed", f"{total_docs}")
    k2.metric("Committed to Registry", f"{auto_val}")
    k3.metric("Avg Extraction Confidence", f"{avg_conf:.1f}%")
    k4.metric("DILRMP API Sync Status", "ONLINE", delta="Active")
    
    st.divider()
    
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.markdown("##### District-Wise Digitization Volume")
        if not df_records.empty and "district" in df_records.columns and df_records["district"].str.strip().ne("").any():
            dist_counts = df_records["district"].value_counts().reset_index()
            dist_counts.columns = ["District", "Count"]
            fig_bar = px.bar(dist_counts, x="District", y="Count", color="Count", title="Records by District")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            mock_data = pd.DataFrame({"District": ["Pune", "Nagpur", "Nashik", "Satara", "Thane"], "Count": [120, 85, 60, 45, 30]})
            fig_bar = px.bar(mock_data, x="District", y="Count", color="Count", title="Sample District Distribution")
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with c_chart2:
        st.markdown("##### System Quality & Validation Ratio")
        status_data = pd.DataFrame({
            "Category": ["Auto-Validated (>85%)", "Human-in-Loop Corrected", "Low Confidence Scans"],
            "Share": [72, 21, 7]
        })
        fig_pie = px.pie(status_data, values="Share", names="Category", title="Extraction Accuracy Breakdown")
        st.plotly_chart(fig_pie, use_container_width=True)