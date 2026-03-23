import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import tempfile
from typing import List, Dict, Any
from collections import Counter

from parser import EnhancedResumeParser
from config import create_directories

# Configure page
st.set_page_config(
    page_title="Resume Screening System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'screening_engine' not in st.session_state:
    st.session_state.screening_engine = None
if 'resumes_data' not in st.session_state:
    st.session_state.resumes_data = []
if 'job_descriptions' not in st.session_state:
    st.session_state.job_descriptions = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'chatbot_history' not in st.session_state:
    st.session_state.chatbot_history = []
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "📄 Resume Upload"

def main():
    """Main application function with enhanced structure"""
    # Header
    st.title("SmartHire.AI")
    st.markdown("### **Multi-Resume vs Multi-JD Analysis**")

    # Ensure directories exist
    create_directories()

    # Initialize screening engine
    if st.session_state.screening_engine is None:
        with st.spinner(" Initializing AI system..."):
            try:
                # Direct import - no models package needed
                from models.google_screening_engine import GoogleAIScreeningEngine
                engine = GoogleAIScreeningEngine()

                # Attach parser if missing to avoid NoneType parser errors
                if not hasattr(engine, "parser") or engine.parser is None:
                    engine.parser = EnhancedResumeParser()

                st.session_state.screening_engine = engine
                st.success(" AI system initialized!")
            except Exception as e:
                st.error(f" System initialization failed: {e}")
                st.info(" Check your API key in secrets.toml")
                return

    # Render sidebar navigation and content
    render_sidebar()
    render_main_content()

def render_sidebar():
    """Enhanced sidebar with navigation and system info"""
    # Navigation Menu
    st.sidebar.markdown("#  Navigation")
    
    # Tab options
    tab_options = [
        "Resume Upload",
        "Job Descriptions", 
        "Analysis & Results",
        "AI Chatbot",
        "System Status"
    ]
    
    # Navigation buttons
    for tab in tab_options:
        if st.sidebar.button(tab, key=f"nav_{tab}", use_container_width=True):
            st.session_state.selected_tab = tab
            
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Actions**")
    if st.sidebar.button("Refresh System"):
        st.session_state.screening_engine = None
        st.rerun()
    if st.sidebar.button("Clear All Data"):
        st.session_state.resumes_data = []
        st.session_state.job_descriptions = []
        st.session_state.analysis_results = []
        st.session_state.chatbot_history = []
        st.rerun()
    if st.sidebar.button("Export Results") and st.session_state.analysis_results:
        export_comprehensive_results()
    
    # Quick status
    st.sidebar.markdown("---")
    st.sidebar.markdown("## Model Status")
    if st.session_state.screening_engine:
        try:
            system_status = st.session_state.screening_engine.get_system_status()
            if system_status.get('ready_for_screening', False):
                # st.sidebar.success("AI Ready")
                st.sidebar.success("Ready")
            else:
                st.sidebar.error("AI Issues")
        except Exception as e:
            st.sidebar.error(f"Status Error: {e}")

    # Current session data
    st.sidebar.markdown("---")
    st.sidebar.markdown("## Current Session")
    st.sidebar.metric("Resumes Loaded", len(st.session_state.resumes_data))
    st.sidebar.metric("Job Descriptions", len(st.session_state.job_descriptions))
    st.sidebar.metric("Analyses Complete", len(st.session_state.analysis_results))

def render_main_content():
    """Render main content based on selected navigation tab"""
    
    if st.session_state.selected_tab == "Resume Upload":
        render_resume_upload()
    elif st.session_state.selected_tab == "Job Descriptions":
        render_job_descriptions()
    elif st.session_state.selected_tab == "Analysis & Results":
        render_analysis_results()
    elif st.session_state.selected_tab == "AI Chatbot":
        render_enhanced_chatbot()
    elif st.session_state.selected_tab == "System Status":
        render_system_status()

def render_resume_upload():
    """Enhanced resume upload with better organization"""
    st.header("Resume Upload & Management")

    # System check
    if not st.session_state.screening_engine:
        st.error("System not initialized. Please refresh.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload New Resumes")

        # File uploader
        uploaded_files = st.file_uploader(
            "Select resume files",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'doc', 'txt'],
            help="Upload PDF, Word documents, or text files",
            key="resume_uploader"
        )

        if uploaded_files:
            if st.button("Process & Add Resumes", type="primary"):
                process_and_store_resumes(uploaded_files)

    with col2:
        st.subheader("Current Resume Bank")
        if st.session_state.resumes_data:
            st.success(f"{len(st.session_state.resumes_data)} resumes loaded")

            # Show resume list
            with st.expander("Resume Details", expanded=False):
                for i, resume in enumerate(st.session_state.resumes_data):
                    st.write(f"**{i+1}.** {resume['filename']}")
                    if 'candidate_name' in resume.get('extracted_data', {}):
                        st.write(f"   {resume['extracted_data']['candidate_name']}")
                    if 'total_years_experience' in resume.get('extracted_data', {}):
                        st.write(f"   {resume['extracted_data']['total_years_experience']} years exp")
        else:
            st.info("No resumes loaded yet")

    # Resume management
    if st.session_state.resumes_data:
        st.markdown("---")
        st.subheader("Resume Bank Management")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Preview All Resumes"):
                show_resume_previews()
        with col2:
            if st.button("Resume Statistics"):
                show_resume_statistics()
        with col3:
            if st.button("Clear Resume Bank"):
                st.session_state.resumes_data = []
                st.rerun()

