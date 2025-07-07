# streamlit_app.py (with evaluation features)
import streamlit as st
import requests
import tempfile
import os
from datetime import datetime
import yaml
from src.education_ai_system.utils.validators import extract_weeks_from_scheme, extract_week_topic

# Configuration
API_BASE_URL = "http://localhost:8001"  # Update if deployed

def main():
    st.title("AI-Teacher's Content Assistant")
    st.markdown("**Nigerian Educational Content Generation System**")

    # Initialize session state with persistent content and evaluation storage
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = {
            'scheme': {'content': None, 'evaluation': None},
            'lesson_plan': {'content': None, 'evaluation': None},
            'lesson_notes': {'content': None, 'evaluation': None}
        }

    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Content Generation", 
        "📄 PDF Processing", 
        "📁 Document Conversion",
        "📊 Evaluation Details"  # New evaluation tab
    ])

    with tab1:  # Content Generation Tab
        st.header("Curriculum Content Generation Workflow")
        
        # Step 1: Scheme of Work
        with st.expander("1. Create Scheme of Work", expanded=True):
            if st.session_state.generated_content['scheme']['content']:
                st.markdown("### Existing Scheme of Work")
                st.markdown(f"**ID:** `{st.session_state.generated_content['scheme']['content']['id']}`")
                st.markdown(st.session_state.generated_content['scheme']['content']['content'])
                
                # Show evaluation summary
                show_evaluation_summary(st.session_state.generated_content['scheme']['evaluation'], "scheme_of_work")
                
                if st.button("Generate New Scheme"):
                    st.session_state.generated_content = {
                        'scheme': {'content': None, 'evaluation': None},
                        'lesson_plan': {'content': None, 'evaluation': None},
                        'lesson_notes': {'content': None, 'evaluation': None}
                    }
                    st.rerun()
            else:
                show_scheme_creation_ui()

        # Step 2: Lesson Plan
        with st.expander("2. Create Lesson Plan", 
                       expanded=st.session_state.generated_content['scheme']['content'] is not None):
            if st.session_state.generated_content['lesson_plan']['content']:
                st.markdown("### Existing Lesson Plan")
                st.markdown(f"**ID:** `{st.session_state.generated_content['lesson_plan']['content']['id']}`")
                st.markdown(st.session_state.generated_content['lesson_plan']['content']['content'])
                
                # Show evaluation summary
                show_evaluation_summary(st.session_state.generated_content['lesson_plan']['evaluation'], "lesson_plan")
                
                if st.button("Generate New Lesson Plan"):
                    st.session_state.generated_content['lesson_plan'] = {'content': None, 'evaluation': None}
                    st.session_state.generated_content['lesson_notes'] = {'content': None, 'evaluation': None}
                    st.rerun()
            elif st.session_state.generated_content['scheme']['content']:
                show_lesson_plan_creation_ui()
            else:
                st.warning("Please generate a Scheme of Work first")

        # Step 3: Lesson Notes
        with st.expander("3. Create Lesson Notes", 
                        expanded=st.session_state.generated_content['lesson_plan']['content'] is not None):
            if st.session_state.generated_content['lesson_notes']['content']:
                st.markdown("### Existing Lesson Notes")
                st.markdown(f"**ID:** `{st.session_state.generated_content['lesson_notes']['content']['id']}`")
                st.markdown(st.session_state.generated_content['lesson_notes']['content']['content'])
                
                # Show evaluation summary
                show_evaluation_summary(st.session_state.generated_content['lesson_notes']['evaluation'], "lesson_notes")
                
                if st.button("Generate New Lesson Notes"):
                    st.session_state.generated_content['lesson_notes'] = {'content': None, 'evaluation': None}
                    st.rerun()
            elif st.session_state.generated_content['lesson_plan']['content']:
                show_lesson_notes_creation_ui()
            else:
                st.warning("Please generate a Lesson Plan first")

    with tab2:  # PDF Processing Tab
        st.header("PDF Processing and Vectorization")
        uploaded_files = st.file_uploader(
            "Upload Curriculum PDFs", 
            type="pdf", 
            accept_multiple_files=True  # Enable multiple file uploads
        )
        
        if uploaded_files:
            # Create a temporary directory to store all files
            with tempfile.TemporaryDirectory() as temp_dir:
                processed_files = []
                processing_status = {}
                
                if st.button("Process All PDFs"):
                    progress_bar = st.progress(0)
                    status_container = st.container()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        try:
                            # Save file to temp directory
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Display processing status
                            status_container.write(f"Processing {uploaded_file.name}...")
                            
                            # Send file to API
                            with open(file_path, "rb") as f:
                                files = {"file": (uploaded_file.name, f, "application/pdf")}
                                response = requests.post(
                                    f"{API_BASE_URL}/api/embeddings/process_pdf",
                                    files=files
                                )
                            
                            # Update progress
                            progress = (i + 1) / len(uploaded_files)
                            progress_bar.progress(progress)
                            
                            if response.status_code == 200:
                                result = response.json()
                                processing_status[uploaded_file.name] = {
                                    "status": "success",
                                    "details": f"Processed {result.get('num_pages', 0)} pages"
                                }
                                processed_files.append(uploaded_file.name)
                            else:
                                error = response.json().get('detail', 'Unknown error')
                                processing_status[uploaded_file.name] = {
                                    "status": "error",
                                    "details": f"Failed: {error}"
                                }
                        except Exception as e:
                            processing_status[uploaded_file.name] = {
                                "status": "error",
                                "details": f"Processing error: {str(e)}"
                            }
                    
                    # Display results
                    status_container.empty()
                    st.success(f"Processed {len(processed_files)}/{len(uploaded_files)} files successfully!")
                    
                    # Show detailed status table
                    st.subheader("Processing Results")
                    status_table = "<table><tr><th>File</th><th>Status</th><th>Details</th></tr>"
                    for file, status in processing_status.items():
                        color = "green" if status["status"] == "success" else "red"
                        status_table += f"""
                            <tr>
                                <td>{file}</td>
                                <td style='color:{color}'>{status["status"].capitalize()}</td>
                                <td>{status["details"]}</td>
                            </tr>
                        """
                    status_table += "</table>"
                    st.markdown(status_table, unsafe_allow_html=True)
                    
                    # Show summary if successful
                    if processed_files:
                        st.json({"processed_files": processed_files})

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
                content_data = st.session_state.generated_content['scheme']['content']
            elif content_type == "Lesson Plan":
                content_data = st.session_state.generated_content['lesson_plan']['content']
            else:
                content_data = st.session_state.generated_content['lesson_notes']['content']
            
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
                
    with tab4:  # Evaluation Details Tab
        st.header("Detailed Content Evaluation")
        
        eval_options = ["Scheme of Work", "Lesson Plan", "Lesson Notes"]
        selected_content = st.selectbox("Select Content to Evaluate", eval_options)
        
        content_map = {
            "Scheme of Work": "scheme",
            "Lesson Plan": "lesson_plan",
            "Lesson Notes": "lesson_notes"
        }
        
        content_key = content_map[selected_content]
        content_data = st.session_state.generated_content[content_key]
        
        if content_data['evaluation']:
            eval_data = content_data['evaluation']
            
            if 'accuracy' in eval_data:
                st.subheader("Accuracy Metrics")
                cols = st.columns(5)
                metrics = [
                    ("Curriculum Compliance", "curriculum_compliance"),
                    ("Topic Relevance", "topic_relevance"),
                    ("Content Consistency", "content_consistency"),
                    ("Quality/Readability", "quality_readability"),
                    ("Cultural Relevance", "cultural_relevance")
                ]
                
                for i, (label, key) in enumerate(metrics):
                    with cols[i]:
                        score = eval_data['accuracy'][key]['score']
                        st.metric(label, f"{score}/5")
                        st.caption(eval_data['accuracy'][key]['reason'])
                
                st.subheader("Bias Assessment")
                bias_score = eval_data['bias']['score']
                st.metric("Bias Score", f"{bias_score}/5")
                st.caption(eval_data['bias']['reason'])
                
                st.subheader("Overall Evaluation")
                st.metric("Overall Accuracy", f"{eval_data['overall_accuracy']:.1f}/5.0")
                
                # Visualization
                scores = [m[1] for m in metrics]
                values = [eval_data['accuracy'][key]['score'] for key in scores]
                values.append(bias_score)
                
                chart_data = {
                    "Metric": [m[0] for m in metrics] + ["Bias"],
                    "Score": values
                }
                
                st.bar_chart(chart_data, x="Metric", y="Score")
            else:
                st.warning("Detailed evaluation data not available")
        else:
            st.warning("No evaluation data available. Generate content first.")

