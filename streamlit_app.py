# # streamlit_app.py
# import streamlit as st
# import requests
# import uuid
# import os
# import tempfile
# from datetime import datetime

# # Configuration
# API_BASE_URL = "http://localhost:8001"  # Update if deployed

# def main():
#     st.title("AI-Teacher's Content Assistant")
#     st.markdown("**Nigerian Educational Content Generation System**")

#     # Initialize session state
#     if 'scheme_id' not in st.session_state:
#         st.session_state.scheme_id = None
#     if 'lesson_plan_id' not in st.session_state:
#         st.session_state.lesson_plan_id = None
#     if 'lesson_notes_id' not in st.session_state:
#         st.session_state.lesson_notes_id = None
#     if 'base_params' not in st.session_state:
#         st.session_state.base_params = {}

#     # Create tabs for different functionalities
#     tab1, tab2, tab3 = st.tabs([
#         "📚 Content Generation", 
#         "📄 PDF Processing", 
#         "📁 Document Conversion"
#     ])

#     with tab1:  # Content Generation Tab
#         st.header("Curriculum Content Generation Workflow")
        
#         # Step 1: Scheme of Work Generation
#         with st.expander("1. Create Scheme of Work", expanded=True):
#             st.markdown("### Scheme of Work Parameters")
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 subject = st.selectbox("Subject", ["Civic Education", "Social Studies", "Security Education"])
#             with col2:
#                 grade_level = st.selectbox("Grade Level", ["Primary One", "Primary Two", "Primary Three"])
#             with col3:
#                 topic = st.text_input("Topic", "National Consciousness")

#             if st.button("Generate Scheme of Work"):
#                 payload = {
#                     "subject": subject,
#                     "grade_level": grade_level,
#                     "topic": topic
#                 }
#                 st.session_state.base_params = payload  # Store base parameters
                
#                 try:
#                     response = requests.post(
#                         f"{API_BASE_URL}/api/content/scheme-of-work",
#                         json=payload
#                     )
#                     if response.status_code == 200:
#                         result = response.json()
#                         st.session_state.scheme_id = result['scheme_of_work_id']
#                         st.success("Scheme generated successfully!")
#                         st.markdown(f"**Generated Scheme ID:** `{st.session_state.scheme_id}`")
#                         st.markdown("### Scheme Content")
#                         st.markdown(result['scheme_of_work_output'])
#                     else:
#                         st.error(f"Error generating scheme: {response.json().get('detail', 'Unknown error')}")
#                 except Exception as e:
#                     st.error(f"API Connection Error: {str(e)}")

#         # Step 2: Lesson Plan Generation
#         with st.expander("2. Create Lesson Plan", expanded=st.session_state.scheme_id is not None):
#             if st.session_state.scheme_id:
#                 st.markdown("### Teaching Constraints")
#                 limitations = st.text_area("What challenges are you facing? (e.g., limited resources, large class size)",
#                 "Large class size (60 students), Limited textbooks (5 copies), No projector")
#                 # Get parameters from session state instead of new inputs
#                 duration = st.text_input("Lesson Duration (minutes)", "40")
#                 objectives = st.text_area("Learning Objectives", 
#                     "All will: [Basic objective]\nMost will: [Intermediate objective]\nSome will: [Advanced objective]")
                
#                 if st.button("Generate Adaptive Lesson Plan"):
#                     payload = {
#                         "scheme_of_work_id": st.session_state.scheme_id,
#                         "limitations": limitations,
#                         **st.session_state.base_params  # Include subject, grade_level, topic
#                     }
                    