def render_job_descriptions():
    """Enhanced job description management with multiple input methods"""
    st.header("Job Descriptions Management")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Add New Job Description")

        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "PDF Upload", "Text File Upload", "Predefined Templates"],
            horizontal=True,
            key="jd_input_method"
        )

        job_title = st.text_input("Job Title", placeholder="e.g., Senior Data Scientist", key="jd_title_input")

        # Optional M Group metadata (additive UI only)
        mgroup_sector = st.selectbox(
            "M Group sector (optional)",
            ["", "Water", "Energy", "Highways", "Rail & Aviation", "Telecom"],
            key="mgroup_sector"
        )
        mgroup_region = st.selectbox(
            "Primary region (optional)",
            ["", "England", "Scotland", "Wales", "Northern Ireland", "Republic of Ireland"],
            key="mgroup_region"
        )
        mgroup_role_family = st.selectbox(
            "Role family (optional)",
            ["", "Site Engineer", "Construction Manager", "Foreman / Supervisor",
             "Project Manager", "Delivery Manager", "Service Support / Office"],
            key="mgroup_role_family"
        )

        job_description = ""

        if input_method == "Text Input":
            job_description = st.text_area(
                "Job Description",
                height=200,
                placeholder="Paste or type job description here...",
                key="jd_text_input"
            )

        elif input_method == "PDF Upload":
            uploaded_pdf = st.file_uploader("Upload JD PDF", type=['pdf'], key="jd_pdf_uploader")
            if uploaded_pdf:
                try:
                    job_description = extract_text_from_pdf(uploaded_pdf)
                    if job_description:
                        st.success(f"Extracted {len(job_description)} characters from PDF")
                        st.text_area(
                            "Extracted JD Text",
                            value=job_description[:500] + "..." if len(job_description) > 500 else job_description,
                            height=150,
                            disabled=True,
                            key="pdf_preview"
                        )
                    else:
                        st.error("Could not extract text from PDF")
                except Exception as e:
                    st.error(f"PDF processing error: {e}")
                    job_description = ""

        elif input_method == "Text File Upload":
            uploaded_txt = st.file_uploader("Upload JD Text File", type=['txt', 'docx'], key="jd_txt_uploader")
            if uploaded_txt:
                try:
                    job_description = extract_text_from_file(uploaded_txt)
                    if job_description:
                        st.success(f"Extracted {len(job_description)} characters from file")
                        st.text_area(
                            "Extracted JD Text",
                            value=job_description[:500] + "..." if len(job_description) > 500 else job_description,
                            height=150,
                            disabled=True,
                            key="txt_preview"
                        )
                    else:
                        st.error("Could not extract text from file")
                except Exception as e:
                    st.error(f"File processing error: {e}")
                    job_description = ""

        elif input_method == "Predefined Templates":
            try:
                from config import JOB_TEMPLATES
                template_choice = st.selectbox("Select template:", list(JOB_TEMPLATES.keys()), key="template_selector")
                job_description = JOB_TEMPLATES[template_choice]
                st.text_area("Template JD", value=job_description, height=150, disabled=True, key="template_preview")
            except ImportError:
                st.error("Job templates not available. Please use other input methods.")
                job_description = ""

        # Add job description button
        st.markdown("---")
        
        # Add button with validation
        if st.button("Add Job Description", type="primary", key="add_jd_button"):
            if job_title and job_title.strip() and job_description and job_description.strip():
                add_job_description(
                    job_title.strip(),
                    job_description.strip(),
                    input_method,
                    mgroup_sector,
                    mgroup_region,
                    mgroup_role_family
                )
            else:
                if not job_title or not job_title.strip():
                    st.error("Please enter a job title")
                if not job_description or not job_description.strip():
                    st.error("Please provide a job description")

    with col2:
        st.subheader("Current Job Descriptions")
        if st.session_state.job_descriptions:
            st.success(f"{len(st.session_state.job_descriptions)} JDs loaded")

            # Show JD list
            for i, jd in enumerate(st.session_state.job_descriptions):
                with st.expander(f"{i+1}. {jd['title']}", expanded=False):
                    st.write(f"**Method:** {jd['input_method']}")
                    st.write(f"**Length:** {len(jd['description'])} characters")
                    st.write(f"**Added:** {jd.get('created_time', 'Unknown')}")
                    st.write(f"**Preview:** {jd['description'][:150]}...")

                    # Show M Group specific metadata if present
                    m_context_bits = []
                    if jd.get('mgroup_sector'):
                        m_context_bits.append(f"Sector: {jd['mgroup_sector']}")
                    if jd.get('mgroup_region'):
                        m_context_bits.append(f"Region: {jd['mgroup_region']}")
                    if jd.get('mgroup_role_family'):
                        m_context_bits.append(f"Role family: {jd['mgroup_role_family']}")
                    if m_context_bits:
                        st.write("**M Group context:** " + " | ".join(m_context_bits))
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"Edit", key=f"edit_jd_{i}"):
                            edit_job_description(i)
                    with col_b:
                        if st.button(f"Delete", key=f"delete_jd_{i}"):
                            st.session_state.job_descriptions.pop(i)
                            st.success(f"Deleted job description: {jd['title']}")
                            st.rerun()
        else:
            st.info("No job descriptions added yet")

