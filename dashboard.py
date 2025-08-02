import pandas as pd
import plotly.express as px

def show_dashboard(stats):
    df = pd.DataFrame(stats)
    bar = px.bar(df, x="action", y="count", title="Activity Dashboard")
    st.plotly_chart(bar)
    stats = [{"action": "Questions", "count": 4}, {"action": "Quizzes", "count": 2}]
show_dashboard(stats)