#                     try:
#                         response = requests.post(
#                             f"{API_BASE_URL}/api/content/lesson-plan",
#                             json=payload
#                         )
#                         if response.status_code == 200:
#                             result = response.json()
#                             st.session_state.lesson_plan_id = result['lesson_plan_id']
#                             st.success("Lesson plan generated successfully!")
#                             st.markdown(f"**Lesson Plan ID:** `{st.session_state.lesson_plan_id}`")
#                             st.markdown("### Lesson Plan Content")
#                             st.markdown(result['lesson_plan_output'])
#                         else:
#                             st.error(f"Error generating lesson plan: {response.json().get('detail', 'Unknown error')}")
#                     except Exception as e:
#                         st.error(f"API Connection Error: {str(e)}")
#             else:
#                 st.warning("Please generate a Scheme of Work first")

#         # Step 3: Lesson Notes Generation
#         with st.expander("3. Create Lesson Notes", expanded=st.session_state.lesson_plan_id is not None):
#             if st.session_state.lesson_plan_id and st.session_state.scheme_id:
#                 st.markdown("### Lesson Notes Parameters")
#                 teaching_method = st.selectbox("Teaching Method", ["Demonstration", "Discussion", "Activity-Based"])
                
#                 if st.button("Generate Lesson Notes"):
#                     payload = {
#                         "scheme_of_work_id": st.session_state.scheme_id,
#                         "lesson_plan_id": st.session_state.lesson_plan_id,
#                         "teaching_method": teaching_method,
#                         **st.session_state.base_params  # Include subject, grade_level, topic
#                     }
                    
#                     try:
#                         response = requests.post(
#                             f"{API_BASE_URL}/api/content/lesson-notes",
#                             json=payload
#                         )
#                         if response.status_code == 200:
#                             result = response.json()
#                             st.session_state.lesson_notes_id = result['lesson_notes_id']
#                             st.success("Lesson notes generated successfully!")
#                             st.markdown(f"**Lesson Notes ID:** `{st.session_state.lesson_notes_id}`")
#                             st.markdown("### Lesson Notes Content")
#                             st.markdown(result['content'])
#                         else:
#                             st.error(f"Error generating notes: {response.json().get('detail', 'Unknown error')}")
#                     except Exception as e:
#                         st.error(f"API Connection Error: {str(e)}")
#             else:
#                 st.warning("Please generate a Lesson Plan first")

#     with tab2:  # PDF Processing Tab
#         st.header("PDF Processing and Vectorization")
#         uploaded_file = st.file_uploader("Upload Curriculum PDF", type="pdf")
        
#         if uploaded_file:
#             # Use temporary file with auto-cleanup
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
#                 temp_file.write(uploaded_file.getbuffer())
#                 temp_path = temp_file.name

#             if st.button("Process PDF"):
#                 try:
#                     with open(temp_path, "rb") as f:
#                         files = {"file": (uploaded_file.name, f, "application/pdf")}
#                         response = requests.post(
#                             f"{API_BASE_URL}/api/embeddings/process_pdf",
#                             files=files
#                         )
                    
#                     if response.status_code == 200:
#                         st.success("PDF processed and stored in vector database!")
#                         st.json(response.json())
#                     else:
#                         st.error(f"Processing failed: {response.json().get('detail', 'Unknown error')}")
#                 except Exception as e:
#                     st.error(f"Processing error: {str(e)}")
#                 finally:
#                     os.unlink(temp_path)  # Ensure file cleanup

#     with tab3:  # Document Conversion Tab
#         st.header("Document Format Conversion")
        
#         # Create a 2-column layout
#         col1, col2 = st.columns([3, 2])
        
#         with col1:
#             st.subheader("Conversion Parameters")
#             content_type = st.selectbox("Select Content Type", [
#                 "Scheme of Work",
#                 "Lesson Plan", 
#                 "Lesson Notes"
#             ])
            
#             # Get ID from session state based on content type
#             content_id = None
#             if content_type == "Scheme of Work":
#                 content_id = st.session_state.get("scheme_id")
#             elif content_type == "Lesson Plan":
#                 content_id = st.session_state.get("lesson_plan_id")
#             else:
#                 content_id = st.session_state.get("lesson_notes_id")
            
