import streamlit as st
import plotly.graph_objs as go
import datetime

def generate_weekly_calendar():
    # Dummy-Daten für den Kalender
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    times = [f"{hour}:00" for hour in range(8, 18)]  # Beispielzeiten von 8:00 bis 17:00 Uhr

    # Erstellung des Kalenderlayouts mit Plotly
    fig = go.Figure()

    # Hinzufügen von leeren Plots für jeden Wochentag und jede Uhrzeit
    for day in days:
        for time in times:
            fig.add_trace(go.Scatter(x=[day], y=[time], mode='markers', marker=dict(size=10), name=''))

    # Anpassung des Layouts und der Achsenbeschriftungen
    fig.update_layout(
        title='Wochenkalender',
        xaxis=dict(title='Wochentage'),
        yaxis=dict(title='Uhrzeit')
    )

    return fig

def main():
    st.title("Interaktiver Wochenkalender")

    st.plotly_chart(generate_weekly_calendar())

if __name__ == "__main__":
    main()
