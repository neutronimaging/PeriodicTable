import numpy as np
import scipy.io
import os
import pandas as pd

import plotly.graph_objects as go
import plotly.offline as pyo
pyo.init_notebook_mode()
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = 'iframe'

import ipywidgets as widgets
from IPython.core.display import HTML
from IPython.display import display

from . import ATTENUATION_FILE


class InteractivePeriodicTable:

    # variable for display
    xoffset = 8

    x0 = 0.5 - xoffset
    y0 = 7.5
    x1 = 1.5 - xoffset
    y0 = 7.5
    y1 = 8.5

    vmin = 0
    vmax = 5

    def __init__(self):
        self.select_options()

    def _load_attenuation_coefficients_chemical_elements(self):
        self.df = pd.read_excel(ATTENUATION_FILE, sheet_name='data')

    def select_options(self):
        self._load_attenuation_coefficients_chemical_elements()

        self._modality = widgets.RadioButtons(options=['Neutrons', 'X-ray'])
        display(self._modality)

        _description = widgets.HTML("<b>Select what you want to see (CMD + click to add)")
        self._select = widgets.SelectMultiple(options=self.df.columns[1:],
                                         value=['Symbol'],
                                         rows=30,
                                         description='')
        vbox = widgets.VBox([_description, self._select])
        display(vbox)

    def _formating_table(self):
        self.data = []
        self.custom_data_name = ['x', 'y']

        self.list_metadata_to_display = list(self._select.value)
        self.modality_mode = self._modality.value

        self.list_metadata_to_display.insert(0, 'Name')

        for _index in np.arange(1, len(self.df)):
            _col = self.df.loc[_index]['Group']
            _row = self.df.loc[_index]['Period']

            x = (self.x0 + self.x1 + 2 * (_col - 1)) / 2
            y = (self.y0 + self.y1 - 2 * (_row - 1)) / 2

            _element_data = [x, y]

            if _index == 1:
                data_name = ['x', 'y']

            for _meta_name in self.list_metadata_to_display:
                _value = self.df.loc[_index][_meta_name]
                _element_data.append(_value)

                if _index == 1:
                    self.custom_data_name.append(_meta_name)

            self.data.append(_element_data)

        self.my_df = pd.DataFrame(self.data, columns=self.custom_data_name)

    def display_periodic_table(self):

        self._formating_table()

        fig1 = px.scatter(self.my_df,
                          x='x',
                          y='y',
                          hover_name='Name',
                          custom_data=self.custom_data_name)

        # build template
        template = "<b>%{customdata[2]}</b><br><br>"
        for _index, _data_name in enumerate(self.custom_data_name[3:]):
            template += "<b>" + _data_name + ': </b>%{customdata[' + str(_index + 3) + ']}<br>'

        fig1.update_traces(hovertemplate=template)

        # fill cells
        for _index in np.arange(1, len(self.df)):
            _col = self.df.loc[_index]['Group']
            _row = self.df.loc[_index]['Period']

            if self.modality_mode == 'Neutrons':
                _col_value = self.df.loc[_index]['Attenuation coef [1/cm] (Sears)']
            else:
                _col_value = self.df.loc[_index]['X-ray 150kV']

            if np.isnan(_col_value):
                _col_value = 0

            if _col_value == 0:
                _col_value_str = "-"
            else:
                _col_value_str = f"{_col_value:.2f}"
            _element_short_name = f"{self.df.loc[_index]['Symbol']} <br> {_col_value_str}"

            # _col_value = df.loc[_index]['Attenuation coef [1/cm] (Sears)']
            graylevel = 1 - (min(max(_col_value, self.vmin), self.vmax) - self.vmin) / (self.vmax - self.vmin)
            _color = np.array([255, 255, 255]) * graylevel
            _color = [int(x) for x in _color]
            _col_rgb = f"rgb({_color[0]}, {_color[1]}, {_color[2]}, 0.5)"

            if graylevel < 0.5:
                _font_color = "white"
            else:
                _font_color = "black"

            fig1.add_shape(
                type="rect",
                fillcolor=_col_rgb,
                x0 = self.x0 + (_col - 1),
                y0 = self.y0 - (_row - 1),
                x1 = self.x1 + (_col - 1),
                y1 = self.y1 - (_row - 1),
                label=dict(
                    texttemplate=_element_short_name,
                    font=dict(size=14,
                              color=_font_color),
                ),
            )

            # x_marker = (x0 + x1 + 2 * (_col - 1)) / 2
            # y_marker = (y0 + y1 - 2 * (_row - 1)) / 2

        fig1.update_traces(marker=dict(size=30))

        # top number
        _x = np.arange(-7, 12)
        _y = np.ones(len(_x)) * 10
        _text = [str(x) for x in np.arange(1, len(_x))]
        fig1.add_trace(go.Scatter(
            x=_x,
            y=_y,
            mode="text",
            text=_text,
            textposition="bottom center",
            textfont=dict(
                size=18,
            ),
            hoverinfo='skip',
        ))

        # left number
        _y = 8 - np.arange(8)
        _x = np.ones(len(_y)) * -9
        _text = [str(x) for x in np.arange(1, len(_x))]
        fig1.add_trace(go.Scatter(
            x=_x,
            y=_y,
            mode="text",
            text=_text,
            textposition="bottom center",
            textfont=dict(
                size=18,
            ),
            hoverinfo='skip',
        ))

        # fig1.update_xaxes(range=[0, 10])
        # fig1.update_yaxes(range=[0, 10])

        fig1.update_layout({
            # 'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'yaxis_scaleanchor': 'x',
        })

        fig1.update_xaxes({'visible': False})
        fig1.update_yaxes({'visible': False})
        fig1.update_layout(showlegend=False)
        fig1.update_layout(width=2200,
                           height=800,
                           autosize=False,
                           margin=dict(l=10, r=0, b=5,
                                       t=20, pad=10
                                       ), )

        fig1.add_annotation(dict(font=dict(color='black',
                                           size=18),
                                 x=0.25,
                                 y=0.14,
                                 showarrow=False,
                                 text='Lanthanides',
                                 textangle=0,
                                 xanchor='left',
                                 xref='paper',
                                 yref='paper'))

        fig1.add_annotation(dict(font=dict(color='black',
                                           size=18),
                                 x=0.25,
                                 y=0.06,
                                 showarrow=False,
                                 text='Actinides',
                                 textangle=0,
                                 xanchor='left',
                                 xref='paper',
                                 yref='paper'))

        fig1.show()

        self.fig = fig1

    def export(self):
        current_path = os.path.dirname(__file__)
        diagram_folder = os.path.dirname(os.path.dirname(current_path))
        self.fig.write_image(diagram_folder + "/diagrams/Interactive_Periodic_XrayAttenuations.svg")
        self.fig.write_image(diagram_folder + "/diagrams/Interactive_Periodic_XrayAttenuations.pdf")
        self.fig.write_image(diagram_folder + "/diagrams/Interactive_Periodic_XrayAttenuations.png")

        display(HTML(f"File exported in {diagram_folder}"))
        display(HTML("\t\t - Interactive_Periodic_XrayAttenuations.svg"))
        display(HTML("\t\t - Interactive_Periodic_XrayAttenuations.pdf"))
        display(HTML("\t\t - Interactive_Periodic_XrayAttenuations.png"))