#             # Display document ID
#             if content_id:
#                 st.markdown(f"**Document ID:** `{content_id}`")
#             else:
#                 st.warning(f"No {content_type} generated yet - create one in the Content Generation tab")
            
#             custom_name = st.text_input("Custom Filename (optional)", key="custom_name_input")
        
#         with col2:
#             st.subheader("Conversion Status")
#             status_placeholder = st.empty()
#             download_placeholder = st.empty()
        
#         if st.button("✨ Convert to DOCX", use_container_width=True, key="convert_btn"):
#             if not content_id:
#                 status_placeholder.warning("⚠️ Please generate the selected document type first")
#                 return
                
#             try:
#                 # Conversion configuration mapping
#                 conversion_config = {
#                     "Scheme of Work": {
#                         "content_type": "scheme",
#                         "id_field": "scheme_of_work_id"
#                     },
#                     "Lesson Plan": {
#                         "content_type": "lesson_plan",
#                         "id_field": "lesson_plan_id"
#                     },
#                     "Lesson Notes": {
#                         "content_type": "lesson_notes",
#                         "id_field": "lesson_notes_id"
#                     }
#                 }
                
#                 config = conversion_config[content_type]
#                 payload = {
#                     "content_type": config["content_type"],
#                     "custom_filename": custom_name or None,
#                     config["id_field"]: content_id
#                 }
                
#                 # Show loading spinner
#                 with st.spinner("🔄 Converting document..."):
#                     response = requests.post(
#                         f"{API_BASE_URL}/api/convert/generate-document",
#                         json=payload,
#                         stream=True  # Important for file downloads
#                     )

#                 # Handle response
#                 if response.status_code == 200:
#                     # Get filename from headers
#                     content_disposition = response.headers.get("Content-Disposition")
#                     filename = "document.docx"
#                     if content_disposition:
#                         filename = content_disposition.split("filename=")[-1].strip('"')
                    
#                     # Create temporary file
#                     with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
#                         tmp_file.write(response.content)
#                         tmp_path = tmp_file.name
                    
#                     # Show success and auto-download
#                     status_placeholder.success("✅ Conversion successful!")
                    
#                     # Auto-download logic
#                     with open(tmp_path, "rb") as file:
#                         download_placeholder.download_button(
#                             label="⬇️ Download Document",
#                             data=file,
#                             file_name=filename,
#                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#                         )
                    
#                     # Cleanup
#                     os.unlink(tmp_path)

#                 else:
#                     error_detail = response.text  # Get raw error message
#                     status_placeholder.error(f"❌ Conversion failed: {error_detail}")
                    
#             except Exception as e:
#                 status_placeholder.error(f"⚠️ Error during conversion: {str(e)}")


# if __name__ == "__main__":
#     main()


# streamlit_app.py (final working version)
import streamlit as st
import requests
import tempfile
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"  # Update if deployed

