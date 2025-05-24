import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error

def create_connection():
     try:
          connection = mysql.connector.connect(
              host="localhost",
              user="root",
              password ="Yaseenathar@123",
              database ="securecheck",
          )
          return connection
     except Exception as e:
          st.error(f"Database Connection Error: {e}")
          return None


def fetch_data(query):
     connection = create_connection()
     if connection:
          try:
               cursor = connection.cursor(dictionary=True)
               cursor.execute(query)
               result = cursor.fetchall()
               df = pd.DataFrame(result)
               return df
          finally:
               connection.close()
     else:
          return pd.DataFrame()
     

st.set_page_config(page_title="SecureCheck Police Dashboard", layout="wide")
st.title("SecureCheck: Police Checkpost Digital Ledger")
st.markdown("Real-time monitoring and insights for law enforcement.")

st.header("Police Logs Overview")
query = "SELECT * FROM secure_check"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)

st.header("Key Metrics")

col1, col2, col3, col4= st.columns(4)

with col1:
     total_stops = data.shape[0]
     st.metric("Total police stops",total_stops)

with col2:
     arrests = data[data["stop_outcome"].str.contains("arrest",case = False,na = False)].shape[0]
     st.metric("Total Arrests", arrests)
with col3:
     warnings = data[data["stop_outcome"].str.contains("warning",case = False,na = False)].shape[0]
     st.metric("Total Warnings", warnings)
with col4:
     drugs_related = data[data["drugs_related_stop"] == 1].shape[0]
     st.metric("Drugs related stops", drugs_related)


st.header("Advanced Insights")

selected_query = st.selectbox("Select a Query to Run",[
     "What are the top 10 vehicles involved in drug-related stops?",
     "Which vehicles were most frequently searched?",
     "Which driver age group had the highest arrest rate?",
     "What is the gender distribution of drivers stopped in each country?",
     "Which race and gender combination has the highest search rate?",
     "What time of day sees the most traffic stops?",
     "What is the average stop duration for different violations?",
     "Are stops during the night more likely to lead to arrests?",
     "Which violations are most associated with searches or arrests?",
     "Which violations are most common among younger drivers (<25)?",
     "Is there a violation that rarely results in search or arrest?",
     "Which countries report the highest rate of drug-related stops?",
     "What is the arrest rate by country and violation?",
     "Which country has the most stops with search conducted?"
     "Yearly Breakdown of Stops and Arrests by Country?",
     "Driver Violation Trends Based on Age and Race?",
     "Time Period Analysis of Stops (Joining with Date Functions), Number of Stops by Year,Month, Hour of the Day?",
     "Violations with High Search and Arrest Rates?",
     "Driver Demographics by Country?",
     "Top 5 Violations with Highest Arrest Rates?"
     ])
     
