# myapp/views.py
import math
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from django.shortcuts import render
import matplotlib
import plotly.graph_objs as go
from scipy.signal import savgol_filter
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
import numpy as np
import pandas as pd
import scipy
#plotly dash
import plotly.express as px
from scipy import signal
from scipy.interpolate import make_interp_spline

matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot, important



def input_values(request):
    if request.method == 'POST':
        #limitation of quantity
        tetta_s = []
        #taking values directly from excel
        values = request.POST['values']
        raw_values = values.strip().split(' ')
        for raw_value in raw_values:
            if raw_value:
        # Replace comma with dot and convert to float
                cleaned_value = raw_value.replace(",", ".")
                tetta_s.append(float(cleaned_value))
        cleaned_values_string = ' '.join(map(str, tetta_s))
        values = cleaned_values_string

        
        #getting inputs and values
        a = float(request.POST.get('a', 0.1))
        n = float(request.POST.get('n', 0.1))
        m = float(request.POST.get('m', 0.1))
        soil_suction_r = float(request.POST.get('soil_suction_r', 10000))
        e = math.exp(1)
        T_s = 72.75 * (10 ** (-3))
        soil_suction = []


        #getting from excel too
        values1 = request.POST['values1']
        raw_values = values1.strip().split(' ')
        for raw_value in raw_values:
            if raw_value:
                cleaned_value = raw_value.replace(",", ".")
                soil_suction.append(float(cleaned_value))
        cleaned_values_string = ' '.join(map(str, soil_suction))
        values1 = cleaned_values_string

        water_content = []
        pore_radius = []
        derivation = []
        base_soil_suction=[0.01,1.00,2.00,5.00,10.00,20.00,30.00,40.00,50.00,60.0,70.00,80.00,90.00,100.00,200.00,500.00,1000.00,5000.00,10000.00,100000.00,1000000.00]

        base_thetha_s=[]

        # Block of code for the 3rd formula - Water content
        def formula3(value, value2, a, n, m, soil_suction_r):
            ln1 = math.log(1 + float(value) / float(soil_suction_r))
            ln2 = math.log(1 + (10 ** 6) / float(soil_suction_r))
            ln3 = math.log(e + (float(value / float(a))) ** float(n))
            overall_formula = float(value2) * (1 - float(ln1) / float(ln2)) * ((1 / float(ln3)) ** float(m))
            return overall_formula

        # Block of code for the 4th formula - Derivation
        def formula4(value, a, n, m, soil_suction_r, T_s):
            ln1 = math.log(1 + (float(value) / soil_suction_r))
            ln2 = math.log(1 + (10 ** 6) / soil_suction_r)
            ln3 = math.log(e + ((float(value / a)) ** n))
            block1 = float(1 - (ln1 / ln2))
            block2 = float(m * n * ((float(value / a) ** (n - 1))))
            block2_1 = float(a * (e + ((float(value / a)) ** n))) * (ln3 ** (m + 1))
            block2_2 = block2 / block2_1
            block3 = float(1 / (value + soil_suction_r))
            block4 = float(1 / (math.log(1 + (10 ** 6) / soil_suction_r)))
            block5 = float(1 / (ln3 ** m))
            second_formula_1 = block1 * block2_2
            third_formula = block3 * block4 * block5
            second_formula = second_formula_1 + third_formula
            return second_formula, float(2 * T_s) / float(value)

        # Block of code to call the third formula and fourth formula functions
        
        for value in range(len(tetta_s)):
            water_content.append(formula3(soil_suction[value], tetta_s[0], a, n, m, soil_suction_r))
            derivation_value, pore_radius_value = formula4(tetta_s[value], a, n, m, soil_suction_r, T_s)
            derivation.append(derivation_value)
            pore_radius.append(pore_radius_value)

        # Block of code to finish the 4th formula
        for value in range(len(tetta_s)):
            derivation[value] = derivation[value] * soil_suction[value]


        swcc_trace = go.Scatter(
            x=soil_suction,
            y=water_content,
            mode='lines',
            name='Best-fit'
        )

        # Create a trace for measured data
        measured_trace = go.Scatter(
            x=soil_suction,
            y=tetta_s,
            mode='markers',
            name='Measured Data'
        )

        # Define the layout for the plot
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey"
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white'
        )

        # Create a figure with the defined data and layout
        #swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)

        # Convert the figure to an HTML div element
        swcc_div1 = swcc_fig.to_html(full_html=False)


        # Define the objective function for optimization
        def objective(variables):
            a, n, m, soil_suction_r = variables
            global error_sum
            error_sum=0
            for i in range(len(soil_suction)):
                predicted_water_content = formula3(soil_suction[i],tetta_s[0], a, n, m, soil_suction_r)
                error = abs(tetta_s[i] - predicted_water_content)
                #if error>=0.00101000:
                #if error>=0.005:
                #if error>=0:
                if error>=0.0001:
                    error_sum+=error #- >even worse
            for i in range(len(soil_suction)):
                predicted_water_content = formula3(soil_suction[i],tetta_s[0], a, n, m, soil_suction_r)
                error = ((tetta_s[i] - predicted_water_content) / tetta_s[i]) ** 2
                print(error)
                #if error>0.4689999999999999:
                if error>0.1:
                #if error>0.5:
                    continue
            error_sum += error
            
            return error_sum

        # Perform optimization
 
               

        # Set initial values for optimization,
        x0 = [0.1, 0.1, 0.1, 0.1]
        # Set bounds for the variables (optional)
        #bounds = [(1,None), (1, 6), (1, 6), (1,None)]
        bounds = [(0.5, None), (0.5, 6), (0.5, 6), (0.5, None)]
        


        # Perform optimization
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,options={'maxiter': 10000, 'ftol': 1e-10})
        #result = differential_evolution(objective, bounds, maxiter=1000, tol=1e-8)

        optimal_a, optimal_n, optimal_m, optimal_soil_suction_r = result.x

        for value in range(len(base_soil_suction)):
            base_thetha_s.append(formula3(base_soil_suction[value],tetta_s[0],optimal_a,optimal_n,optimal_m,optimal_soil_suction_r))
        #to save input values
        a1=a
        n1=n
        m1=m
        soil_suction_r1=soil_suction_r

        #to draw a new graph
        a=optimal_a
        n=optimal_n
        m=optimal_m
        soil_suction_r=optimal_soil_suction_r
        water_content.clear()
        derivation.clear()
        pore_radius.clear()

        for value in range(len(soil_suction)):
            water_content.append(formula3(soil_suction[value], tetta_s[0], optimal_a, optimal_n, optimal_m, optimal_soil_suction_r))
            derivation_value, pore_radius_value = formula4(soil_suction[value], a, n, m, soil_suction_r, T_s)
            derivation.append(derivation_value)
            pore_radius.append(pore_radius_value)

        # Block of code to finish 4th formula
        for value in range(len(soil_suction)):
            derivation[value] = derivation[value] * soil_suction[value]


        # Graph 2.
        # smoothed_water_content = savgol_filter(water_content, window_length=10, polyorder=8)
        #
        # smoothed_trace = go.Scatter(
        #     x=soil_suction,
        #     y=smoothed_water_content,
        #     mode='lines',
        #     name='Smoothed Best-fit'
        # )

        smoothed_water_content = scipy.signal.savgol_filter(water_content, window_length=17, polyorder=10)

        gfg=make_interp_spline(soil_suction, water_content, k=9 )
        new_water_content=gfg(soil_suction)


        #swcc = go.Scatter(x=soil_suction, y=smoothed_water_content, mode='lines', name='Smoothed Best-fit', line_shape='spline')
        #swcc=go.Scatter(x=soil_suction,y=signal.savgol_filter(water_content,17,13),mode='lines', name='Smoothed Best-fit', line_shape='spline',trendline_options=dict(frac=0.1))#9-11 are good numbers#17 is max for windows
        swcc = go.Scatter(x=soil_suction, y=new_water_content, mode='lines', name='Best-fit')
        swcc_trace = go.Scatter(x=soil_suction, y=water_content, mode='lines', name='Best-fit')
        measured_trace = go.Scatter(x=soil_suction, y=tetta_s, mode='markers', name='Measured Data')
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
        )
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace,swcc], layout=swcc_layout)
        swcc_div = swcc_fig.to_html(full_html=False)




        #Graph 3
        new_swcc = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Smoothed Best-fit Extended', line_shape='spline')
        new_swcc_trace = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Best-fit Extended')
        new_measured_trace = go.Scatter(x=soil_suction, y=tetta_s, mode='markers', name='Measured Data')
        optimal_a_text = f"a: {round(optimal_a, 2)}"
        optimal_n_text = f"n: {round(optimal_n, 2)}"
        optimal_m_text = f"m: {round(optimal_m, 2)}"
        optimal_soil_suction_r_text = f"Ψr: {round(optimal_soil_suction_r, 2)}"
        annotations = [
        dict(
        x=1.0,  # Adjust the x position to move the annotation to the right
        y=0.85,  # Adjust the y position to move the annotation upwards
        xref='paper',
        yref='paper',
        text=optimal_a_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        dict(
        x=1.0,  # Adjust the x position
        y=0.80,   # Adjust the y position
        xref='paper',
        yref='paper',
        text=optimal_n_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        dict(
        x=1.0,  # Adjust the x position
        y=0.75,  # Adjust the y position
        xref='paper',
        yref='paper',
        text=optimal_m_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        dict(
        x=1.0,  # Adjust the x position
        y=0.70,   # Adjust the y position
        xref='paper',
        yref='paper',
        text=optimal_soil_suction_r_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        ]

        new_swcc_layout = go.Layout(
        title='New Soil-Water Characteristics Curve',
        xaxis=dict(
            type='log',
            title='Soil Suction (kPa)',
            showgrid=True,  # Show the grid lines
            gridwidth=0.4,     # Set the grid line width
            gridcolor='grey',  # Set the grid line color to black
            dtick='auto',
            linewidth=1, linecolor='black',
            zeroline=True,
            zerolinecolor="grey",
        ),
        yaxis=dict(
            title='Volumetric Water Content (w)',
            showgrid=True,  # Show the grid lines
            gridwidth=0.4,  # Set the grid line width
            gridcolor='grey',  # Set the grid line color to grey
            dtick='0.1',  # Automatically determine the spacing of grid lines
            linewidth=1,
            linecolor='black',
            zeroline=True,
            zerolinecolor="grey",
            rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
            annotations=annotations
        )
        new_swcc_fig = go.Figure(data=[new_swcc_trace, new_measured_trace,new_swcc], layout=new_swcc_layout)
        new_swcc_div = new_swcc_fig.to_html(full_html=False)


        # Graph 5
        psd_trace_smooth=go.Scatter(x=pore_radius, y=derivation, mode='lines', name='Smooth PSD',line_shape="spline")
        psd_trace = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='PSD')
        psd_layout = go.Layout(
            title='Pore-Size Distribution',
            xaxis=dict(
                type='log',
                title='Pore Radius (mm)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',  # Change the x-axis color to black
                zeroline=True,  # Start the x-axis from 0
                zerolinecolor='grey',  # Change the c
                # olor of the zero line
            ),
            yaxis=dict(
                title='Derivation',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,  # Change dtick to a specific value
                linewidth=1,
                linecolor='black',


                zeroline=True,
                zerolinecolor='grey',
                rangemode = 'tozero'
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white',
        )

        psd_fig = go.Figure(data=[psd_trace_smooth], layout=psd_layout)
        psd_div = psd_fig.to_html(full_html=False)

        context = {
        'tetta_s': values,
        'soil_suction': values1,
        'a': a1,
        'n': n1,
        'm': m1,
        'soil_suction_r': soil_suction_r1,
        'optimal_a': round(optimal_a,2),
        'optimal_n': round(optimal_n,2),
        'optimal_m': round(optimal_m,2),
        'optimal_soil_suction_r': round(optimal_soil_suction_r,2),
        'error_sum': error_sum,
        'swcc_div': swcc_div,  # Pass the Soil-Water Characteristics Curve as HTML div
        'psd_div': psd_div,    # Pass the Pore-Size Distribution as HTML div
        'new_swcc_div':new_swcc_div,
        'swcc_div1':swcc_div1,
        }
        return render(request, 'myapp/input_values.html', context)
    else:
        return render(request, 'myapp/input_values.html')

def show_graph(request):
    return render(request, 'myapp/input_values.html')