def show_scheme_creation_ui():
    # Load predefined inputs from YAML
    with open("src/education_ai_system/config/predefined_input.yaml", "r") as file:
        predefined_data = yaml.safe_load(file)
    
    st.markdown("### Scheme of Work Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get subject options from YAML
        subject_options = [subject["name"] for subject in predefined_data["subjects"]]
        subject = st.selectbox("Subject", subject_options)
    
    with col2:
        # Find the selected subject
        selected_subject = next(
            (s for s in predefined_data["subjects"] if s["name"] == subject), 
            None
        )
        
        if selected_subject:
            # Get grade levels based on selected subject
            grade_options = [grade["name"] for grade in selected_subject["grade_levels"]]
            grade_level = st.selectbox("Grade Level", grade_options)
        else:
            grade_level = st.selectbox("Grade Level", [])
    
    with col3:
        if selected_subject and grade_level:
            # Find the selected grade level
            selected_grade = next(
                (g for g in selected_subject["grade_levels"] if g["name"] == grade_level), 
                None
            )
            
            if selected_grade:
                # Get topics - handle both 'topics' and 'topic' keys
                if "topics" in selected_grade:
                    topic_options = selected_grade["topics"]
                elif "topic" in selected_grade:
                    # Handle singular 'topic' key (like in Primary Five)
                    topic_options = selected_grade["topic"]
                else:
                    topic_options = []
                    
                topic = st.selectbox("Topic", topic_options)
            else:
                topic = st.selectbox("Topic", [])
        else:
            topic = st.selectbox("Topic", [])
    
    if st.button("Generate Scheme of Work"):
        payload = {
            "subject": subject,
            "grade_level": grade_level,
            "topic": topic
        }
        
        try:
            with st.spinner("Generating scheme of work..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/content/scheme-of-work",
                    json=payload
                )
                
            if response.status_code == 200:
                result = response.json()
                st.session_state.generated_content['scheme']['content'] = {
                    'id': result['scheme_of_work_id'],
                    'content': result['scheme_of_work_output'],
                    'context_id': result['context_id']  # Store context ID
                }
                
                # Evaluate the generated content using context ID
                evaluation_payload = {"context_id": result['context_id']}
                
                with st.spinner("Evaluating content against curriculum standards..."):
                    try:
                        eval_response = requests.post(
                            f"{API_BASE_URL}/api/evaluate/scheme",
                            json={"context_id": result['context_id']},
                            timeout=120
                        )
                        
                        if eval_response.status_code == 200:
                            eval_data = eval_response.json()
                            
                            if eval_data.get('status') == 'error':
                                # Show detailed error message
                                error_details = (
                                    f"Evaluation failed: {eval_data.get('message', 'Unknown error')}\n\n"
                                    f"Context ID: {eval_data.get('context_id', '')}\n"
                                    f"Scheme ID: {eval_data.get('scheme_id', '')}"
                                )
                                st.error(error_details)
                            else:
                                st.session_state.generated_content['scheme']['evaluation'] = eval_data
                        else:
                            st.error(f"Evaluation request failed: HTTP {eval_response.status_code}")
                            
                    except Exception as e:
                        st.error(f"Evaluation request exception: {str(e)}")

                        st.error(error_msg)
                        print(error_msg)
                
                st.rerun()
            else:
                st.error(f"Error generating scheme: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"API Connection Error: {str(e)}")

def show_lesson_plan_creation_ui():
    st.markdown("### Teaching Constraints")
    
    # Initialize selected_week with default value
    selected_week = "1"
    
    # Only try to extract weeks if scheme content exists
    if st.session_state.generated_content['scheme']['content']:
        scheme_content = st.session_state.generated_content['scheme']['content']['content']
        weeks = extract_weeks_from_scheme(scheme_content)
        
        # Ensure we have valid weeks before showing selector
        if weeks:
            selected_week = st.selectbox("Select Week", weeks)
        else:
            st.warning("No weeks found in scheme. Using week 1 by default")
    else:
        st.warning("No scheme content available. Using week 1 by default")
    
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
        scheme = st.session_state.generated_content['scheme']['content']
        scheme_payload = scheme.get('payload', {})
        
        # Get the week-specific topic
        week_topic = "General Topic"
        if st.session_state.generated_content['scheme']['content']:
            scheme_content = st.session_state.generated_content['scheme']['content']['content']
            week_topic = extract_week_topic(scheme_content, selected_week)
        
        payload = {
            "scheme_of_work_id": scheme['id'],
            "limitations": f"{constraints_text}\n{limitations}",
            # Use week-specific topic instead of scheme-wide topic
            "subject": scheme_payload.get('subject', ''),
            "grade_level": scheme_payload.get('grade_level', ''),
            "topic": week_topic,  # Use the week-specific topic here
            "week": selected_week
        }
        
        try:
            with st.spinner("Generating lesson plan..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/content/lesson-plan",
                    json=payload
                )
                
            if response.status_code == 200:
                result = response.json()
                content_data = {
                    'id': result['lesson_plan_id'],
                    'content': result['lesson_plan_output'],
                    'week': selected_week
                }
                
                # Safely get context_id (fallback to None)
                context_id = result.get('context_id')
                content_data['context_id'] = context_id
                
                st.session_state.generated_content['lesson_plan']['content'] = content_data
                
                # Evaluate the generated content using lesson plan ID
                evaluation_payload = {"lesson_plan_id": content_data['id']}  # Changed to use ID
                
                try:
                    with st.spinner("Evaluating lesson plan..."):
                        eval_response = requests.post(
                            f"{API_BASE_URL}/api/evaluate/lesson_plan",
                            json=evaluation_payload,
                            timeout=120  # Increase timeout for evaluation
                        )
                        
                    if eval_response.status_code == 200:
                        eval_data = eval_response.json()
                        
                        # Check if evaluation was successful
                        if eval_data.get('status') == 'success':
                            st.session_state.generated_content['lesson_plan']['evaluation'] = eval_data
                        else:
                            st.warning(f"Evaluation completed but returned status: {eval_data.get('status')}")
                            st.session_state.generated_content['lesson_plan']['evaluation'] = {
                                'status': 'error',
                                'message': eval_data.get('message', 'Unknown evaluation error')
                            }
                    else:
                        error_msg = f"Evaluation failed with status {eval_response.status_code}: {eval_response.text}"
                        st.error(error_msg)
                        st.session_state.generated_content['lesson_plan']['evaluation'] = {
                            'status': 'error',
                            'message': error_msg
                        }
                except Exception as eval_error:
                    error_msg = f"Evaluation request failed: {str(eval_error)}"
                    st.error(error_msg)
                    st.session_state.generated_content['lesson_plan']['evaluation'] = {
                        'status': 'error',
                        'message': error_msg
                    }
                
                st.rerun()
            else:
                error_msg = f"Error generating lesson plan: {response.json().get('detail', 'Unknown error')}"
                st.error(error_msg)
                # Store error in evaluation field for visibility
                st.session_state.generated_content['lesson_plan']['evaluation'] = {
                    'status': 'error',
                    'message': error_msg
                }
        except Exception as e:
            error_msg = f"API Connection Error: {str(e)}"
            st.error(error_msg)
            st.session_state.generated_content['lesson_plan']['evaluation'] = {
                'status': 'error',
                'message': error_msg
            }

def show_lesson_notes_creation_ui():
    st.markdown("### Lesson Notes Parameters")
    teaching_method = st.selectbox("Teaching Method", ["Demonstration", "Discussion", "Activity-Based"])
    
    # Initialize selected_week with default value
    selected_week = "1"
    
    if st.session_state.generated_content['scheme']['content']:
        scheme_content = st.session_state.generated_content['scheme']['content']['content']
        weeks = extract_weeks_from_scheme(scheme_content)
        
        # Ensure we have valid weeks before showing selector
        if weeks:
            selected_week = st.selectbox("Select Week", weeks)
        else:
            st.warning("No weeks found in scheme. Using week 1 by default")
    else:
        st.warning("No scheme content available. Using week 1 by default")
    
    if st.button("Generate Lesson Notes"):
        scheme = st.session_state.generated_content['scheme']['content']
        lesson_plan = st.session_state.generated_content['lesson_plan']['content']
        
        # Get the week-specific topic
        week_topic = "General Topic"
        if st.session_state.generated_content['scheme']['content']:
            scheme_content = st.session_state.generated_content['scheme']['content']['content']
            week_topic = extract_week_topic(scheme_content, selected_week)
        
        payload = {
            "scheme_of_work_id": scheme['id'],
            "lesson_plan_id": lesson_plan['id'],
            "teaching_method": teaching_method,
            "subject": scheme.get('payload', {}).get('subject', ''),
            "grade_level": scheme.get('payload', {}).get('grade_level', ''),
            "topic": week_topic,
            "week": selected_week
        }
        
        try:
            with st.spinner("Generating lesson notes..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/content/lesson-notes",
                    json=payload
                )
                
            if response.status_code == 200:
                result = response.json()
                
                # Handle context_id safely
                content_data = {
                    'id': result['lesson_notes_id'],
                    'content': result['content'],
                    'week': selected_week
                }
                
                # Add context_id if available
                if 'context_id' in result:
                    content_data['context_id'] = result['context_id']
                
                st.session_state.generated_content['lesson_notes']['context_id'] = result['context_id']
                st.session_state.generated_content['lesson_notes']['content'] = content_data
                
                # Evaluate the generated content using lesson notes ID
                evaluation_payload = {"lesson_notes_id": content_data['id']}
                
                try:
                    with st.spinner("Evaluating lesson notes..."):
                        eval_response = requests.post(
                            f"{API_BASE_URL}/api/evaluate/lesson_notes",
                            json=evaluation_payload,
                            timeout=120
                        )
                    
                    if eval_response.status_code == 200:
                        eval_data = eval_response.json()
                        if eval_data.get('status') == 'success':
                            st.session_state.generated_content['lesson_notes']['evaluation'] = eval_data
                        else:
                            st.warning(f"Evaluation completed with status: {eval_data.get('status')}")
                            st.session_state.generated_content['lesson_notes']['evaluation'] = {
                                'status': 'error',
                                'message': eval_data.get('message', 'Unknown evaluation error')
                            }
                    else:
                        error_msg = f"Evaluation failed with status {eval_response.status_code}: {eval_response.text}"
                        st.error(error_msg)
                        st.session_state.generated_content['lesson_notes']['evaluation'] = {
                            'status': 'error',
                            'message': error_msg
                        }
                except Exception as e:
                    error_msg = f"Evaluation request failed: {str(e)}"
                    st.error(error_msg)
                    st.session_state.generated_content['lesson_notes']['evaluation'] = {
                        'status': 'error',
                        'message': error_msg
                    }
                
                st.rerun()
            else:
                error_msg = f"Error generating notes: {response.json().get('detail', 'Unknown error')}"
                st.error(error_msg)
                st.session_state.generated_content['lesson_notes']['evaluation'] = {
                    'status': 'error',
                    'message': error_msg
                }
        except Exception as e:
            error_msg = f"API Connection Error: {str(e)}"
            st.error(error_msg)
            st.session_state.generated_content['lesson_notes']['evaluation'] = {
                'status': 'error',
                'message': error_msg
            }

# UPDATED EVALUATION SUMMARY FUNCTION
def show_evaluation_summary(evaluation_data, content_type):
    if not evaluation_data:
        st.warning(f"No evaluation data available for {content_type}. Please generate content first.")
        return
        
    if evaluation_data.get('status') == 'error':
        st.warning(f"Evaluation failed: {evaluation_data.get('message', 'Unknown error')}")
        return

    # Display metrics
    st.subheader(f"{content_type.title()} Evaluation Metrics")
    accuracy = evaluation_data.get('overall_accuracy', 0)
    bias = evaluation_data.get('bias', {}).get('score', 0)
    
    col1, col2 = st.columns(2)
    col1.metric("Accuracy Score", f"{accuracy:.1f}/5.0")
    col2.metric("Bias Score", f"{bias:.1f}/5.0")
    
    # Detailed metrics
    with st.expander("Detailed Evaluation"):
        if 'accuracy' in evaluation_data:
            st.write("#### Accuracy Breakdown")
            for metric, details in evaluation_data['accuracy'].items():
                st.progress(details['score']/5, text=f"{metric.replace('_', ' ').title()}: {details['score']}/5")
                st.caption(details['reason'])
        
        if 'bias' in evaluation_data:
            st.write("#### Bias Assessment")
            st.write(evaluation_data['bias']['reason'])


if __name__ == "__main__":
    main()