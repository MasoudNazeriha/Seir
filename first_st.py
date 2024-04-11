import streamlit as st
import pandas as pd

def main():
    st.title("Excel File Viewer")

    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Read Excel file as DataFrame
            df = pd.read_excel(uploaded_file)

            # Display DataFrame
            st.write(df)
        except Exception as e:
            st.error("An error occurred while reading the file: {}".format(str(e)))

if __name__ == "__main__":
    main()
