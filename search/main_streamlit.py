import os
import sys
import re
import importlib

import streamlit as st

# Ensure repo root is on sys.path so GuidedPrompt package can be imported
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GUIDEDPROMPT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if GUIDEDPROMPT_ROOT not in sys.path:
    sys.path.insert(0, GUIDEDPROMPT_ROOT)

# Remove any relative paths that might interfere
sys.path = [p for p in sys.path if not p.startswith('.')]

# Debug: print paths
print(f"REPO_ROOT: {REPO_ROOT}")
print(f"GUIDEDPROMPT_ROOT: {GUIDEDPROMPT_ROOT}")
print(f"sys.path cleaned: {[p for p in sys.path[:5]]}")

DB_MODULE = "GuidedPrompt.mysql.connection"

# Try importing directly with absolute path
try:
    import importlib.util
    connection_path = os.path.join(GUIDEDPROMPT_ROOT, "mysql", "connection.py")
    print(f"Trying to load connection from: {connection_path}")
    print(f"File exists: {os.path.exists(connection_path)}")
    spec = importlib.util.spec_from_file_location("connection_module", connection_path)
    db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_module)
    DB_IMPORT_SUCCESS = True
    print("✅ Connection module loaded successfully!")
except Exception as e:
    DB_IMPORT_SUCCESS = False
    print(f" Connection import has failed: {e}")
    st.error(f" Direct import has failed: {e}")

# Import AI integration
try:
    if DB_IMPORT_SUCCESS:
        # Try to import the AI integration using the same direct approach
        ai_path = os.path.join(GUIDEDPROMPT_ROOT, "mysql", "AI_intergration.py")
        print(f"Trying to load AI integration from: {ai_path}")
        print(f"AI file exists: {os.path.exists(ai_path)}")
        ai_spec = importlib.util.spec_from_file_location("ai_module", ai_path)
        ai_module = importlib.util.module_from_spec(ai_spec)
        ai_spec.loader.exec_module(ai_module)
        generate_summary = ai_module.generate_summary
        AI_AVAILABLE = True
        print("✅ AI module loaded successfully!")
    else:
        raise ImportError("DB module not available")
except ImportError as e:
    AI_AVAILABLE = False
    print(f"AI integration has failed: {e}")
    st.error(f" AI integration has failed: {e}")

st.title("GuidedPrompt ")

# Initialize session state
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'use_ai_summary' not in st.session_state:
    st.session_state.use_ai_summary = True
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Use a form to enable Enter key functionality
with st.form("search_form"):
    query = st.text_input("Enter a word or phrase to search for:", value=st.session_state.search_query)
    
    # Add AI summary toggle
    use_ai_summary = st.checkbox("Generate AI Summary", value=st.session_state.use_ai_summary) if AI_AVAILABLE else False
    
    if not AI_AVAILABLE:
        st.info("💡 Install google-generativeai for AI summaries: pip install google-generativeai")
    
    # This button will be triggered by Enter key or clicking
    search_button = st.form_submit_button("Find verses")