def render_analysis_results():
    """Enhanced analysis and results with multi-resume vs multi-JD comparison and KPI cards"""
    st.header("Multi-Resume vs Multi-JD Analysis")

    # Check prerequisites
    if not st.session_state.resumes_data:
        st.warning("Please upload resumes first")
        return

    if not st.session_state.job_descriptions:
        st.warning("Please add job descriptions first")
        return

    # High-level note on M Group context
    st.info(
        "Scoring and analysis are tuned for M Group Services infrastructure roles "
        "across water, energy, highways, rail & aviation, and telecom in the UK and Ireland."
    )

    # Analysis configuration
    st.subheader("Analysis Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_resumes = st.multiselect(
            "Select Resumes to Analyze",
            options=range(len(st.session_state.resumes_data)),
            default=range(len(st.session_state.resumes_data)),
            format_func=lambda x: f"{st.session_state.resumes_data[x]['filename']}"
        )

    with col2:
        selected_jds = st.multiselect(
            "Select Job Descriptions",
            options=range(len(st.session_state.job_descriptions)),
            default=range(len(st.session_state.job_descriptions)),  # Default to all
            format_func=lambda x: f"{st.session_state.job_descriptions[x]['title']}"
        )

    with col3:
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Quick Scoring", "Detailed Analysis", "Comprehensive Report"]
        )

    # Start analysis
    if st.button("Start Multi-Analysis", type="primary"):
        if selected_resumes and selected_jds:
            run_comprehensive_analysis(selected_resumes, selected_jds, analysis_depth)
        else:
            st.warning("Please select both resumes and job descriptions")

    # Show results with KPI cards
    if st.session_state.analysis_results:
        st.markdown("---")
        render_comprehensive_results()

def create_kpi_card(title, value, icon="", delta=None, help_text=None):
    """Create a styled KPI card"""
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    ">
        <h3 style="margin: 0; color: white; font-size: 1.8rem;">{icon} {value}</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{title}</p>
        {f'<p style="margin: 0; font-size: 0.8rem; margin-top: 0.5rem;">{delta}</p>' if delta else ''}
    </div>
    """
    return card_html

def compute_mgroup_insights(successful_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute M Group specific aggregate insights from successful results"""
    resumes_seen: Dict[int, Dict[str, Any]] = {}

    for r in successful_results:
        idx = r.get("resume_index")
        if idx is None:
            continue
        if idx in resumes_seen:
            continue

        # Look at each unique resume once
        resume = st.session_state.resumes_data[idx]
        text = (resume.get("raw_text") or "").lower()

        stats = {
            "infra": False,
            "hse": False,
            "uk_ie": False,
            "project_mentions": 0
        }

        infra_keywords = [
            "water", "wastewater", "clean water", "potable water", "sewerage",
            "trunk main", "pipeline", "utilities", "electricity", "substation",
            "overhead line", "gas", "highways", "road", "motorway",
            "rail", "railway", "airport", "aviation", "telecom", "telecommunications",
            "fibre", "fiber", "fibre optic"
        ]
        if any(k in text for k in infra_keywords):
            stats["infra"] = True

        hse_keywords = [
            "health and safety", "hse", "sheq", "cdm", "risk assessment",
            "method statement", "rams", "nebosh", "iosh",
            "permit to work", "ptw", "safe system of work"
        ]
        if any(k in text for k in hse_keywords):
            stats["hse"] = True

        uk_keywords = [
            "united kingdom", "uk", "england", "scotland", "wales",
            "northern ireland", "republic of ireland", "dublin",
            "london", "manchester", "birmingham", "glasgow",
            "cardiff", "belfast"
        ]
        if any(k in text for k in uk_keywords):
            stats["uk_ie"] = True

        stats["project_mentions"] = text.count("project")
        resumes_seen[idx] = stats

    total = max(len(resumes_seen), 1)
    infra_count = sum(1 for s in resumes_seen.values() if s["infra"])
    hse_count = sum(1 for s in resumes_seen.values() if s["hse"])
    uk_ie_count = sum(1 for s in resumes_seen.values() if s["uk_ie"])
    avg_projects = sum(s["project_mentions"] for s in resumes_seen.values()) / total

    return {
        "infra_experienced_candidates": infra_count,
        "hse_focused_candidates": hse_count,
        "uk_ie_candidates": uk_ie_count,
        "avg_projects_per_candidate": avg_projects
    }

