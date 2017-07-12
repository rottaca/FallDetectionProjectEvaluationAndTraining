#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    QStringList args = QCoreApplication::arguments();
    if(args.size() == 2) {
        QString fileName = args.at(1);
    } else {
        exit(1);
    }


}

MainWindow::~MainWindow()
{
    delete ui;
}
