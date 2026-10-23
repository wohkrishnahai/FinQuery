import requests
import streamlit as st
import pandas as pd
import plotly.express as px


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="FinQuery",
    page_icon="📊",
    layout="wide",
)


st.title("📊 FinQuery")
st.caption("AI Financial Data Analyst")


question = st.text_area(
    "Ask a question about your financial data",
    placeholder=(
        "Example: Which 5 merchants generated the highest revenue?"
    ),
    height=100,
)


if st.button("Analyze", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing your question..."):

        try:
            response = requests.post(
                f"{API_URL}/query",
                json={"question": question},
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

        except requests.exceptions.RequestException as exc:
            st.error(f"FinQuery could not process the request: {exc}")
            st.stop()

    st.subheader("Results")

    st.info(data["explanation"])

    result = data["result"]

    columns = result["columns"]
    rows = result["rows"]

    dataframe = pd.DataFrame(rows, columns=columns)

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )

    # Display a chart when the result is suitable.
    if len(dataframe.columns) >= 2 and not dataframe.empty:

        st.subheader("Visualization")

        x_column = dataframe.columns[0]
        y_column = dataframe.columns[-1]

        if pd.api.types.is_numeric_dtype(dataframe[y_column]):

            figure = px.bar(
                dataframe,
                x=x_column,
                y=y_column,
                title=f"{y_column} by {x_column}",
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    with st.expander("Generated SQL"):
        st.code(
            data["sql"],
            language="sql",
        )
