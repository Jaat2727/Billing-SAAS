# src/utils/plot_canvas.py
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

    def plot_bar(self, x, y, title, xlabel, ylabel):
        self.axes.cla()
        self.axes.bar(x, y)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.draw()

    def plot_pie(self, sizes, labels, title):
        self.axes.cla()
        self.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.axes.axis('equal')
        self.axes.set_title(title)
        self.draw()
