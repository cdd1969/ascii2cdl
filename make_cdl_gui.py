#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import os
import inspect

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "lib")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
from modify_cdl import make_cdl


class aaa(QtGui.QWidget):
    
    def __init__(self):
        self.parent = super(aaa, self)
        self.parent.__init__()
        
        self.initUI()
        
    def initUI(self):
        
        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        
        self.qle1 = QtGui.QLineEdit()
        self.qle2 = QtGui.QLineEdit()
        self.qle1.setDisabled(True)
        self.qle2.setDisabled(True)
        grid.addWidget(self.qle1, *(0, 0))
        grid.addWidget(self.qle2, *(1, 0))

        button1 = QtGui.QPushButton("open CDL")
        button2 = QtGui.QPushButton("open Meta")
        button3 = QtGui.QPushButton("Create New CDL")
        grid.addWidget(button1, *(0, 1))
        grid.addWidget(button2, *(1, 1))
        grid.addWidget(button3, *(3, 1))
        button1.clicked.connect(self.button1Clicked)
        button2.clicked.connect(self.button2Clicked)
        button3.clicked.connect(self.button3Clicked)

        self.cb = QtGui.QCheckBox('Show log in console', self)
        self.cb.toggle()
        grid.addWidget(self.cb, *(2, 1))
        
        self.lbl = QtGui.QLabel(' ')
        grid.addWidget(self.lbl, *(3, 0))


        self.move(300, 150)
        self.setWindowTitle('make_cdl_gui')
        self.show()
    

    def button1Clicked(self):
        self.CDLfileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", "", "CDL files (*.cdl)")
        self.qle1.setText(self.CDLfileName)
    
    
    def button2Clicked(self):
        self.METAfileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", "", "Meta file(*.*)")
        self.qle2.setText(self.METAfileName)

    def button3Clicked(self):
        log = self.cb.isChecked()
        if self.CDLfileName and self.METAfileName:
            self.lbl.setText("...Wait until MessageBox Appears...")
            Path, _ = os.path.split(os.path.abspath(sys.argv[0]))  # Path - is directory of the script itself
            newCdlName = os.path.join(Path, '_'+os.path.split(str(self.CDLfileName))[1])
            
            make_cdl(str(self.CDLfileName), metafname=str(self.METAfileName), log=log , outpath=Path)
            print '-'*50+'\nClick Ok button'
            QtGui.QMessageBox.about(self, "CDL file created successfully", QtCore.QString(newCdlName))
            QtCore.QCoreApplication.instance().quit()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = aaa()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
