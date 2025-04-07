import streamlit as st
import difflib
from bs4 import BeautifulSoup

def clean_diff_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove the default legend
    for table in soup.find_all("table", {"class": "diff", "summary": "Legends"}):
        table.decompose()

    # Remove anchor tags and leftover characters
    for anchor in soup.find_all("a"):
        anchor.unwrap()
    for td in soup.find_all("td", class_="diff_next"):
        td.string = ""

    # Custom color legend
    legend = BeautifulSoup("""
    <div class="legend">
        <p>Legend:</p>
        <span class="legend-item added">Added</span>
        <span class="legend-item deleted">Deleted</span>
        <span class="legend-item changed">Changed</span>
    </div>
    """, "html.parser")

    first_table = soup.find("table", class_="diff")
    if first_table:
        first_table.insert_before(legend)

    # Inject future-proof CSS with dark/light mode support
    style = BeautifulSoup("""
    <style>
        body {
            background-color: transparent;
            font-family: sans-serif;
            color: black;
        }
        table.diff {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
        }
        .diff_header {
            background-color: #f2f2f2;
            font-weight: bold;
            padding: 6px;
        }
        td, th {
            padding: 6px;
            border: 1px solid #ccc;
        }
        td.diff_add {
            background-color: #c8facc !important;
        }
        td.diff_sub {
            background-color: #f9cbcb !important;
        }
        td.diff_chg {
            background-color: #fcf6b1 !important;
        }

        .legend {
            margin-bottom: 20px;
        }
        .legend-item {
            display: inline-block;
            padding: 5px 10px;
            margin-right: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .added { background-color: #c8facc; }
        .deleted { background-color: #f9cbcb; }
        .changed { background-color: #fcf6b1; }

        /* Future-proof theme styles */
        .legend > p {
            font-weight: bold;
            margin-bottom: 5px;
        }

        @media (prefers-color-scheme: dark) {
            .legend > p {
                color: white;
            }
        }

        @media (prefers-color-scheme: light) {
            .legend > p {
                color: black;
            }
        }
    </style>
    """, "html.parser")

    soup.head.insert(len(soup.head.contents), style)
    return str(soup)

def calculate_diff_percentage(left: str, right: str) -> float:
    matcher = difflib.SequenceMatcher(None, left, right)
    similarity = matcher.ratio()
    return round((1 - similarity) * 100, 2)

def main():
    st.set_page_config(layout="wide")
    st.title("MCI - Code Comparison Tool")

    with st.expander("ℹ️ What does this tool do?"):
        st.markdown("""
        This tool helps you visually compare two versions of code side-by-side.  
        It highlights additions, deletions, and modifications using color coding and also calculates how different the two versions are.
        """)

    col1, col2 = st.columns(2)
    with col1:
        left_code = st.text_area("Previous Code", height=200)
    with col2:
        right_code = st.text_area("Current Code", height=200)

    if st.button("Compare"):
        left_lines = left_code.splitlines()
        right_lines = right_code.splitlines()

        raw_html = difflib.HtmlDiff().make_file(
            fromlines=left_lines,
            tolines=right_lines,
            fromdesc="Previous Code",
            todesc="Current Code",
            context=True,
            numlines=3
        )

        cleaned_html = clean_diff_html(raw_html)

        diff_pct = calculate_diff_percentage(left_code, right_code)
        st.metric(label="Code Difference", value=f"{diff_pct}%")

        st.components.v1.html(cleaned_html, height=600, scrolling=True)

if __name__ == "__main__":
    main()
