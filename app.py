# Import dependencies
import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly
import palmerpenguins
from shiny import reactive, render, req
import seaborn as sns
import pandas as pd
from faicons import icon_svg
from shinywidgets import render_plotly, render_widget
import palmerpenguins
from shinyswatch import theme

# Get the data
penguins_df = palmerpenguins.load_penguins()

# Define Shiny UI page
ui.page_opts(title="Customized Penguin Data - Breum", fillable=True)

theme.cyborg

# Define Shiny UI sidebar
with ui.sidebar(open="open"):  
    ui.HTML('<h3 style="font-size: medium;">Dashboard Configuration Options</h3>')
    with ui.accordion():
        with ui.accordion_panel("Attribute Selection"):
            ui.input_selectize("selected_attribute", "Select an attribute:", 
                          ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
        with ui.accordion_panel("Histogram Bins Configuration"):
            ui.input_numeric("plotly_bin_count", "# of Histogram Bins:", value=20, min=1, max=100)
        with ui.accordion_panel("Seaborn Bins Slider"):
            ui.input_slider("seaborn_bin_count", "# of Seaborn Bins:", min=1, max=50, value=10)
        with ui.accordion_panel("Species Filter"):
            ui.input_checkbox_group("selected_species_list", "Filter by Species:", 
                                choices=["Adelie", "Gentoo", "Chinstrap"], 
                                selected=["Adelie"], inline=True)
        with ui.accordion_panel("Island Filter"):
            ui.input_checkbox_group("selected_island_list", "Filter by Island:", 
                                choices=["Torgersen", "Biscoe", "Dream"], 
                                selected=["Torgersen", "Biscoe", "Dream"], inline=True)
        with ui.accordion_panel("Mass Filter"):
            ui.input_slider("mass_filter", "Mass (g)", 2000, 6000, 6000)
    
    ui.hr()
    @render.ui
    def selected_info2():
        selected_attribute = input.selected_attribute()
        plotly_bin_count = input.plotly_bin_count()
        seaborn_bin_count = input.seaborn_bin_count()
        selected_species = input.selected_species_list()
        selected_species_str = ", ".join(selected_species)
        selected_island = input.selected_island_list()
        selected_island_str = ", ".join(selected_island)
        mass_filter = input.mass_filter()
    
    ui.hr()
    ui.h6(class_="text-white")
    ui.span("Links:", class_="text-white")
    ui.a(
        "GitHub",
        href="https://github.com/kcbreum/cintel-06-custom",
        target="_blank",
        class_="text-white"
    )

# Define Shiny UI main page
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("igloo"),
        style="background-color: lightblue", 
        ):
        "Penguin Count"
        @render.text
        def display_penguin_count():
            df = filtered_data()
            return f"{len(df)} penguins"


with ui.accordion(id="acc", open="closed"):
    with ui.accordion_panel("Data Table"):
        @render.data_frame
        def penguin_datatable():
            return render.DataTable(penguins_df)

    with ui.accordion_panel("Data Grid"):
        @render.data_frame
        def penguin_datagrid():
            return render.DataGrid(penguins_df)

with ui.navset_card_tab(id="tab"):
    with ui.nav_panel("Plotly Histogram"):

        @render_plotly
        def plotly_histogram():
            plotly_hist = px.histogram(
                data_frame=penguins_df,
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count(),
                color="species",
            ).update_layout(
                title="Plotly Penguins Data",
                xaxis_title="Selected Attribute",
                yaxis_title="Count",
            )
            return plotly_hist
    
    with ui.nav_panel("Seaborn Histogram"):
        @render.plot
        def seaborn_histogram():
            histplot = sns.histplot(data=penguins_df, x="body_mass_g", bins=input.seaborn_bin_count())
            histplot.set_title("Palmer Penguins")
            histplot.set_xlabel("Mass")
            histplot.set_ylabel("Count")
            return histplot

with ui.card(full_screen=True):
    ui.card_header("Plotly Scatterplot: Species")

    @render_plotly
    def plotly_scatterplot():
        return px.scatter(penguins_df,
            title="Penguin Species",
            x="flipper_length_mm",
            y="body_mass_g",
            color="species",
            size_max=8,
            labels={"flipper_length_mm": "Flipper Length (mm)", "body_mass_g": "Body Mass (g)"})

# Define reactive calc
@reactive.calc
def filtered_data():
    return penguins_df[
        (penguins_df["species"].isin(input.selected_species_list())) &
        (penguins_df["island"].isin(input.selected_island_list()))]
