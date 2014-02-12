#! python3

import sys
import webbrowser
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QLineEdit, \
    QGridLayout, QPushButton, QTreeWidget, QTableView, QWidget
from articlefinder.finder.finder import Finder
from articlefinder.qt.articlelist_model import ArticleListModel, PRICE, NAME
from articlefinder.shops.bike.bike24 import Bike24
from articlefinder.shops.bike.bike_discount import BikeDiscount
from articlefinder.shops.bike.cnc_bikes import CNCBikes
from articlefinder.shops.bike.mtb_news import MTBNews

__author__ = 'stefanlehmann'



class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.finder = Finder()
        self.finder.shops = [Bike24(), BikeDiscount(), CNCBikes(), MTBNews()]
        self.model = ArticleListModel()

        #Search label and LineEdit
        self.searchLabel = QLabel(self.tr("Search term:"))
        self.searchLineEdit = QLineEdit()
        self.searchLabel.setBuddy(self.searchLineEdit)
        self.searchLineEdit.returnPressed.connect(self.search)

        #Search Button
        self.searchButton = QPushButton(self.tr("Search"))

        #Results
        self.resultTable = QTableView()
        self.resultTable.setSortingEnabled(True)
        self.resultTable.setModel(self.model)
        self.resultTable.setMouseTracking(True)
        self.resultTable.clicked.connect(self.open_url)
        self.resultTable.mouseMoveEvent = self.resultTable_mouseMove

        #Layout
        self.setLayout(QGridLayout())
        self.layout().addWidget(self.searchLabel, 0, 0)
        self.layout().addWidget(self.searchLineEdit, 0, 1)
        self.layout().addWidget(self.searchButton, 0, 2)
        self.layout().addWidget(self.resultTable, 1, 0, 1, 3)

        self.resize(800, 600)
        self.searchButton.pressed.connect(self.search)

    def search(self):
        self.model.beginResetModel()
        search_term = self.searchLineEdit.text()
        self.model.articles = self.finder.find(search_term)
        self.model.endResetModel()

        self.resultTable.sortByColumn(PRICE, Qt.AscendingOrder)
        self.resultTable.resizeColumnsToContents()

    def open_url(self, event):
        index = self.resultTable.currentIndex()
        if index.isValid():
            if index.column() == NAME:
                article = self.model.articles[index.row()]
                webbrowser.open_new_tab(article.url)

    def resultTable_mouseMove(self, event):
        index = self.resultTable.indexAt(event.pos())
        if not index.isValid():
            self.resultTable.unsetCursor()

        if index.column() == NAME:
            self.resultTable.setCursor(Qt.PointingHandCursor)
        else:
            self.resultTable.unsetCursor()


if __name__=="__main__":
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load("mainwindow.qm")
    app.installTranslator(translator)
    w = MainWindow()
    w.show()
    app.exec_()