# Handle search button or if we have cached results to display
if search_button or (st.session_state.search_query and st.session_state.search_results):
    if search_button:
        # Reset page to 1 on new search
        st.session_state.current_page = 1
        q = query.strip()
        st.session_state.search_query = q
        st.session_state.use_ai_summary = use_ai_summary
    else:
        # Use cached search
        q = st.session_state.search_query
        use_ai_summary = st.session_state.use_ai_summary
    
    if not q:
        st.warning("Please enter a search word.")
    else:
        # Only perform search if it's a new search (search_button was clicked)
        if search_button:
            try:
                if DB_IMPORT_SUCCESS:
                    # Use the directly imported module
                    db = db_module
                else:
                    st.error("DB module is not available")
                    st.stop()
            except Exception as e:
                st.error(f"Could not use DB module: {e}")
                st.stop()
            else:
                # Prefer server-side structured search if available
                matches = []
                if hasattr(db, "search_verses_struct"):
                    try:
                        matches = db.search_verses_struct(q)
                    except Exception as e:
                        st.error(f"DB structured search failed: {e}")
                        matches = []
                else:
                    # Fallback: fetch all verses and filter client-side
                    fetch_fn = None
                    for name in ("get_all_verses", "get_scriptures", "get_verses", "get_all"):
                        if hasattr(db, name):
                            fetch_fn = getattr(db, name)
                            break
                    if fetch_fn is None:
                        st.error(f"DB module {DB_MODULE} has no suitable fetch function.")
                        matches = []
                    else:
                        try:
                            all_texts = fetch_fn()
                            normalized = []
                            for r in all_texts:
                                if isinstance(r, dict) and "text" in r:
                                    normalized.append(r)
                                elif isinstance(r, str):
                                    normalized.append({"text": r})
                                else:
                                    normalized.append({"text": str(r)})
                            word_re = re.compile(rf"(?<!\w){re.escape(q)}(?!\w)", re.IGNORECASE)
                            for item in normalized:
                                if word_re.search(item["text"]):
                                    matches.append({
                                        "text": item["text"],
                                        "book": item.get("book", ""),
                                        "chapter": item.get("chapter", ""),
                                        "verse": item.get("verse", "")
                                    })
                        except Exception as e:
                            st.error(f"Failed to fetch verses from DB: {e}")
                            matches = []

                # Store search results in session state
                st.session_state.search_results = matches

        # Use cached results for pagination
        matches = st.session_state.search_results

        # Deduplicate simple duplicates
        seen = set()
        dedup = []
        for m in matches:
            book = (m.get("book") or "").strip()
            chapter = str(m.get("chapter", "")).strip()
            verse = str(m.get("verse", "")).strip()
            text = (m.get("text") or "").strip()
            key = (book.lower(), chapter, verse, text)
            if key in seen:
                continue
            seen.add(key)
            dedup.append({"book": book, "chapter": chapter, "verse": verse, "text": text})
        matches = dedup

        # Generate AI Summary if requested
        if use_ai_summary and AI_AVAILABLE and matches:
            with st.spinner("Generating AI summary..."):
                summary = generate_summary(q, matches)
                st.markdown("## 🤖 AI Summary")
                st.markdown(summary)
                st.markdown(f"*Based on {len(matches)} scripture verses found*")
                st.markdown("---")

        # Pagination logic
        RESULTS_PER_PAGE = 50
        total_results = len(matches)
        
        if total_results > RESULTS_PER_PAGE:
                # Calculate pagination
                total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
                
                # Initialize session state for current page
                if 'current_page' not in st.session_state:
                    st.session_state.current_page = 1
                
                # Display pagination info
                st.markdown(f"**Showing results {((st.session_state.current_page - 1) * RESULTS_PER_PAGE) + 1}-{min(st.session_state.current_page * RESULTS_PER_PAGE, total_results)} of {total_results} total results**")
                
                # Pagination controls
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                
                with col1:
                    if st.button("« First", disabled=(st.session_state.current_page == 1)):
                        st.session_state.current_page = 1
                
                with col2:
                    if st.button("‹ Previous", disabled=(st.session_state.current_page == 1)):
                        st.session_state.current_page -= 1
                
                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 5px;'>Page {st.session_state.current_page} of {total_pages}</div>", unsafe_allow_html=True)
                
                with col4:
                    if st.button("Next ›", disabled=(st.session_state.current_page == total_pages)):
                        st.session_state.current_page += 1
                
                with col5:
                    if st.button("Last »", disabled=(st.session_state.current_page == total_pages)):
                        st.session_state.current_page = total_pages
                
                # Calculate slice for current page
                start_idx = (st.session_state.current_page - 1) * RESULTS_PER_PAGE
                end_idx = start_idx + RESULTS_PER_PAGE
                paginated_matches = matches[start_idx:end_idx]
                
                st.markdown("---")
        else:
            # If 50 or fewer results, show all
            paginated_matches = matches
            if total_results > 0:
                st.markdown(f"**Showing all {total_results} results**")

        # helper to categorize book into collection
        def categorize_book(name: str) -> str:
                n = (name or "").lower()
                if not n:
                    return "Unknown"
                # Explicit Articles of Faith collection (separate from POGP)
                if "articles of faith" in n:
                    return "Articles of Faith"
                # Book of Mormon keywords
                bom_keys = ("nephi", "second nephi","jacob", "enos", "jarom", "omni", "mosiah", "alma",
                            "helaman", "mormon", "third nephi", "fourth nephi",
                            "ether", "moroni", "words of mormon")
                for k in bom_keys:
                    if k in n:
                        return "Book of Mormon"
                # Doctrine and Covenants
                if "doctrine and covenants" in n or "d&c" in n or n.startswith("dc "):
                    return "Doctrine and Covenants"
                # Pearl of Great Price (exclude Articles of Faith)
                pogp_keys = ("moses", "abridgment", "abridg", "book of abraham", "joseph smith—history", "joseph smith-matthew")
                for k in pogp_keys:
                    if k in n:
                        return "Pearl of Great Price"
                # New Testament book names (map these to New Testament)
                nt_books = ("matthew","mark","luke","john","acts",
                            "romans","one corinthians","two corinthians","galatians","ephesians","philippians","colossians","one thessalonians","two thessalonians",
                            "one timothy","two  timothy","titus","philemon","hebrews","james","one peter","two peter","one john","two john","three john","jude","revelation")
                for k in nt_books:
                    if k in n:
                        return "New Testament"
                # Otherwise if it matches common Bible names, mark as Old Testament
                ot_keys = ("genesis","exodus","leviticus","numbers","deuteronomy","joshua","judges","ruth",
                              "one samuel","two samuel","one kings","two kings","one chronicles","two chronicles","ezra","nehemiah","esther","job","psalms",
                              "proverbs","ecclesiastes","song of solomon","isaiah","jeremiah","lamentations",
                              "ezekiel","daniel","hosea","joel","amos","obadiah","jonah","micah","nahum","habakkuk",
                              "zephaniah","haggai","zechariah","malachi")
                for k in ot_keys:
                    if k in n:
                        return "Old Testament"
                # fallback
                return "Other"

        # build collections dict (collection -> book -> [verses]) using paginated results
        collections = {}
        for m in paginated_matches:
                book = (m.get("book") or "").strip() or "Unknown"
                coll = categorize_book(book)
                collections.setdefault(coll, {}).setdefault(book, []).append(m)

        # sort collections in desired order with Old/New Testament first
        preferred_order = ["Old Testament", "New Testament", "Book of Mormon", "Doctrine and Covenants", "Pearl of Great Price", "Articles of Faith"]
        ordered_collections = sorted(collections.keys(), key=lambda x: (0 if x in preferred_order else 1,
                                                                        preferred_order.index(x) if x in preferred_order else 99,
                                                                        x.lower()))

        word_re = re.compile(rf"(?<!\w){re.escape(q)}(?!\w)", re.IGNORECASE)
        
        for coll in ordered_collections:
                st.markdown(f"**{coll}**")
                books = collections[coll]
                for book in sorted(books.keys(), key=lambda s: s.lower()):
                    # sort verses within book by chapter and verse (numeric when possible)
                    def to_int(v):
                        try:
                            return int(v)
                        except Exception:
                            m = re.match(r"\d+", str(v))
                            return int(m.group(0)) if m else 0
                    items = books[book]
                    items.sort(key=lambda x: (to_int(x.get("chapter", 0)), to_int(x.get("verse", 0))))
                    for m in items:
                        heading = f"**{book} {m.get('chapter', '')}:{m.get('verse', '')}**"
                        st.markdown(heading)
                        highlighted = word_re.sub(lambda mo: f'<mark style=\"background:black;color:red\">{mo.group(0)}</mark>', m["text"])
                        st.markdown(highlighted, unsafe_allow_html=True)
                    st.markdown("---")
        
        # Add pagination controls at bottom if more than 50 results
        if total_results > RESULTS_PER_PAGE:
            st.markdown("---")
            # Bottom pagination controls (duplicate for convenience)
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("« First ", key="first_bottom", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page = 1
            
            with col2:
                if st.button("‹ Previous ", key="prev_bottom", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page -= 1
                
            with col3:
                st.markdown(f"<div style='text-align: center; padding: 5px;'>Page {st.session_state.current_page} of {total_pages}</div>", unsafe_allow_html=True)
            
            with col4:
                if st.button("Next › ", key="next_bottom", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page += 1
            
            with col5:
                if st.button("Last » ", key="last_bottom", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page = total_pages