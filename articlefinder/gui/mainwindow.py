#! python3

import os
import sys
import webbrowser

from PyQt5.Qt import Qt
from PyQt5.QtCore import QTranslator, QCoreApplication, \
    QSettings
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QProgressDialog, \
    QMainWindow

from articlefinder.gui.articlelist import ArticleListModel, PRICE, NAME
from articlefinder.gui.centralwidget import CentralWidget
from articlefinder.gui.shoplist import ShoplistDockWidget
from articlefinder.gui.workerthread import WorkerThread
from articlefinder.shops.bike.bike24 import Bike24
from articlefinder.shops.bike.bike_discount import BikeDiscount
from articlefinder.shops.bike.cnc_bikes import CNCBikes
from articlefinder.shops.bike.mtb_news import MTBNews


WINDOW_STATE_SETTING = "WindowState"
WINDOW_GEOMETRY_SETTING = "WindowGeometry"
HORIZONTAL_HEADER_SETTING = "HorizontalHeader"
VERTICAL_HEADER_SETTING = "VerticalHeader"


class MainWindow(QMainWindow):
    def __init__(self, shops, parent=None):
        super().__init__(parent)

        # Worker Thread for Download
        self.worker = WorkerThread()
        self.worker.finished.connect(self.search_finished)
        self.worker.progress.connect(self.progress)

        # Progress Dialog
        self.progressDlg = None

        # Central Widget with Result Table
        self.model = ArticleListModel()
        self.setCentralWidget(CentralWidget())
        self.table = self.centralWidget().resultTable
        self.table.setModel(self.model)
        self.model.table = self.centralWidget().resultTable

        # Signals
        self.centralWidget().searchLineEdit.returnPressed.connect(self.search)
        self.centralWidget().resultTable.clicked.connect(self.open_url)
        self.centralWidget().searchButton.pressed.connect(self.search)
        self.centralWidget().resultTable.mouseMoveEvent = self.resultTable_mouseMove

        # Supplier list
        self.suppliers = shops
        self.shoplistDockWidget = ShoplistDockWidget()
        self.shoplistWidget = self.shoplistDockWidget.widget()
        # self.shoplistWidget.itemChanged.connect(self.filter_checked_suppliers)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.shoplistDockWidget)
        self.fill_supplier_list()

        self._init_menus()
        self.load_settings()

    def _init_menus(self):
        self.viewMenu = self.menuBar().addMenu(self.tr('View'))
        self.viewMenu.addAction(self.shoplistDockWidget.toggleViewAction())

    def closeEvent(self, event):
        self.save_settings()
        QMainWindow.closeEvent(self, event)

    def fill_supplier_list(self):
        self.shoplistWidget.clear()
        for s in self.suppliers:
            item = QListWidgetItem(s.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, s)
            self.shoplistWidget.addItem(item)

    def filter_checked_suppliers(self):
        for row in range(self.shoplistWidget.count()):
            item = self.shoplistWidget.item(row)
            shop = item.data(Qt.UserRole)
            for a in self.model.articles:
                if a.shop.name == shop.name:
                    a.visible = item.checkState()
        self.model.refresh()

    def load_settings(self):
        try:
            self.restoreState(QSettings().value(WINDOW_STATE_SETTING))
            self.restoreGeometry(QSettings().value(WINDOW_GEOMETRY_SETTING))
            self.table.horizontalHeader().restoreState(
                QSettings().value(HORIZONTAL_HEADER_SETTING)
            )
            self.table.verticalHeader().restoreState(
                QSettings().value(VERTICAL_HEADER_SETTING)
            )
        except (AttributeError, TypeError):
            self.resize(600, 800)

    def open_url(self, event):
        index = self.centralWidget().resultTable.currentIndex()
        if index.isValid():
            if index.column() == NAME:
                article = self.model.visible_articles[index.row()]
                webbrowser.open_new_tab(article.url)

    def progress(self, i, max, shopname):
        self.progressDlg.setMaximum(max)
        self.progressDlg.setLabelText(shopname)
        self.progressDlg.setValue(i)

    def resultTable_mouseMove(self, event):
        index = self.centralWidget().resultTable.indexAt(event.pos())
        if not index.isValid():
            self.centralWidget().resultTable.unsetCursor()

        if index.column() == NAME:
            self.centralWidget().resultTable.setCursor(Qt.PointingHandCursor)
        else:
            self.centralWidget().resultTable.unsetCursor()

    def save_settings(self):
        QSettings().setValue(WINDOW_STATE_SETTING, self.saveState())
        QSettings().setValue(WINDOW_GEOMETRY_SETTING, self.saveGeometry())
        QSettings().setValue(
            HORIZONTAL_HEADER_SETTING,
            self.table.horizontalHeader().saveState()
        )
        QSettings().setValue(
            VERTICAL_HEADER_SETTING,
            self.table.verticalHeader().saveState()
        )

    def search(self):
        def _get_suppliers():
            for row in range(self.shoplistWidget.count()):
                item = self.shoplistWidget.item(row)
                if item.checkState() == Qt.Checked:
                    yield item.data(Qt.UserRole)

        self.worker.shops = list(_get_suppliers())
        self.worker.search_term = self.centralWidget().searchLineEdit.text()
        self.progressDlg = QProgressDialog(self)
        self.progressDlg.canceled.connect(self.worker.quit)
        self.progressDlg.setMinimum(0)
        self.progressDlg.setMaximum(len(self.worker.shops))
        self.progressDlg.setModal(True)
        self.progressDlg.show()
        self.worker.start()

    def search_finished(self):
        self.progressDlg.close()

        self.model.beginResetModel()
        self.model.articles = self.worker.articles
        self.filter_checked_suppliers()
        self.model.refresh()
        self.model.endResetModel()

        self.centralWidget().resultTable.sortByColumn(PRICE, Qt.AscendingOrder)

    def suppliers_changed(self):
        for row in range(self.shoplistWidget.count()):
            item = self.shoplistWidget.item(row)
            shop = item.data(Qt.UserRole)
            for a in self.model.articles:
                if a.shopname == shop.name:
                    a.visible = item.checkState()
        self.model.refresh()


def run(shops=[Bike24(), BikeDiscount(), CNCBikes(), MTBNews()],
        title="Articlefinder"):

    app = QApplication(sys.argv)
    QCoreApplication.setApplicationName(title)
    QCoreApplication.setApplicationVersion("1.0.1")
    QCoreApplication.setOrganizationName("Stefan Lehmann")
    translator = QTranslator()
    tf = os.path.join(os.path.dirname(__file__), "articlefinder_de.qm")
    translator.load(tf)
    app.installTranslator(translator)
    w = MainWindow(shops)
    w.setWindowTitle(title)
    w.show()
    app.exec_()


if __name__ == "__main__":
    run()