def render_comprehensive_results():
    """Render comprehensive analysis results with KPI cards and different views based on analysis depth"""
    st.subheader("Analysis Results Dashboard")

    if not st.session_state.analysis_results:
        st.info("No analysis results available")
        return

    results = st.session_state.analysis_results
    successful_results = [r for r in results if r.get('status') == 'completed']

    if not successful_results:
        st.warning("No successful analyses to display")
        return

    # Get the analysis depth from the first result (they should all be the same)
    analysis_depth = successful_results[0].get('analysis_depth', 'Quick Scoring')

    # KPI Cards Section
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_html = create_kpi_card("Total Analyses", str(len(results)), "")
        st.markdown(kpi_html, unsafe_allow_html=True)

    with col2:
        kpi_html = create_kpi_card(
            "Successful",
            str(len(successful_results)),
            "",
            delta=f"{len(successful_results)/len(results)*100:.1f}% success rate"
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

    with col3:
        avg_score = np.mean([r['scores']['composite_score'] for r in successful_results])
        kpi_html = create_kpi_card("Average Score", f"{avg_score:.3f}", "")
        st.markdown(kpi_html, unsafe_allow_html=True)

    with col4:
        top_score = max([r['scores']['composite_score'] for r in successful_results])
        kpi_html = create_kpi_card("Top Score", f"{top_score:.3f}", "")
        st.markdown(kpi_html, unsafe_allow_html=True)

    # Additional KPI row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        excellent_count = len([r for r in successful_results if r['scores']['composite_score'] >= 0.8])
        kpi_html = create_kpi_card("Excellent Matches", str(excellent_count), "", 
                                  delta="Score ≥ 0.8")
        st.markdown(kpi_html, unsafe_allow_html=True)

    with col6:
        good_count = len([r for r in successful_results if 0.6 <= r['scores']['composite_score'] < 0.8])
        kpi_html = create_kpi_card("Good Matches", str(good_count), "", 
                                  delta="Score 0.6-0.8")
        st.markdown(kpi_html, unsafe_allow_html=True)

    with col7:
        avg_relevance = np.mean([r['scores'].get('relevance_score', 0) for r in successful_results])
        kpi_html = create_kpi_card("Avg Relevance", f"{avg_relevance:.3f}", "")
        st.markdown(kpi_html, unsafe_allow_html=True)

    with col8:
        avg_experience = np.mean([r['scores'].get('experience_score', 0) for r in successful_results])
        kpi_html = create_kpi_card("Avg Experience", f"{avg_experience:.3f}", "")
        st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("---")

    # M Group specific insights
    st.subheader("M Group Infrastructure Insights")
    m_stats = compute_mgroup_insights(successful_results)
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        kpi_html = create_kpi_card(
            "Civils / Utilities Experience",
            str(m_stats["infra_experienced_candidates"]),
            "",
            delta="Candidates mentioning water/energy/highways/rail/aviation/telecom"
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

    with mcol2:
        kpi_html = create_kpi_card(
            "HSE / CDM Indicators",
            str(m_stats["hse_focused_candidates"]),
            "",
            delta="NEBOSH/IOSH/CDM/permits/RAMS in resume"
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

    with mcol3:
        kpi_html = create_kpi_card(
            "UK & Ireland Based",
            str(m_stats["uk_ie_candidates"]),
            "",
            delta="Location mentions in UK & Ireland"
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

    with mcol4:
        kpi_html = create_kpi_card(
            "Avg 'Project' Mentions",
            f"{m_stats['avg_projects_per_candidate']:.1f}",
            "",
            delta="Proxy for project-driven experience"
        )
        st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("---")

    # Different displays based on analysis depth
    if analysis_depth == "Quick Scoring":
        render_quick_scoring_results(successful_results)
    elif analysis_depth == "Detailed Analysis":
        render_detailed_analysis_results(successful_results)
    elif analysis_depth == "Comprehensive Report":
        render_comprehensive_report_results(successful_results)
    else:
        # Fallback to interactive view selector
        render_interactive_results(successful_results)

def render_enhanced_chatbot():
    """Enhanced chatbot with enter icon submit"""
    st.header("AI Chatbot")
    st.markdown("**Chat about all resumes and analysis results in a single conversation**")

    st.info(
        "This chatbot is tuned for M Group Services' infrastructure hiring across "
        "water, energy, highways, rail & aviation, and telecom in the UK and Ireland."
    )

    if not st.session_state.screening_engine:
        st.error("System not initialized")
        return

    # Context information
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Resume Context:** {len(st.session_state.resumes_data)} resumes loaded")
    with col2:
        st.info(f"**Analysis Context:** {len(st.session_state.analysis_results)} analyses completed")

    # Chat history display
    if st.session_state.chatbot_history:
        st.subheader("💬 Conversation History")
        for i, exchange in enumerate(st.session_state.chatbot_history):
            # User message
            with st.container():
                st.markdown(f"**You:** {exchange['question']}")
                st.markdown(f"**AI:** {exchange['answer']}")
                st.caption(f"Time: {exchange.get('timestamp', 'Unknown')}")
                st.markdown("---")

    # Chat input with enter icon
    st.subheader("Ask About Your Resume Portfolio")
    
    # Create form for enter key submission
    with st.form(key="chat_form", clear_on_submit=True):
        user_question = st.text_input(
            "Ask about any resume, comparison, or analysis:",
            placeholder="e.g., Which candidates are best for our M Group Site Engineer and Project Manager roles?",
            key="enhanced_chat_input"
        )
        
        # Submit button with enter icon
        col1, col2 = st.columns([3, 1])
        with col1:
            submit_chat = st.form_submit_button("⏎", type="primary", use_container_width=True)
        with col2:
            clear_chat = st.form_submit_button("🧹 Clear")

    # Process chat
    if submit_chat and user_question:
        process_enhanced_chat(user_question)
    
    if clear_chat:
        st.session_state.chatbot_history = []
        st.rerun()

def render_system_status():
    """System status and diagnostics"""
    st.header("System Status")

    if not st.session_state.screening_engine:
        st.error("System not initialized")
        return

    try:
        system_status = st.session_state.screening_engine.get_system_status()

        # Overall status
        if system_status.get('ready_for_screening', False):
            st.success("System Ready for Multi-Analysis")
        else:
            st.error("System Issues Detected")

        # Detailed status
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("AI Status")
            google_status = system_status.get('google_ai_status', {})
            conn_status = google_status.get('connection_status', {})
            if conn_status.get('connected', False):
                st.success("Google AI Connected")
                models = google_status.get('models', {})
                st.info(f"Model: {models.get('main_model', 'Unknown')}")
            else:
                st.error("Google AI Connection Failed")
                error = conn_status.get('error', 'Unknown error')
                st.error(f"Error: {error}")

        with col2:
            st.subheader("Session Stats")
            st.metric("Resumes Processed", len(st.session_state.resumes_data))
            st.metric("JDs Available", len(st.session_state.job_descriptions))
            st.metric("Analyses Completed", len(st.session_state.analysis_results))

        with col3:
            st.subheader("Performance")
            stats = system_status.get('processing_stats', {})
            st.metric("Total API Calls", stats.get('google_ai_calls', 0))
            st.metric("Avg Processing Time", f"{stats.get('avg_processing_time', 0):.2f}s")

    except Exception as e:
        st.error(f"Status check failed: {e}")

# [Existing helper functions from original code, with small updates where needed]

def render_quick_scoring_results(results):
    """Render quick scoring results - simple score table"""
    st.subheader("Quick Scoring Results")
    st.markdown("*Simple score overview with basic metrics*")

    # Create simple scoring table
    table_data = []
    for i, result in enumerate(sorted(results, key=lambda x: x['scores']['composite_score'], reverse=True)):
        resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
        jd_title = result['jd_title']
        scores = result.get('scores', {})

        # Get candidate name if available
        candidate_name = result.get('analysis', {}).get('extracted_data', {}).get('candidate_name', 'Unknown')

        table_data.append({
            'Rank': i + 1,
            'Candidate': candidate_name,
            'Resume': resume_name[:20] + "..." if len(resume_name) > 20 else resume_name,
            'Job': jd_title[:25] + "..." if len(jd_title) > 25 else jd_title,
            'Score': round(scores.get('composite_score', 0), 3),
            'Match': '🟢 Strong' if scores.get('composite_score', 0) > 0.7 else
                    '🟡 Good' if scores.get('composite_score', 0) > 0.5 else
                    '🔴 Weak'
        })

    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400)

        # Quick insights
        st.markdown("### Quick Insights")
        top_matches = [r for r in results if r['scores']['composite_score'] > 0.6]
        if top_matches:
            st.success(f"Found {len(top_matches)} strong candidate-job matches (score > 0.6)")

            # Show top 3 matches
            st.markdown("**Top 3 Matches:**")
            for i, result in enumerate(sorted(results, key=lambda x: x['scores']['composite_score'], reverse=True)[:3]):
                resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
                candidate_name = result.get('analysis', {}).get('extracted_data', {}).get('candidate_name', 'Unknown')
                jd_title = result['jd_title']
                score = result['scores']['composite_score']
                st.write(f"**{i+1}.** {candidate_name} → {jd_title}: **{score:.3f}**")
        else:
            st.warning("No strong matches found. Consider reviewing job requirements or candidate pool.")

def render_detailed_analysis_results(results):
    """Render detailed analysis results"""
    st.subheader("Detailed Analysis Results")
    st.markdown("*Comprehensive breakdown with detailed insights and comparisons*")

    # Results visualization options
    view_mode = st.selectbox(
        "Select View:",
        [
            "ALL Candidates - Complete Matrix",
            "Score Matrix",
            "Top Matches",
            "By Candidate",
            "By Job",
            "Detailed Table"
        ],
        key="detailed_view_selector"
    )

    # Route to the correct function
    if view_mode == "ALL Candidates - Complete Matrix":
        render_all_candidates_complete_matrix(results)
    elif view_mode == "Score Matrix":
        render_score_matrix(results)
    elif view_mode == "Top Matches":
        render_top_matches_detailed(results)
    elif view_mode == "By Candidate":
        render_by_candidate(results)
    elif view_mode == "By Job":
        render_by_job(results)
    else:
        render_detailed_table(results)

def render_comprehensive_report_results(results):
    """Render comprehensive report with full analysis"""
    st.subheader("Comprehensive Analysis Report")
    st.markdown("*Complete analysis with strategic insights and hiring recommendations*")

    # Executive Summary
    st.markdown("## Executive Summary")
    scores = [r['scores']['composite_score'] for r in results]
    total_analyses = len(results)
    strong_matches = len([s for s in scores if s >= 0.7])
    good_matches = len([s for s in scores if 0.5 <= s < 0.7])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Strong Matches", f"{strong_matches}/{total_analyses}")
        st.metric("Conversion Rate", f"{strong_matches/total_analyses*100:.1f}%")
    with col2:
        st.metric("🟡 Good Matches", f"{good_matches}/{total_analyses}")
        st.metric("Combined Success", f"{(strong_matches + good_matches)/total_analyses*100:.1f}%")
    with col3:
        st.metric("Avg Score", f"{np.mean(scores):.3f}")
        st.metric("Best Score", f"{max(scores):.3f}")

def render_interactive_results(results):
    """Render interactive results with view selector"""
    st.subheader("Interactive Results View")
    view_mode = st.selectbox(
        "Choose Analysis View:",
        ["ALL Candidates - Complete Matrix", "Score Matrix", "Top Matches", "By Candidate", "By Job", "Detailed Table"]
    )

    if view_mode == "ALL Candidates - Complete Matrix":
        render_all_candidates_complete_matrix(results)
    elif view_mode == "Score Matrix":
        render_score_matrix(results)
    elif view_mode == "Top Matches":
        render_top_matches_detailed(results)
    elif view_mode == "By Candidate":
        render_by_candidate(results)
    elif view_mode == "By Job":
        render_by_job(results)
    else:
        render_detailed_table(results)

# Placeholder implementations for complex functions (to maintain functionality)
def render_all_candidates_complete_matrix(results):
    """Show ALL candidates with ALL job scores"""
    st.info("Complete candidate matrix functionality maintained - displaying simplified view")
    render_detailed_table(results)

def render_score_matrix(results):
    """Render score matrix visualization"""
    st.subheader("Resume vs Job Description Score Matrix")
    resume_names = list(set([st.session_state.resumes_data[r['resume_index']]['filename'] for r in results]))
    jd_names = list(set([r['jd_title'] for r in results]))

    # Create matrix data
    matrix_data = []
    for resume_name in resume_names:
        row = []
        for jd_name in jd_names:
            matching_result = next(
                (
                    r for r in results
                    if st.session_state.resumes_data[r['resume_index']]['filename'] == resume_name
                    and r['jd_title'] == jd_name
                ),
                None
            )
            score = matching_result['scores']['composite_score'] if matching_result else 0
            row.append(score)
        matrix_data.append(row)

    df_matrix = pd.DataFrame(matrix_data, index=resume_names, columns=jd_names)
    st.dataframe(
        df_matrix.style.format("{:.3f}"),
        use_container_width=True,
        height=400
    )
    st.info("**Score Guide:** 0.8+ = Excellent, 0.6-0.8 = Good, 0.4-0.6 = Fair, <0.4 = Poor")

def render_top_matches_detailed(results):
    """Render top matches with detailed breakdown"""
    st.subheader("Top Resume-Job Matches (Detailed)")
    sorted_results = sorted(results, key=lambda x: x['scores']['composite_score'], reverse=True)

    for i, result in enumerate(sorted_results[:10]):
        resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
        jd_title = result['jd_title']
        score = result['scores']['composite_score']

        # Determine match quality
        if score >= 0.8:
            match_emoji = "🟢"
            match_text = "Excellent Match"
        elif score >= 0.6:
            match_emoji = "🟡"
            match_text = "Good Match"
        elif score >= 0.4:
            match_emoji = "🟠"
            match_text = "Fair Match"
        else:
            match_emoji = "🔴"
            match_text = "Poor Match"

        with st.expander(
            f"{match_emoji} #{i+1} {resume_name} → {jd_title} ({score:.3f}) - {match_text}",
            expanded=(i < 3)
        ):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown("**Score Breakdown**")
                scores = result['scores']
                score_data = {
                    'Relevance': scores.get('relevance_score', 0),
                    'Experience': scores.get('experience_score', 0),
                    'Skills': scores.get('skills_score', 0),
                    'Overall': scores.get('composite_score', 0)
                }

                for score_type, score_val in score_data.items():
                    percentage = score_val * 100
                    st.write(f"**{score_type}:** {score_val:.3f} ({percentage:.1f}%)")
                    st.progress(min(score_val, 1.0))

            with col2:
                st.markdown("**Candidate Profile**")
                analysis = result.get('analysis', {})
                extracted_data = analysis.get('extracted_data', {})
                st.write(f"**Name:** {extracted_data.get('candidate_name', 'Unknown')}")
                st.write(f"**Experience:** {extracted_data.get('total_years_experience', 'N/A')} years")

def render_by_candidate(results):
    """Render results grouped by candidate"""
    st.subheader("Results by Candidate")
    st.markdown("*View how each candidate performs across different job roles*")

    candidate_groups = {}
    for result in results:
        resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
        candidate_name = result.get('analysis', {}).get('extracted_data', {}).get('candidate_name', resume_name)
        if candidate_name not in candidate_groups:
            candidate_groups[candidate_name] = []
        candidate_groups[candidate_name].append(result)

    for candidate, candidate_results in candidate_groups.items():
        avg_score = np.mean([r['scores']['composite_score'] for r in candidate_results])
        best_score = max([r['scores']['composite_score'] for r in candidate_results])

        with st.expander(f"{candidate} - Avg: {avg_score:.3f} | Best: {best_score:.3f}"):
            sorted_results = sorted(candidate_results, key=lambda x: x['scores']['composite_score'], reverse=True)
            for result in sorted_results:
                jd_title = result['jd_title']
                score = result['scores']['composite_score']
                if score >= 0.7:
                    color = "🟢"
                elif score >= 0.5:
                    color = "🟡"
                else:
                    color = "🔴"
                st.write(f"{color} **{jd_title}:** {score:.3f}")

def render_by_job(results):
    """Render results grouped by job description"""
    st.subheader("Results by Job Description")
    st.markdown("*View which candidates are best suited for each role*")

    job_groups = {}
    for result in results:
        jd_title = result['jd_title']
        if jd_title not in job_groups:
            job_groups[jd_title] = []
        job_groups[jd_title].append(result)

    for job_title, job_results in job_groups.items():
        avg_score = np.mean([r['scores']['composite_score'] for r in job_results])
        best_score = max([r['scores']['composite_score'] for r in job_results])
        qualified_candidates = len([r for r in job_results if r['scores']['composite_score'] > 0.6])

        with st.expander(
            f"{job_title} - Avg: {avg_score:.3f} | Best: {best_score:.3f} | Qualified: {qualified_candidates}"
        ):
            sorted_results = sorted(job_results, key=lambda x: x['scores']['composite_score'], reverse=True)
            st.markdown("**Candidate Rankings:**")
            for i, result in enumerate(sorted_results):
                resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
                candidate_name = result.get('analysis', {}).get('extracted_data', {}).get('candidate_name', resume_name)
                score = result['scores']['composite_score']

                if score >= 0.7:
                    color = "🟢"
                    status = "Strong"
                elif score >= 0.5:
                    color = "🟡"
                    status = "Good"
                else:
                    color = "🔴"
                    status = "Weak"
                st.write(f"{color} **{i+1}.** {candidate_name} - {score:.3f} ({status})")

def render_detailed_table(results):
    """Render detailed results table"""
    st.subheader("📋 Detailed Results Table")

    table_data = []
    for result in results:
        if result.get('status') == 'completed':
            resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
            jd_title = result['jd_title']
            scores = result.get('scores', {})

            extracted_data = result.get('analysis', {}).get('extracted_data', {})
            candidate_name = extracted_data.get('candidate_name', 'Unknown')
            experience = extracted_data.get('total_years_experience', 0)

            table_data.append({
                'Candidate': candidate_name,
                'Resume File': resume_name,
                'Job Position': jd_title,
                'Overall Score': round(scores.get('composite_score', 0), 3),
                'Relevance': round(scores.get('relevance_score', 0), 3),
                'Experience': round(scores.get('experience_score', 0), 3),
                'Skills': round(scores.get('skills_score', 0), 3),
                'Years Exp': experience,
                'Match Quality': '🟢 Strong' if scores.get('composite_score', 0) > 0.7 else
                               '🟡 Good' if scores.get('composite_score', 0) > 0.5 else
                               '🔴 Weak'
            })

    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=500)

# Helper functions

def process_and_store_resumes(uploaded_files):
    """Process uploaded resumes and store in session state"""
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing {uploaded_file.name}...")

        try:
            # Save file temporarily
            temp_path = save_temp_file(uploaded_file)

            # Ensure parser exists (defensive in case engine was replaced)
            if not hasattr(st.session_state.screening_engine, "parser") or st.session_state.screening_engine.parser is None:
                st.session_state.screening_engine.parser = EnhancedResumeParser()

            # Parse resume
            result = st.session_state.screening_engine.parser.parse_resume(temp_path, uploaded_file.name)

            if result.get('success'):
                # Extract additional data using Google AI (if manager is available)
                extraction_result = {"success": False, "data": {}}
                google_manager = getattr(st.session_state.screening_engine, "google_ai_manager", None)
                if google_manager is not None:
                    try:
                        extraction_result = google_manager.extract_resume_data(
                            result.get('cleaned_text', '')
                        )
                    except Exception as e:
                        st.error(f"Google AI data extraction failed for {uploaded_file.name}: {e}")

                resume_data = {
                    'filename': uploaded_file.name,
                    'file_size': uploaded_file.size,
                    'upload_time': datetime.now().isoformat(),
                    'raw_text': result.get('cleaned_text', ''),
                    'parsed_data': result,
                    'extracted_data': extraction_result.get('data', {}) if extraction_result.get('success') else {},
                    'processing_status': 'completed'
                }

                st.session_state.resumes_data.append(resume_data)
                st.success(f"{uploaded_file.name} processed successfully")
            else:
                st.error(f"Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}")

            # Clean up temp file
            os.unlink(temp_path)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    progress_bar.empty()
    status_text.empty()

    if len(st.session_state.resumes_data) > 0:
        st.success(
            f"Successfully processed "
            f"{len([f for f in uploaded_files if any(r['filename'] == f.name for r in st.session_state.resumes_data)])} "
            f"resumes!"
        )

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF"""
    try:
        temp_path = save_temp_file(uploaded_file)
        
        # Use the parser's extract_text_from_pdf method
        if hasattr(st.session_state.screening_engine.parser, 'extract_text_from_pdf'):
            text = st.session_state.screening_engine.parser.extract_text_from_pdf(temp_path)
        else:
            # Fallback method using fitz directly
            import fitz  # PyMuPDF
            doc = fitz.open(temp_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

        os.unlink(temp_path)
        return text.strip()

    except Exception as e:
        st.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file"""
    try:
        temp_path = save_temp_file(uploaded_file)

        # Use the parser's extract_text method
        if hasattr(st.session_state.screening_engine.parser, 'extract_text'):
            text = st.session_state.screening_engine.parser.extract_text(temp_path)
        else:
            # Fallback methods
            if uploaded_file.name.endswith('.txt'):
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif uploaded_file.name.endswith(('.docx', '.doc')):
                import docx
                doc = docx.Document(temp_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            else:
                text = ""

        os.unlink(temp_path)
        return text.strip()

    except Exception as e:
        st.error(f"File extraction error: {e}")
        return ""

def save_temp_file(uploaded_file):
    """Save uploaded file temporarily"""
    temp_dir = "./data/temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def add_job_description(title, description, method,
                        mgroup_sector: str = "",
                        mgroup_region: str = "",
                        mgroup_role_family: str = ""):
    """Add job description to session state"""
    try:
        jd_data = {
            'title': title,
            'description': description,
            'input_method': method,
            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'word_count': len(description.split()),
            'employer': "M Group Services",
            'mgroup_sector': mgroup_sector or "",
            'mgroup_region': mgroup_region or "",
            'mgroup_role_family': mgroup_role_family or ""
        }

        st.session_state.job_descriptions.append(jd_data)
        st.success(f"Added job description: {title}")
        
        # Force rerun to update the display
        st.rerun()

    except Exception as e:
        st.error(f"Error adding job description: {e}")

def build_mgroup_job_context(jd_data: Dict[str, Any]) -> str:
    """Append M Group specific employer context to the JD description."""
    base_desc = jd_data.get('description', '') or ""

    sector = jd_data.get('mgroup_sector') or ""
    role_family = jd_data.get('mgroup_role_family') or ""
    region = jd_data.get('mgroup_region') or ""

    context_lines = [
        "Employer context:",
        (
            "The hiring organisation is M Group Services, which delivers essential "
            "infrastructure services across water, energy, transport (highways, rail and aviation) "
            "and telecoms in the UK and Ireland, operating with a strong safety-first and "
            "client/customer-centric culture."
        )
    ]
    if sector:
        context_lines.append(f"This vacancy sits in the {sector} division.")
    if role_family:
        context_lines.append(f"The role family is {role_family}.")
    if region:
        context_lines.append(f"Primary region or base for this role: {region}.")

    extras_text = "\n".join(context_lines)

    if base_desc.strip():
        return base_desc.strip() + "\n\n" + extras_text
    else:
        return extras_text

def run_comprehensive_analysis(selected_resumes, selected_jds, analysis_depth):
    """Run comprehensive multi-resume vs multi-JD analysis"""
    st.markdown("### Running Comprehensive Analysis...")

    # Clear previous results
    st.session_state.analysis_results = []

    results = []
    total_analyses = len(selected_resumes) * len(selected_jds)
    progress_bar = st.progress(0)
    status_text = st.empty()
    analysis_count = 0

    for resume_idx in selected_resumes:
        resume_data = st.session_state.resumes_data[resume_idx]

        for jd_idx in selected_jds:
            jd_data = st.session_state.job_descriptions[jd_idx]

            analysis_count += 1
            progress = analysis_count / total_analyses
            progress_bar.progress(progress)
            status_text.text(
                f"Analyzing {resume_data['filename']} vs {jd_data['title']} "
                f"({analysis_count}/{total_analyses})"
            )

            try:
                # Create temporary file for analysis
                temp_path = create_temp_file_from_data(resume_data['raw_text'], resume_data['filename'])

                # Build augmented JD description with M Group context
                augmented_jd_description = build_mgroup_job_context(jd_data)

                # Run analysis using existing screening engine
                result = st.session_state.screening_engine.process_single_resume(
                    temp_path,
                    resume_data['filename'],
                    augmented_jd_description
                )

                # Add context information
                result['resume_index'] = resume_idx
                result['jd_index'] = jd_idx
                result['jd_title'] = jd_data['title']
                result['analysis_depth'] = analysis_depth
                result['analysis_timestamp'] = datetime.now().isoformat()

                results.append(result)

                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

            except Exception as e:
                st.error(f"Analysis failed for {resume_data['filename']} vs {jd_data['title']}: {e}")

    # Store results
    st.session_state.analysis_results = results

    progress_bar.empty()
    status_text.empty()

    st.success(f"Completed {len(results)} analyses!")

    # Show quick summary
    if results:
        show_analysis_summary(results)

def create_temp_file_from_data(text_data, filename):
    """Create temporary file from text data"""
    temp_dir = "./data/temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"temp_{filename}.txt")
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(text_data)
    return temp_path

def process_enhanced_chat(question):
    """Process chat question with comprehensive context"""
    try:
        # Build comprehensive context from all loaded data
        context_parts = []

        # M Group employer context
        context_parts.append(
            "EMPLOYER CONTEXT: M Group Services delivers essential infrastructure "
            "services across water, energy, transport (highways, rail and aviation) and "
            "telecoms for clients across the UK and Ireland, with a strong safety-first "
            "and client/customer-centric culture."
        )

        # Add resume context
        if st.session_state.resumes_data:
            context_parts.append(f"RESUME PORTFOLIO ({len(st.session_state.resumes_data)} resumes):")
            for i, resume in enumerate(st.session_state.resumes_data[:10]):  # Limit to top 10
                extracted = resume.get('extracted_data', {})
                name = extracted.get('candidate_name', f'Candidate_{i+1}')
                exp = extracted.get('total_years_experience', 'Unknown')
                skills = ', '.join(extracted.get('technical_skills', [])[:5])
                context_parts.append(f"- {name}: {exp} years exp, Skills: {skills}")

        # Add job description context
        if st.session_state.job_descriptions:
            context_parts.append(f"\nJOB DESCRIPTIONS ({len(st.session_state.job_descriptions)} jobs):")
            for jd in st.session_state.job_descriptions:
                context_bits = []
                if jd.get('mgroup_sector'):
                    context_bits.append(f"Sector: {jd['mgroup_sector']}")
                if jd.get('mgroup_region'):
                    context_bits.append(f"Region: {jd['mgroup_region']}")
                if jd.get('mgroup_role_family'):
                    context_bits.append(f"Role family: {jd['mgroup_role_family']}")
                context_suffix = f" ({'; '.join(context_bits)})" if context_bits else ""
                context_parts.append(f"- {jd['title']}{context_suffix}: {jd['description'][:100]}...")

        context = "\n".join(context_parts)

        # Get response from AI
        with st.spinner("AI analyzing comprehensive context..."):
            response = st.session_state.screening_engine.google_ai_manager.comprehensive_chat_response(
                question, context
            )

            if response['success']:
                # Add to chat history
                st.session_state.chatbot_history.append({
                    'question': question,
                    'answer': response['answer'],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'context_type': 'comprehensive'
                })
                st.rerun()
            else:
                st.error(f"Chat failed: {response.get('error', 'Unknown error')}")

    except Exception as e:
        st.error(f"Chat processing error: {e}")

def show_analysis_summary(results):
    """Show quick analysis summary"""
    st.markdown("### Quick Analysis Summary")

    successful = [r for r in results if r.get('status') == 'completed']
    if successful:
        scores = [r['scores']['composite_score'] for r in successful]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Best Match", f"{max(scores):.3f}")
        with col2:
            st.metric("Average Score", f"{np.mean(scores):.3f}")
        with col3:
            st.metric("Success Rate", f"{len(successful)/len(results)*100:.1f}%")

def export_comprehensive_results():
    """Export comprehensive results to CSV"""
    if not st.session_state.analysis_results:
        st.warning("No results to export")
        return

    try:
        csv_data = []
        for result in st.session_state.analysis_results:
            if result.get('status') == 'completed':
                resume_name = st.session_state.resumes_data[result['resume_index']]['filename']
                jd_title = result['jd_title']
                scores = result.get('scores', {})

                csv_data.append({
                    'Resume': resume_name,
                    'Job_Description': jd_title,
                    'Composite_Score': scores.get('composite_score', 0),
                    'Relevance_Score': scores.get('relevance_score', 0),
                    'Experience_Score': scores.get('experience_score', 0),
                    'Skills_Score': scores.get('skills_score', 0),
                    'Analysis_Date': result.get('analysis_timestamp', ''),
                })

        if csv_data:
            df = pd.DataFrame(csv_data)
            csv_string = df.to_csv(index=False)

            st.download_button(
                label="Download Results CSV",
                data=csv_string,
                file_name=f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

            st.success("Export ready for download!")

    except Exception as e:
        st.error(f"Export failed: {e}")

def show_resume_previews():
    """Show preview of all resumes"""
    st.info("Resume preview functionality will be implemented")

def show_resume_statistics():
    """Show statistics about resume portfolio"""
    st.info("Resume statistics functionality will be implemented")

def edit_job_description(index):
    """Edit job description (placeholder function)"""
    st.info("Edit functionality will be implemented")

if __name__ == "__main__":
    main()
