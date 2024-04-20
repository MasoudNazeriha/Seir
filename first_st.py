import streamlit as st
import pandas as pd
import altair as alt
from pandasql import sqldf

# Function to check if required columns are present in the DataFrame
def check_columns(df):
    required_columns = ['Hall', 'Route', 'Date_of_dp', 'Tariff']
    return all(col in df.columns for col in required_columns)

# Function to display Excel file
def display_excel_file(df):
    st.success('فایل اکسل با موفقیت بارگزاری شد', icon="✅")
    st.write(df)

# Main function
def main():
    st.title('وبگاه بررسی فروش قطارهای ریل سیر کوثر')

    # Sidebar: Browse Excel File
    st.sidebar.header('فایل اکسل را جستجو کنید')
    uploaded_file = st.sidebar.file_uploader("بارگزاری فایل اکسل", type=['xlsx'])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        if check_columns(df):
            display_excel_file(df)

            # List to track selected queries
            selected_queries = []

            # Display query options in sidebar
            custom_query = st.sidebar.checkbox("گزارش تعداد فروش هر سیر بر اساس نوع قطار و بازه زمانی")
            if custom_query:
                selected_queries.append("گزارش تعداد فروش هر سیر بر اساس نوع قطار و بازه زمانی")

            q2_query = st.sidebar.checkbox("گزارش تعداد فروش هر سیر بر اساس نوع قطار و بازه زمانی و تعرفه")
            if q2_query:
                selected_queries.append("گزارش تعداد فروش هر سیر بر اساس نوع قطار و بازه زمانی و تعرفه")

            sum_query = st.sidebar.checkbox("گزارش **مجموع** فروش هر سیر بر اساس نوع قطار و بازه زمانی ")
            if sum_query:
                selected_queries.append("گزارش **مجموع** فروش هر سیر بر اساس نوع قطار و بازه زمانی ")
                
            sumT_query = st.sidebar.checkbox("گزارش **مجموع** فروش هر سیر بر اساس نوع قطار و بازه زمانی و تعرفه ")
            if sumT_query:
                selected_queries.append("گزارش **مجموع** فروش هر سیر بر اساس نوع قطار و بازه زمانی و تعرفه ")


            # Display results based on selected queries
            for query in selected_queries:
                st.header(query)

                if query == "گزارش تعداد فروش هر سیر بر اساس نوع قطار و بازه زمانی":
                    # Custom Query Options
                    st.subheader("گزارش فروش سیر")

                    selected_halls = st.multiselect("لطفا نوع قطار را انتخاب کنید", sorted(df['Hall'].unique()), key="custom_halls")

                    date_options = st.radio("انتخاب تاریخ :", ["بر اساس تاریخ یک روز معین ", "بر اساس بازه زمانی"], key="custom_date_option")

                    if date_options == "بر اساس تاریخ یک روز معین ":
                        selected_date = st.selectbox("بر اساس تاریخ یک روز معین ", sorted(df['Date_of_dp'].unique()), key="custom_date")

                    elif date_options == "بر اساس بازه زمانی":
                        date_options = sorted(df['Date_of_dp'].unique())
                        if date_options:
                            min_date, max_date = st.select_slider("بر اساس بازه زمانی", options=date_options, value=(date_options[0], date_options[-1]), key="custom_date_range")
                            selected_date = (min_date, max_date)
                        else:
                            st.warning("هیچ سیری در این بازه وجود ندارد")
                            selected_date = None

                    if selected_halls and selected_date is not None:
                        filtered_df = df[df['Hall'].isin(selected_halls)]

                        if isinstance(selected_date, tuple):  # Date range
                            start_date, end_date = selected_date
                            filtered_df = filtered_df[(filtered_df['Date_of_dp'] >= start_date) & (filtered_df['Date_of_dp'] <= end_date)]
                        else:  # Single date
                            filtered_df = filtered_df[filtered_df['Date_of_dp'] == selected_date]

                        if not filtered_df.empty:
                            st.subheader('نتایج')

                            # Perform SQL query directly on DataFrame
                            query = "SELECT Hall, Date_of_dp, Route ,COUNT(*) as Count FROM filtered_df GROUP BY Hall, Route , Date_of_dp"
                            result_df = sqldf(query, locals())
                            st.dataframe(result_df)

                            # Chart for unique combinations
                            st.subheader(' نمودار تعداد فروش انواع قطار - تاریخ')
                            chart = alt.Chart(result_df).mark_bar().encode(
                                x='Date_of_dp',
                                y='Count',
                                color='Hall',
                                tooltip=['Hall', 'Date_of_dp', 'Count']
                            ).properties(width=600, height=400)
                            st.altair_chart(chart, use_container_width=True)

                        else:
                            st.warning("هیچ داده ای برای رسم نمودار یافت نشد ")

                    else:
                        st.warning("لطفا حداقل یک نوع قطار را انتخاب کنید ")

                elif query == "گزارش تعداد فروش هر سیر بر اساس نوع قطار و بازه زمانی و تعرفه":
                    # q2 Query Options
                    #st.subheader("q2 Query Options")

                    selected_halls = st.multiselect("انتخاب نوع قطار :", sorted(df['Hall'].unique()), key="q2_halls")
                    
                    selected_tariffs = st.multiselect("انتخاب تعرفه :", sorted(df['Tariff'].unique()), key="q2_tariffs")

                    date_options = st.radio("انتخاب تاریخ :", ["بر اساس تاریخ یک روز معین ", "بر اساس بازه زمانی"], key="q2_date_option")

                    if date_options == "بر اساس تاریخ یک روز معین " :
                        selected_date = st.selectbox(" بر اساس تاریخ یک روز معین :", sorted(df['Date_of_dp'].unique()), key="q2_date")

                    elif date_options == "بر اساس بازه زمانی":
                        date_options = sorted(df['Date_of_dp'].unique())
                        if date_options:
                            min_date, max_date = st.select_slider("بر اساس بازه زمانی :", options=date_options, value=(date_options[0], date_options[-1]), key="q2_date_range")
                            selected_date = (min_date, max_date)
                        else:
                            st.warning("هیچ سیری در این بازه وجود ندارد")
                            selected_date = None

                    if selected_halls and selected_date is not None:
                        filtered_df = df[df['Hall'].isin(selected_halls)]
                        
                        if selected_tariffs:
                            filtered_df = filtered_df[filtered_df['Tariff'].isin(selected_tariffs)]


                        if isinstance(selected_date, tuple):  # Date range
                            start_date, end_date = selected_date
                            filtered_df = filtered_df[(filtered_df['Date_of_dp'] >= start_date) & (filtered_df['Date_of_dp'] <= end_date)]
                        else:  # Single date
                            filtered_df = filtered_df[filtered_df['Date_of_dp'] == selected_date]

                        if not filtered_df.empty:
                            st.subheader('نتایج')

                            # Perform SQL query directly on DataFrame
                            query = "SELECT Hall, Date_of_dp, Route, Tariff, COUNT(*) as Count FROM filtered_df GROUP BY Hall, Route, Date_of_dp, Tariff"
                            result_df = sqldf(query, locals())
                            st.dataframe(result_df)

                            # Chart for unique combinations
                            st.subheader('نمودار')
                            chart = alt.Chart(result_df).mark_bar().encode(
                                x='Date_of_dp',
                                y='Count',
                                color='Hall',
                                tooltip=['Hall', 'Date_of_dp', 'Count']
                            ).properties(width=600, height=400)
                            st.altair_chart(chart, use_container_width=True)

                        else:
                            st.warning("هیچ داده ای برای رسم نمودار یافت نشد")

                    else:
                        st.warning("لطفا حداقل یک نوع قطار را انتخاب نمایید")
                
                elif query == "گزارش **مجموع** فروش هر سیر بر اساس نوع قطار و بازه زمانی ":
                    # Custom Query Options
                    st.subheader("گزارش مجموع فروش سیر")

                    selected_halls = st.multiselect("لطفا نوع قطار را انتخاب کنید", sorted(df['Hall'].unique()), key="custom_halls3")

                    date_options = st.radio("انتخاب تاریخ :", ["بر اساس تاریخ یک روز معین ", "بر اساس بازه زمانی"], key="custom_date_option3")

                    if date_options == "بر اساس تاریخ یک روز معین ":
                        selected_date = st.selectbox("بر اساس تاریخ یک روز معین ", sorted(df['Date_of_dp'].unique()), key="custom_date3")

                    elif date_options == "بر اساس بازه زمانی":
                        date_options = sorted(df['Date_of_dp'].unique())
                        if date_options:
                            min_date, max_date = st.select_slider("بر اساس بازه زمانی", options=date_options, value=(date_options[0], date_options[-1]), key="custom_date_range3")
                            selected_date = (min_date, max_date)
                        else:
                            st.warning("هیچ سیری در این بازه وجود ندارد")
                            selected_date = None

                    if selected_halls and selected_date is not None:
                        filtered_df = df[df['Hall'].isin(selected_halls)]

                        if isinstance(selected_date, tuple):  # Date range
                            start_date, end_date = selected_date
                            filtered_df = filtered_df[(filtered_df['Date_of_dp'] >= start_date) & (filtered_df['Date_of_dp'] <= end_date)]
                        else:  # Single date
                            filtered_df = filtered_df[filtered_df['Date_of_dp'] == selected_date]

                        if not filtered_df.empty:
                            st.subheader('نتایج')

                            # Perform SQL query directly on DataFrame
                            query = "SELECT Hall, Date_of_dp, Route ,SUM(Passenger_pay) as Total_Amount FROM filtered_df GROUP BY Hall, Route , Date_of_dp"
                            result_df = sqldf(query, locals())
                            st.dataframe(result_df)

                            # Chart for unique combinations
                            st.subheader(' نمودار مجموع فروش انواع قطار - تاریخ')
                            chart = alt.Chart(result_df).mark_bar().encode(
                                x='Date_of_dp',
                                y='Total_Amount',
                                color='Hall',
                                tooltip=['Hall', 'Date_of_dp', 'Total_Amount']
                            ).properties(width=600, height=400)
                            st.altair_chart(chart, use_container_width=True)

                        else:
                            st.warning("هیچ داده ای برای رسم نمودار یافت نشد ")

                    else:
                        st.warning("لطفا حداقل یک نوع قطار را انتخاب کنید ")
                        
                elif query == "گزارش **مجموع** فروش هر سیر بر اساس نوع قطار و بازه زمانی و تعرفه ":
                    # q2 Query Options
                    #st.subheader("q2 Query Options")

                    selected_halls = st.multiselect("انتخاب نوع قطار :", sorted(df['Hall'].unique()), key="q2_halls4")
                    
                    selected_tariffs = st.multiselect("انتخاب تعرفه :", sorted(df['Tariff'].unique()), key="q2_tariffs4")

                    date_options = st.radio("انتخاب تاریخ :", ["بر اساس تاریخ یک روز معین ", "بر اساس بازه زمانی"], key="q2_date_option4")

                    if date_options == "بر اساس تاریخ یک روز معین " :
                        selected_date = st.selectbox(" بر اساس تاریخ یک روز معین :", sorted(df['Date_of_dp'].unique()), key="q2_date4")

                    elif date_options == "بر اساس بازه زمانی":
                        date_options = sorted(df['Date_of_dp'].unique())
                        if date_options:
                            min_date, max_date = st.select_slider("بر اساس بازه زمانی :", options=date_options, value=(date_options[0], date_options[-1]), key="q2_date_range4")
                            selected_date = (min_date, max_date)
                        else:
                            st.warning("هیچ سیری در این بازه وجود ندارد")
                            selected_date = None

                    if selected_halls and selected_date is not None:
                        filtered_df = df[df['Hall'].isin(selected_halls)]
                        
                        if selected_tariffs:
                            filtered_df = filtered_df[filtered_df['Tariff'].isin(selected_tariffs)]


                        if isinstance(selected_date, tuple):  # Date range
                            start_date, end_date = selected_date
                            filtered_df = filtered_df[(filtered_df['Date_of_dp'] >= start_date) & (filtered_df['Date_of_dp'] <= end_date)]
                        else:  # Single date
                            filtered_df = filtered_df[filtered_df['Date_of_dp'] == selected_date]

                        if not filtered_df.empty:
                            st.subheader('نتایج')

                            # Perform SQL query directly on DataFrame
                            query = "SELECT Hall, Date_of_dp, Route, Tariff, SUm(Passenger_pay) as Total_amount FROM filtered_df GROUP BY Hall, Route, Date_of_dp, Tariff"
                            result_df = sqldf(query, locals())
                            st.dataframe(result_df)

                            # Chart for unique combinations
                            st.subheader('نمودار')
                            chart = alt.Chart(result_df).mark_bar().encode(
                                x='Date_of_dp',
                                y='Total_amount',
                                color='Hall',
                                tooltip=['Hall', 'Date_of_dp', 'Total_amount']
                            ).properties(width=600, height=400)
                            st.altair_chart(chart, use_container_width=True)

                        else:
                            st.warning("هیچ داده ای برای رسم نمودار یافت نشد")

                    else:
                        st.warning("لطفا حداقل یک نوع قطار را انتخاب نمایید")
                        
        else : st.error("فایل اکسل بارگزاری شده با استاندارد های برنامه تطابق ندارد لطفا با پشتیبانی جهت حل مشکل تماس حاصل شود")
if __name__ == "__main__":
    main()