def main():
    st.title("AI-Teacher's Content Assistant")
    st.markdown("**Nigerian Educational Content Generation System**")

    # Initialize session state with persistent content storage
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = {
            'scheme': None,
            'lesson_plan': None,
            'lesson_notes': None
        }

    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs([
        "📚 Content Generation", 
        "📄 PDF Processing", 
        "📁 Document Conversion"
    ])

    with tab1:  # Content Generation Tab
        st.header("Curriculum Content Generation Workflow")
        
        # Step 1: Scheme of Work
        with st.expander("1. Create Scheme of Work", expanded=True):
            if st.session_state.generated_content['scheme']:
                st.markdown("### Existing Scheme of Work")
                st.markdown(f"**ID:** `{st.session_state.generated_content['scheme']['id']}`")
                st.markdown(st.session_state.generated_content['scheme']['content'])
                
                if st.button("Generate New Scheme"):
                    st.session_state.generated_content = {
                        'scheme': None,
                        'lesson_plan': None,
                        'lesson_notes': None
                    }
                    st.rerun()
            else:
                show_scheme_creation_ui()

        # Step 2: Lesson Plan
        with st.expander("2. Create Lesson Plan", 
                       expanded=st.session_state.generated_content['scheme'] is not None):
            if st.session_state.generated_content['lesson_plan']:
                st.markdown("### Existing Lesson Plan")
                st.markdown(f"**ID:** `{st.session_state.generated_content['lesson_plan']['id']}`")
                st.markdown(st.session_state.generated_content['lesson_plan']['content'])
                
                if st.button("Generate New Lesson Plan"):
                    st.session_state.generated_content['lesson_plan'] = None
                    st.session_state.generated_content['lesson_notes'] = None
                    st.rerun()
            elif st.session_state.generated_content['scheme']:
                show_lesson_plan_creation_ui()
            else:
                st.warning("Please generate a Scheme of Work first")

        # Step 3: Lesson Notes
        with st.expander("3. Create Lesson Notes", 
                        expanded=st.session_state.generated_content['lesson_plan'] is not None):
            if st.session_state.generated_content['lesson_notes']:
                st.markdown("### Existing Lesson Notes")
                st.markdown(f"**ID:** `{st.session_state.generated_content['lesson_notes']['id']}`")
                st.markdown(st.session_state.generated_content['lesson_notes']['content'])
                
                if st.button("Generate New Lesson Notes"):
                    st.session_state.generated_content['lesson_notes'] = None
                    st.rerun()
            elif st.session_state.generated_content['lesson_plan']:
                show_lesson_notes_creation_ui()
            else:
                st.warning("Please generate a Lesson Plan first")

    with tab2:  # PDF Processing Tab
        st.header("PDF Processing and Vectorization")
        uploaded_file = st.file_uploader("Upload Curriculum PDF", type="pdf")
        
        if uploaded_file:
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
                    os.unlink(temp_path)

    with tab3:  # Document Conversion Tab
        st.header("Document Format Conversion")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Conversion Parameters")
            content_type = st.selectbox("Select Content Type", [
                "Scheme of Work",
                "Lesson Plan", 
                "Lesson Notes"
            ])
            
            # Get ID from generated content based on content type
            content_id = None
            content_data = None
            
            if content_type == "Scheme of Work":
                content_data = st.session_state.generated_content['scheme']
            elif content_type == "Lesson Plan":
                content_data = st.session_state.generated_content['lesson_plan']
            else:
                content_data = st.session_state.generated_content['lesson_notes']
            
            if content_data:
                content_id = content_data['id']
                st.markdown(f"**Document ID:** `{content_id}`")
            else:
                st.warning(f"No {content_type} generated yet - create one in the Content Generation tab")
            
            custom_name = st.text_input("Custom Filename (optional)", key="custom_name_input")
        
        with col2:
            st.subheader("Conversion Status")
            status_placeholder = st.empty()
            download_placeholder = st.empty()
        
        if st.button("✨ Convert to DOCX", use_container_width=True, key="convert_btn"):
            if not content_id:
                status_placeholder.warning("⚠️ Please generate the selected document type first")
                return
                
            try:
                conversion_config = {
                    "Scheme of Work": {
                        "content_type": "scheme",
                        "id_field": "scheme_of_work_id"
                    },
                    "Lesson Plan": {
                        "content_type": "lesson_plan",
                        "id_field": "lesson_plan_id"
                    },
                    "Lesson Notes": {
                        "content_type": "lesson_notes",
                        "id_field": "lesson_notes_id"
                    }
                }
                
                config = conversion_config[content_type]
                payload = {
                    "content_type": config["content_type"],
                    "custom_filename": custom_name or None,
                    config["id_field"]: content_id
                }
                
                with st.spinner("🔄 Converting document..."):
                    response = requests.post(
                        f"{API_BASE_URL}/api/convert/generate-document",
                        json=payload,
                        stream=True
                    )

                if response.status_code == 200:
                    content_disposition = response.headers.get("Content-Disposition")
                    filename = "document.docx"
                    if content_disposition:
                        filename = content_disposition.split("filename=")[-1].strip('"')
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                        tmp_file.write(response.content)
                        tmp_path = tmp_file.name
                    
                    status_placeholder.success("✅ Conversion successful!")
                    
                    with open(tmp_path, "rb") as file:
                        download_placeholder.download_button(
                            label="⬇️ Download Document",
                            data=file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    os.unlink(tmp_path)

                else:
                    error_detail = response.text
                    status_placeholder.error(f"❌ Conversion failed: {error_detail}")
                    
            except Exception as e:
                status_placeholder.error(f"⚠️ Error during conversion: {str(e)}")

def show_scheme_creation_ui():
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
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/content/scheme-of-work",
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.generated_content['scheme'] = {
                    'id': result['scheme_of_work_id'],
                    'content': result['scheme_of_work_output']
                }
                st.rerun()
            else:
                st.error(f"Error generating scheme: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"API Connection Error: {str(e)}")

def show_lesson_plan_creation_ui():
    st.markdown("### Teaching Constraints")
    scheme = st.session_state.generated_content['scheme']
    
    # Add more structured constraint inputs
    with st.container(border=True):
        st.markdown("**Class Challenges**")
        class_size = st.number_input("Number of Students", min_value=1, value=40)
        resources = st.multiselect("Available Resources", 
                                 ["Textbooks", "Whiteboard", "Projector", "Internet Access"])
        special_needs = st.text_area("Special Needs Considerations", 
                                   "Include any special learning needs in the class")
        time_constraints = st.slider("Available Time (minutes)", 20, 120, 40)
        
        constraints_text = f"""
        - Class size: {class_size} students
        - Available resources: {', '.join(resources) if resources else 'None'}
        - Special needs: {special_needs}
        - Available time: {time_constraints} minutes
        """

    limitations = st.text_area("Additional Constraints",
                             "Large class size (60 students), Limited textbooks (5 copies), No projector",
                             help="Describe specific teaching challenges you're facing")
    
    if st.button("Generate Adaptive Lesson Plan"):
        payload = {
            "scheme_of_work_id": scheme['id'],
            "limitations": f"{constraints_text}\n{limitations}",  # Combine structured and freeform constraints
            "subject": scheme.get('subject', ''),
            "grade_level": scheme.get('grade_level', ''),
            "topic": scheme.get('topic', ''),
            "time_constraints": time_constraints  # Pass specific constraint parameter
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/content/lesson-plan",
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.generated_content['lesson_plan'] = {
                    'id': result['lesson_plan_id'],
                    'content': result['lesson_plan_output']
                }
                st.rerun()
            else:
                st.error(f"Error generating lesson plan: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"API Connection Error: {str(e)}")

def show_lesson_notes_creation_ui():
    st.markdown("### Lesson Notes Parameters")
    teaching_method = st.selectbox("Teaching Method", ["Demonstration", "Discussion", "Activity-Based"])
    
    if st.button("Generate Lesson Notes"):
        scheme = st.session_state.generated_content['scheme']
        lesson_plan = st.session_state.generated_content['lesson_plan']
        
        payload = {
            "scheme_of_work_id": scheme['id'],
            "lesson_plan_id": lesson_plan['id'],
            "teaching_method": teaching_method,
            "subject": scheme.get('payload', {}).get('subject', ''),
            "grade_level": scheme.get('payload', {}).get('grade_level', ''),
            "topic": scheme.get('payload', {}).get('topic', '')
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/content/lesson-notes",
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.generated_content['lesson_notes'] = {
                    'id': result['lesson_notes_id'],
                    'content': result['content']
                }
                st.rerun()
            else:
                st.error(f"Error generating notes: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"API Connection Error: {str(e)}")

if __name__ == "__main__":
    main()