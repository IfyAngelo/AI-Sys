# streamlit_app.py
import streamlit as st
import requests
import uuid
import os
import tempfile
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"  # Update if deployed

def main():
    st.title("AI-Teacher's Content Assistant")
    st.markdown("**Nigerian Educational Content Generation System**")

    # Initialize session state
    if 'scheme_id' not in st.session_state:
        st.session_state.scheme_id = None
    if 'lesson_plan_id' not in st.session_state:
        st.session_state.lesson_plan_id = None
    if 'lesson_notes_id' not in st.session_state:
        st.session_state.lesson_notes_id = None
    if 'base_params' not in st.session_state:
        st.session_state.base_params = {}

    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs([
        "📚 Content Generation", 
        "📄 PDF Processing", 
        "📁 Document Conversion"
    ])

    with tab1:  # Content Generation Tab
        st.header("Curriculum Content Generation Workflow")
        
        # Step 1: Scheme of Work Generation
        with st.expander("1. Create Scheme of Work", expanded=True):
            st.markdown("### Scheme of Work Parameters")
            col1, col2, col3 = st.columns(3)
            with col1:
                subject = st.selectbox("Subject", ["Civic Education", "Social Studies", "Security Education"])
            with col2:
                grade_level = st.selectbox("Grade Level", ["Primary One", "Primary Two", "Primary Three"])
            with col3:
                topic = st.text_input("Topic", "National Consciousness")

            if st.button("Generate Scheme of Work"):
                payload = {
                    "subject": subject,
                    "grade_level": grade_level,
                    "topic": topic
                }
                st.session_state.base_params = payload  # Store base parameters
                
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/content/scheme-of-work",
                        json=payload
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.scheme_id = result['scheme_of_work_id']
                        st.success("Scheme generated successfully!")
                        st.markdown(f"**Generated Scheme ID:** `{st.session_state.scheme_id}`")
                        st.markdown("### Scheme Content")
                        st.markdown(result['scheme_of_work_output'])
                    else:
                        st.error(f"Error generating scheme: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"API Connection Error: {str(e)}")

        # Step 2: Lesson Plan Generation
        with st.expander("2. Create Lesson Plan", expanded=st.session_state.scheme_id is not None):
            if st.session_state.scheme_id:
                st.markdown("### Teaching Constraints")
                limitations = st.text_area("What challenges are you facing? (e.g., limited resources, large class size)",
                "Large class size (60 students), Limited textbooks (5 copies), No projector")
                # Get parameters from session state instead of new inputs
                duration = st.text_input("Lesson Duration (minutes)", "40")
                objectives = st.text_area("Learning Objectives", 
                    "All will: [Basic objective]\nMost will: [Intermediate objective]\nSome will: [Advanced objective]")
                
                if st.button("Generate Adaptive Lesson Plan"):
                    payload = {
                        "scheme_of_work_id": st.session_state.scheme_id,
                        "limitations": limitations,
                        **st.session_state.base_params  # Include subject, grade_level, topic
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/content/lesson-plan",
                            json=payload
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.lesson_plan_id = result['lesson_plan_id']
                            st.success("Lesson plan generated successfully!")
                            st.markdown(f"**Lesson Plan ID:** `{st.session_state.lesson_plan_id}`")
                            st.markdown("### Lesson Plan Content")
                            st.markdown(result['lesson_plan_output'])
                        else:
                            st.error(f"Error generating lesson plan: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"API Connection Error: {str(e)}")
            else:
                st.warning("Please generate a Scheme of Work first")

        # Step 3: Lesson Notes Generation
        with st.expander("3. Create Lesson Notes", expanded=st.session_state.lesson_plan_id is not None):
            if st.session_state.lesson_plan_id and st.session_state.scheme_id:
                st.markdown("### Lesson Notes Parameters")
                teaching_method = st.selectbox("Teaching Method", ["Demonstration", "Discussion", "Activity-Based"])
                
                if st.button("Generate Lesson Notes"):
                    payload = {
                        "scheme_of_work_id": st.session_state.scheme_id,
                        "lesson_plan_id": st.session_state.lesson_plan_id,
                        "teaching_method": teaching_method,
                        **st.session_state.base_params  # Include subject, grade_level, topic
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/content/lesson-notes",
                            json=payload
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.lesson_notes_id = result['lesson_notes_id']
                            st.success("Lesson notes generated successfully!")
                            st.markdown(f"**Lesson Notes ID:** `{st.session_state.lesson_notes_id}`")
                            st.markdown("### Lesson Notes Content")
                            st.markdown(result['content'])
                        else:
                            st.error(f"Error generating notes: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"API Connection Error: {str(e)}")
            else:
                st.warning("Please generate a Lesson Plan first")

    with tab2:  # PDF Processing Tab
        st.header("PDF Processing and Vectorization")
        uploaded_file = st.file_uploader("Upload Curriculum PDF", type="pdf")
        
        if uploaded_file:
            # Use temporary file with auto-cleanup
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_path = temp_file.name

            if st.button("Process PDF"):
                try:
                    with open(temp_path, "rb") as f:
                        files = {"file": (uploaded_file.name, f, "application/pdf")}
                        response = requests.post(
                            f"{API_BASE_URL}/api/embeddings/process_pdf",
                            files=files
                        )
                    
                    if response.status_code == 200:
                        st.success("PDF processed and stored in vector database!")
                        st.json(response.json())
                    else:
                        st.error(f"Processing failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Processing error: {str(e)}")
                finally:
                    os.unlink(temp_path)  # Ensure file cleanup

    with tab3:  # Document Conversion Tab
        st.header("Document Format Conversion")
        
        conversion_type = st.radio("Select Conversion Type", [
            "Scheme of Work to DOCX",
            "Lesson Plan to DOCX",
            "Lesson Notes to DOCX"
        ])

        content_id = st.text_input("Enter Document ID")
        custom_name = st.text_input("Custom Filename (optional)")
        
        if st.button("Convert to DOCX"):
            if not content_id:
                st.warning("Please enter a document ID")
                return
                
            try:
                payload = {
                    "content_type": conversion_type.lower().split()[0],
                    "custom_filename": custom_name or None
                }
                
                # Add appropriate ID based on content type
                id_type = {
                    "scheme": "scheme_of_work_id",
                    "plan": "lesson_plan_id",
                    "notes": "lesson_notes_id"
                }[conversion_type.lower().split()[0]]
                
                payload[id_type] = content_id

                response = requests.post(
                    f"{API_BASE_URL}/api/convert/generate-document",
                    json=payload
                )

                if response.status_code == 200:
                    st.success("Conversion successful!")
                    download_link = f"{API_BASE_URL}{response.json()['file_path']}"
                    st.markdown(f"[Download DOCX File]({download_link})")
                else:
                    st.error(f"Conversion failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Conversion error: {str(e)}")

if __name__ == "__main__":
    main()