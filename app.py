import streamlit as st
from s3_client import get_s3_client, list_markdown_files, fetch_file_content, get_config

# Page configuration
st.set_page_config(
    page_title="S3 Markdown Viewer",
    page_icon="📄",
    layout="wide",
)

def main():
    st.title("📄 S3 Markdown Viewer")

    # Load configuration
    bucket_name = get_config("S3_BUCKET_NAME")
    
    if not bucket_name:
        st.error("S3_BUCKET_NAME is not set. Please check your .env file or Streamlit secrets.")
        return

    try:
        client = get_s3_client()
    except Exception as e:
        st.error(f"Failed to initialize S3 client: {e}")
        return

    # Sidebar: File List and Enhancements
    st.sidebar.title("📁 Explorer")
    
    # Enhancement: Refresh button
    if st.sidebar.button("🔄 Refresh List"):
        st.cache_data.clear()
        st.rerun()

    # Enhancement: Search box
    search_query = st.sidebar.text_input("🔍 Search files", "").lower()

    # Get file list
    all_files = list_markdown_files(client, bucket_name)
    
    if not all_files:
        st.sidebar.info("No Markdown files found.")
        st.info("No Markdown files found in the specified bucket.")
        return

    # Filter files based on search
    filtered_files = [f for f in all_files if search_query in f.lower()]
    total_filtered = len(filtered_files)

    # --- Pagination Logic ---
    st.sidebar.markdown("---")
    items_per_page = st.sidebar.selectbox("Items per page", [10, 20, 50, 100], index=1)
    
    total_pages = max(1, (total_filtered + items_per_page - 1) // items_per_page)
    
    # Use session state for page number to persist through selections
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    
    # Reset page if search changes or items_per_page changes
    if "last_search" not in st.session_state or st.session_state.last_search != search_query:
        st.session_state.current_page = 1
        st.session_state.last_search = search_query

    # Pagination controls
    col_prev, col_page, col_next = st.sidebar.columns([1, 2, 1])
    if col_prev.button("⬅️", disabled=st.session_state.current_page <= 1):
        st.session_state.current_page -= 1
        st.rerun()
    
    col_page.markdown(f"Page **{st.session_state.current_page}** of {total_pages}")
    
    if col_next.button("➡️", disabled=st.session_state.current_page >= total_pages):
        st.session_state.current_page += 1
        st.rerun()

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_files = filtered_files[start_idx:end_idx]

    # View Mode Toggle
    view_mode = st.sidebar.radio("View Mode", ["Folder Tree", "Flat List"], horizontal=True)

    if view_mode == "Folder Tree":
        # Group current page files by prefix
        tree = {}
        for f in page_files:
            parts = f.split("/")
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if "_files" not in current:
                current["_files"] = []
            current["_files"].append(f)

        def render_tree(nodes, depth=0):
            for folder, children in nodes.items():
                if folder == "_files":
                    continue
                with st.sidebar.expander(f"{'  ' * depth}📂 {folder}", expanded=True):
                    render_tree(children, depth + 1)
            
            if "_files" in nodes:
                for f in nodes["_files"]:
                    display_name = f.split("/")[-1]
                    # Highlight selected file
                    is_selected = st.session_state.get("selected_key") == f
                    btn_label = f"📍 {display_name}" if is_selected else f"📄 {display_name}"
                    if st.sidebar.button(btn_label, key=f"tree_{f}", use_container_width=True):
                        st.session_state.selected_key = f
                        st.rerun()

        render_tree(tree)
    else:
        # Flat List view
        for f in page_files:
            is_selected = st.session_state.get("selected_key") == f
            btn_label = f"📍 {f}" if is_selected else f"📄 {f}"
            if st.sidebar.button(btn_label, key=f"flat_{f}", use_container_width=True):
                st.session_state.selected_key = f
                st.rerun()

    # Initialize session state for selection
    if "selected_key" not in st.session_state:
        st.session_state.selected_key = None

    # Main area: Content Display
    if st.session_state.selected_key:
        selected_key = st.session_state.selected_key
        
        # Enhancement: Raw source toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Viewing: {selected_key}")
        with col2:
            show_raw = st.toggle("Show raw Markdown", value=False)

        with st.spinner(f"Fetching {selected_key}..."):
            content = fetch_file_content(client, bucket_name, selected_key)
        
        if content:
            if show_raw:
                st.code(content, language="markdown")
            else:
                # unsafe_allow_html=True as per plan for trusted sources
                st.markdown(content, unsafe_allow_html=True)
        else:
            st.warning("The selected file appears to be empty or could not be fetched.")
    else:
        st.info("👈 Select a file from the sidebar to view its content.")

if __name__ == "__main__":
    main()
