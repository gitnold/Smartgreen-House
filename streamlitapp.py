import streamlit as st
import pandas as pd
from enum import Enum, auto
import rule_engine
import altair as alt

class AvgType(Enum):
    SIMPLE=auto()
    EXP=auto()


st.title("Smart GreenHouse Control")
st.markdown("""
    ## Smart Green House Control.
Welcome to Smart Green House Control. This is the homepage to simulate the green house control scenario by dynamically changing input using sliders in the sidebar on the `streamlitapp` page.
The latest sensor readings dataframes and bar charts rerender when environment variables change. 
""")

moving_avearages_description = """###### Simple Moving Average.
The line charts below show visualizations for moving averages of soil moisture levels.
**Simple Moving Average** denoted as *sma* on the chart below is calculated as shown below:
$$
SMA_n = \\frac{P_t + P_{t-1} + P_{t-2} + \ldots + P_{t-(n-1)}}{n}
$$
Where:
- $SMA_n$ = Simple Moving Average over n periods
- $n$ = Number of periods
- $P_t$ = Soil moisture at time t

###### Exponential Moving Average.
**Exponential Moving Average** deonated as *ema* is calculated as follows:
$$
EMA_t = \\alpha \cdot P_t + (1 - \\alpha) \cdot EMA_{t-1}
$$
Where:
- $EMA_t$ = Exponential Moving Average at time t
- $\\alpha$ = Smoothing factor (weighting multiplier)
- $P_t$ = Soil Moisture at time t
- $EMA_{t-1}$ = Previous period's EMA

"""



#TODO: add moving average based decisions.


def launch_app() -> None:
    #TODO: do an average of soil moisture

    # Adding persistent variables that should remain between reruns and page refresh
    # soil moistures for moving averages and alerts for flag triggers.
    if "moisture_values" not in st.session_state:
        st.session_state.moisture_values = []

    if "alerts" not in st.session_state:
        st.session_state.alerts = []


    st.sidebar.header("Environment variable controls") #sidebar header

    #input values from the sidebar sliders.
    moisture_slider = st.sidebar.slider("Soil Moisture", min_value=10, max_value=100, step=1, help="Adjust soil moisture")
    light_slider = st.sidebar.slider("Light Intensity", min_value=20, max_value=2200, step=1, help="Light Intensity")
    humidity_slider = st.sidebar.slider("Humidity", min_value=0, max_value=100, step=1, help="Adjust Humidity")
    temperature_slider = st.sidebar.slider("Temperature", min_value=0, max_value=100, step=1, help="Adjust Temperature")
    c02_slider = st.sidebar.slider("Carbon dioxide", min_value=20, max_value=2000, step=1, help="Adjust Carbon Dioxide")
   
    #appending the soil moisture values to the moisture_values session state variable
    st.session_state.moisture_values.append(moisture_slider)

    #creating a pandas dataframe for easier data manipulation.
    data = pd.DataFrame({
        'Variables': ['Soil Moisture', 'Light', 'Humidity', 'Temperature', 'Carbon IV Oxide'],
        'Value': [moisture_slider, light_slider, humidity_slider, temperature_slider, c02_slider]
    })
    
    #Turning each row of the dataframe to dictionary where the keys are the corresponding column titles.
    #the zip function creates and returns a tuple from the arguments which is then converted to a dictionary by the dict function.
    data_dict = dict(zip(data['Variables'], data['Value']))

    #notification pop-ups for the rule engine decisions.
    st.toast(f"**Watering Control:** {rule_engine.wateringControl(data_dict)}")
    st.toast(f"**Shading Control:** {rule_engine.shadingControl(data_dict)}")
   
    #adding the alerts to the session state for future reference.
    st.session_state.alerts.append(bool(rule_engine.raiseAlert(data_dict)))
    
    #writing the data dataframe to the web page for visual analysis.
    st.markdown("###### Latest sensor readings dataframe")
    st.dataframe(data)
    
    #Functions to handle drawing the line and bar charts as well as managing alerts.
    draw_moving_average_line_chart(st.session_state.moisture_values)
    draw_bar_charts(data)

    manage_alerts(st.session_state.alerts)


def manage_alerts(alerts: list[bool]) -> None:
    if len(alerts) >= 3 and alerts[-3:] == [True, True, True]:
        st.toast("##### Critical Risk Attained")
    elif alerts[-1] == True:
        st.toast("###### Conditions not optimum.")

def draw_bar_charts(data: pd.DataFrame) -> None:
    st.markdown("Latest sensor readings.")
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Variables', sort=None),
        y='Value',
        color='Variables'  
    ).properties(
        width=600,
        height=400,
        title="Sensor Readings"
    )

    st.altair_chart(chart, use_container_width=True)


def draw_moving_average_line_chart(moistures: list[int]) -> None:
    st.write("#### Moving average.")
    st.markdown(moving_avearages_description)
    
    sma = local_moving_average(moistures, AvgType.SIMPLE)
    ema = local_moving_average(moistures, AvgType.EXP)

    movavgs = pd.DataFrame({'sma': sma, 'ema': ema})

    st.line_chart(movavgs, y=['sma', 'ema'], x_label='Hours', y_label='moving average')
    

    

#NOTE: sma seems to rise gradually over time hence reduce watering over time.
#NOTE: ema changes drastically, find how useful it is.

def local_moving_average(moistures: list[int], avg_type: AvgType) -> list[int]:
    avg_points = []
    ema_points = []
    #exp mov avg = Pt * alpha + EMA(t-1) * (1- alpha)
    #Pt = most recent data point.
    # alpha is the smoothing factor = 2 / (n + 1).
    # n = number of periods
    # EMA(t - 1) = moving average rom previous period.

    match avg_type:
        case avg_type.SIMPLE:
            for i in range(len(moistures)):
                if i == 0:
                    sma = moistures[i]
                else:
                    sma = sum(moistures[:i]) / len(moistures[:i])
                avg_points.append(sma)

            return avg_points

        case avg_type.EXP:
            for i in range(len(moistures)):
                if i == 0:
                    ema = moistures[i]
                else:
                    alpha = 2 / (len(moistures) + 1)
                    ema = (moistures[-1] * alpha) + (ema_points[-1] * (1 - alpha))
                ema_points.append(ema)

            return ema_points


    
    



if __name__ == "__main__":
    launch_app()