query_map = {
     "What are the top 10 vehicles involved in drug-related stops?": """
             SELECT vehicle_number, COUNT(*) AS drugs_related_stop
             FROM secure_check
             WHERE drugs_related_stop = 1
             GROUP BY vehicle_number
             ORDER BY drugs_related_stop DESC
             LIMIT 10;
        """,
     "Which vehicles were most frequently searched?":"""
             SELECT vehicle_number, COUNT(*) AS search_count
             FROM secure_check
             WHERE search_conducted = 1
             GROUP BY vehicle_number
             ORDER BY search_count DESC
             """,
     "Which driver age group had the highest arrest rate?" : """ 
             select driver_age, count(*) as is_arrested
             from secure_check
             where is_arrested = 1
             group by  driver_age
             order by is_arrested desc
             """, 
     "What is the gender distribution of drivers stopped in each country?":"""
             SELECT country_name, driver_gender, COUNT(*) AS stop_count
             FROM secure_check
             GROUP BY country_name, driver_gender
             ORDER BY country_name, stop_count DESC;
             """,
     "Which race and gender combination has the highest search rate?":"""
             SELECT driver_race,driver_gender,COUNT(*) AS total_stops,
             SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS search_count,
             ROUND(1.0 * SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS search_rate
             FROM secure_check
             WHERE driver_race IS NOT NULL AND driver_gender IS NOT NULL
             GROUP BY driver_race, driver_gender
             ORDER BY search_rate DESC
             LIMIT 1;
             """,
     "What time of day sees the most traffic stops?": """
             SELECT EXTRACT(HOUR FROM stop_time) AS stop_hour,
             COUNT(*) AS stop_count FROM secure_check
             GROUP BY stop_hour ORDER BY stop_count DESC
             LIMIT 1;
             """,
     "What is the average stop duration for different violations?":"""
             SELECT violation, AVG(stop_duration) AS avg_stop_duration
             FROM secure_check WHERE stop_duration IS NOT NULL
             GROUP BY violation ORDER BY avg_stop_duration DESC;
             """,
     "Are stops during the night more likely to lead to arrests?":"""
           SELECT CASE 
           WHEN CONVERT(SUBSTRING(stop_time, 1, 2), UNSIGNED) BETWEEN 20 AND 23 
             OR CONVERT(SUBSTRING(stop_time, 1, 2), UNSIGNED) BETWEEN 0 AND 5 
           THEN 'Night'
           ELSE 'Day'
           END AS time_of_day,COUNT(*) AS total_stops,
           SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
           ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS arrest_rate
           FROM secure_check WHERE stop_time IS NOT NULL AND is_arrested IS NOT NULL
           GROUP BY time_of_day ORDER BY arrest_rate DESC;
        """,
     "Which violations are most associated with searches or arrests?":"""
            SELECT violation,COUNT(*) AS total_stops,
            SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
            ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS search_rate,
            SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
            ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS arrest_rate
            FROM secure_check WHERE violation IS NOT NULL GROUP BY violation
            ORDER BY search_rate DESC, arrest_rate DESC;
        """,
     "Which violations are most common among younger drivers (<25)?":"""
           SELECT violation,COUNT(*) AS stop_count FROM secure_check
           WHERE driver_age < 25 AND violation IS NOT NULL
           GROUP BY violation ORDER BY stop_count DESC;
        """,
     "Is there a violation that rarely results in search or arrest?":"""
           SELECT 
               violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
               ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS search_rate,
               SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS arrest_rate
           FROM secure_check
           WHERE violation IS NOT NULL
           GROUP BY violation
           HAVING search_rate < 0.05 AND arrest_rate < 0.05
           ORDER BY total_stops DESC;
       """,
     "Which countries report the highest rate of drug-related stops?":"""
           SELECT country_name,COUNT(*) AS total_stops,
           SUM(CASE WHEN drugs_related_stop = 1 THEN 1 ELSE 0 END) AS drug_stops,
           ROUND(SUM(CASE WHEN drugs_related_stop = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS drug_stop_rate
           FROM secure_check WHERE country_name IS NOT NULL
           GROUP BY country_name ORDER BY drug_stop_rate DESC
        """,
     "What is the arrest rate by country and violation?":"""
           SELECT country_name,violation,COUNT(*) AS total_stops,
           SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
           ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS arrest_rate
           FROM secure_check WHERE country_name IS NOT NULL AND violation IS NOT NULL
           GROUP BY country_name, violation ORDER BY arrest_rate DESC;
        """,
     "Which country has the most stops with search conducted?":"""
           SELECT country_name,COUNT(*) AS total_searches FROM secure_check
           WHERE search_conducted = 1 AND country_name IS NOT NULL
           GROUP BY country_name ORDER BY total_searches DESC LIMIT 1;
        """, 
     "Yearly Breakdown of Stops and Arrests by Country?":"""
           SELECT country_name, YEAR(stop_date) AS stop_year, COUNT(*) AS total_stops,
           SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
           ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS arrest_rate,
           SUM(COUNT(*)) OVER (PARTITION BY country_name ORDER BY YEAR(stop_date)) AS running_total_stops
           FROM secure_check WHERE stop_date IS NOT NULL AND country_name IS NOT NULL
           GROUP BY country_name, YEAR(stop_date) ORDER BY country_name, stop_year;
        """,
     "Driver Violation Trends Based on Age and Race?":"""
           SELECT v.driver_race,v.age_group,v.violation,COUNT(*) AS total_violations
           FROM (
                SELECT 
                driver_race,
                violation,
                CASE
                     WHEN driver_age < 18 THEN 'Under 18'
                     WHEN driver_age BETWEEN 18 AND 24 THEN '18-24'
                     WHEN driver_age BETWEEN 25 AND 34 THEN '25-34'
                     WHEN driver_age BETWEEN 35 AND 44 THEN '35-44'
                     WHEN driver_age BETWEEN 45 AND 59 THEN '45-59'
                     ELSE '60+'
                     END AS age_group
           FROM secure_check
           WHERE driver_age IS NOT NULL AND violation IS NOT NULL AND driver_race IS NOT NULL
           ) AS v
           GROUP BY v.driver_race, v.age_group, v.violation
           ORDER BY v.driver_race, v.age_group, total_violations DESC;
        """,
     "Time Period Analysis of Stops (Joining with Date Functions), Number of Stops by Year,Month, Hour of the Day?":"""
           SELECT YEAR(stop_date) AS stop_year,MONTH(stop_date) AS stop_month,
           HOUR(STR_TO_DATE(stop_time, '%H:%i')) AS stop_hour,COUNT(*) AS total_stops
           FROM secure_check WHERE stop_date IS NOT NULL AND stop_time IS NOT NULL
           GROUP BY YEAR(stop_date), MONTH(stop_date), HOUR(STR_TO_DATE(stop_time, '%H:%i'))
           ORDER BY stop_year, stop_month, stop_hour;
        """,
     "Violations with High Search and Arrest Rates?":"""
           SELECT
                violation,
                total_stops,
                total_searches,
                total_arrests,
                ROUND(total_searches / total_stops, 4) AS search_rate,
                ROUND(total_arrests / total_stops, 4) AS arrest_rate,
                RANK() OVER (ORDER BY (total_searches / total_stops) DESC) AS search_rate_rank,
                RANK() OVER (ORDER BY (total_arrests / total_stops) DESC) AS arrest_rate_rank
           FROM (
                 SELECT
                 violation,
                 COUNT(*) AS total_stops,
                 SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
                 SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests
                 FROM secure_check
                 WHERE violation IS NOT NULL
                 GROUP BY violation
           ) AS v
           ORDER BY search_rate DESC, arrest_rate DESC;
        """,
     "Driver Demographics by Country?":"""
           SELECT 
                country_name,driver_gender,driver_race,
                ROUND(AVG(driver_age), 1) AS avg_driver_age, COUNT(*) AS total_stops
           FROM secure_check
           WHERE 
                country_name IS NOT NULL 
                AND driver_gender IS NOT NULL 
                AND driver_race IS NOT NULL 
                AND driver_age IS NOT NULL
           GROUP BY country_name, driver_gender, driver_race
           ORDER BY country_name, total_stops DESC;
        """,
     "Top 5 Violations with Highest Arrest Rates?":"""
           SELECT violation,COUNT(*) AS total_stops,
           SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
           ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS arrest_rate
           FROM secure_check
           WHERE violation IS NOT NULL
           GROUP BY violation
           HAVING total_stops > 0
           ORDER BY arrest_rate DESC
           LIMIT 5;
        """
     
}    

