import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from skimage import data
from skimage import img_as_ubyte
from dash_canvas.utils import array_to_data_url

img=img_as_ubyte(data.binary_blobs(length=512, n_dim=3, seed=0))
img_slices = [array_to_data_url(img[i, :, :]) for i in range(img.shape[0])]
print(len(img_slices))

def make_figure(filename_uri, width, height):
    fig = go.Figure()
    # Add trace
    fig.add_trace(
        go.Scatter(x=[], y=[])
    )
    # Add images
    fig.add_layout_image(
        dict(
            source=filename_uri,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=width,
            sizey=height,
            sizing="contain",
            layer="below"
        )
    )
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, scaleanchor='x', range=(0, width),
    #showticklabels=False,
    zeroline=False)
    fig.update_yaxes(showgrid=False, scaleanchor='y', range=(height, 0),
    #showticklabels=False,
    zeroline=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

app = dash.Dash(__name__)

app.layout=html.Div([
    html.Img(id="image-display",src=img_slices[0]),
    dcc.Store(id="image-slices",data=img_slices),
    dcc.Slider(id="image-select",min=0,max=len(img_slices),step=1,updatemode="drag"),
    dcc.Slider(id="image-select-2",min=0,max=len(img_slices),step=1,updatemode="drag"),
    dcc.Graph(id="image-display-graph",figure=make_figure(img_slices[0],img[0].shape[1],img[0].shape[0]))
])

app.clientside_callback(
    """
    function(image_select_value,image_slices_data) {
        return image_slices_data[image_select_value];
    }
    """,
    Output("image-display","src"),
    [Input("image-select","value")],
    [State("image-slices","data")]
)

app.clientside_callback(
"""
function(image_select_value2,image_slices_data,image_display_figure) {
    		console.log(image_display_figure);
    		let image_display_figure_ = {...image_display_figure};
    		image_display_figure_.layout.images[0].source=image_slices_data[image_select_value2];
    		return image_display_figure_;
		}
"""
,
    Output("image-display-graph","figure"),
    [Input("image-select-2","value")],
    [State("image-slices","data"),
     State("image-display-graph","figure")]
)

if __name__ == '__main__':
    app.run_server(debug=True)