if st.button("Run query"):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)   
     else:
          st.warning("No result found for the selected query") 

st.markdown("...")
st.markdown("Built for Law enforcement by Securecheck")
st.header("Securecheck")

st.markdown("Fill the deatails below to get a prediction of the outcome based on existing data.")    

st.header("Add new police log and predict outcome and violation")

with st.form("new_log_form"):
     stop_date = st.date_input("stop Date")
     stop_time = st.time_input("stop Time")
     country_name = st.text_input("country name")
     driver_gender = st.selectbox("driver gender",["male","female"])
     driver_age = st.number_input("driver age", min_value=16, max_value=100, value=27)
     driver_race = st.text_input("driver race")
     search_conducted =st.selectbox("was a search conducted?", ["0","1"]) 
     search_type =st.text_input("search type") 
     drugs_related_stops =st.selectbox("was it drug related?", ["0","1"])
     stop_duration = st.selectbox("stop duration",data['stop_duration'].dropna().unique())
     vehicle_number = st.text_input("vehicle number")
     time_stamp = pd.Timestamp.now()

     submitted = st.form_submit_button("predict stop outcome & violation")

     if submitted:
          filtered_data= data[
               (data['driver_gender']==driver_gender)&
               (data['driver_age']==driver_age)&
               (data['search_conducted']==int(search_conducted))&
               (data['stop_duration']==stop_duration)&
               (data['drugs_related_stop']==int(drugs_related_stops))
          ]

          if not filtered_data.empty:
               predicted_outcome = filtered_data['stop_outcome'].mode()[0]
               predicted_violation = filtered_data['violation'].mode()[0]
          else:
               predicted_outcome = "warning"
               predicted_violation = "speeding"
          
               
               
          
     
      